import os
import sys
import json
import pandas as pd
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import threading

# Add parent directory to path to import from scraper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper.scraper import SportsScraper
from scraper.config import AVAILABLE_LEAGUES, AVAILABLE_STATISTICS

app = Flask(__name__, 
            static_folder='../static',
            template_folder='../templates')
CORS(app)  # Enable Cross-Origin Resource Sharing

# Keep track of running jobs
active_jobs = {}
job_lock = threading.Lock()
job_counter = 0

# Create data directory if it doesn't exist
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/leagues', methods=['GET'])
def get_leagues():
    """Get available leagues"""
    return jsonify({"leagues": AVAILABLE_LEAGUES})

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get available statistics"""
    return jsonify({"statistics": AVAILABLE_STATISTICS})

@app.route('/api/scrape', methods=['POST'])
def start_scrape():
    """Start a scraping job"""
    global job_counter
    
    data = request.get_json()
    leagues = data.get('leagues', [])
    statistic = data.get('statistic', '')
    
    # Validate input
    if not leagues:
        return jsonify({"error": "No leagues selected"}), 400
    
    if not statistic:
        return jsonify({"error": "No statistic selected"}), 400
    
    # Check if leagues and statistic are valid
    invalid_leagues = [league for league in leagues if league not in AVAILABLE_LEAGUES]
    if invalid_leagues:
        return jsonify({"error": f"Invalid leagues: {', '.join(invalid_leagues)}"}), 400
    
    if statistic not in AVAILABLE_STATISTICS:
        return jsonify({"error": f"Invalid statistic: {statistic}"}), 400
    
    # Create a job ID
    with job_lock:
        job_id = job_counter
        job_counter += 1
        active_jobs[job_id] = {
            "leagues": leagues,
            "statistic": statistic,
            "status": "starting",
            "output_file": None
        }
    
    # Start the scraper in a separate thread
    thread = threading.Thread(target=run_scraper_job, args=(job_id, leagues, statistic))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "job_id": job_id,
        "status": "started",
        "message": f"Started scraping {statistic} for {', '.join(leagues)}"
    })

def run_scraper_job(job_id, leagues, statistic):
    """Run the scraper job in a separate thread"""
    try:
        # Update job status
        with job_lock:
            active_jobs[job_id]["status"] = "running"
        
        # Create scraper and run the job
        scraper = SportsScraper(output_dir=data_dir)
        output_file = scraper.scrape_data(leagues, statistic)
        
        # Update job status
        with job_lock:
            active_jobs[job_id]["status"] = "completed"
            active_jobs[job_id]["output_file"] = os.path.basename(output_file)
    
    except Exception as e:
        # Update job status on error
        with job_lock:
            active_jobs[job_id]["status"] = "failed"
            active_jobs[job_id]["error"] = str(e)

@app.route('/api/job/<int:job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get the status of a job"""
    if job_id not in active_jobs:
        return jsonify({"error": "Job not found"}), 404
    
    return jsonify(active_jobs[job_id])

@app.route('/api/data/<filename>', methods=['GET'])
def get_data(filename):
    """Get data from a completed job"""
    try:
        file_path = os.path.join(data_dir, filename)
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404
        
        # Read CSV file
        df = pd.read_csv(file_path)
        
        # Convert to dictionary format
        data = df.to_dict(orient='records')
        
        return jsonify({"data": data})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download the CSV file"""
    return send_from_directory(data_dir, filename, as_attachment=True)

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    """Get all jobs"""
    return jsonify({"jobs": active_jobs})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)