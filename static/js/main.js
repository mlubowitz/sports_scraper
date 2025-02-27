// Main JavaScript for Sports Betting Scraper

document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const leaguesContainer = document.getElementById('leagues-container');
    const statisticsContainer = document.getElementById('statistics-container');
    const scraperForm = document.getElementById('scraper-form');
    const statusContainer = document.getElementById('status-container');
    const resultsContainer = document.getElementById('results-container');
    const dataModal = new bootstrap.Modal(document.getElementById('dataModal'));
    const resultsTable = document.getElementById('results-table').querySelector('tbody');
    const downloadLink = document.getElementById('download-link');
    
    // Active jobs tracking
    const activeJobs = {};
    
    // Initialize by loading leagues and statistics
    initializeApp();
    
    function initializeApp() {
        // Fetch leagues
        fetch('/api/leagues')
            .then(response => response.json())
            .then(data => {
                renderLeagues(data.leagues);
            })
            .catch(error => console.error('Error fetching leagues:', error));
        
        // Fetch statistics
        fetch('/api/statistics')
            .then(response => response.json())
            .then(data => {
                renderStatistics(data.statistics);
            })
            .catch(error => console.error('Error fetching statistics:', error));
        
        // Check for any existing jobs
        fetch('/api/jobs')
            .then(response => response.json())
            .then(data => {
                const jobs = data.jobs || {};
                Object.entries(jobs).forEach(([jobId, jobData]) => {
                    activeJobs[jobId] = jobData;
                    updateJobStatus(jobId, jobData);
                });
                updateStatusContainer();
            })
            .catch(error => console.error('Error fetching jobs:', error));
    }
    
    function renderLeagues(leagues) {
        leaguesContainer.innerHTML = '';
        leagues.forEach(league => {
            const checkbox = document.createElement('div');
            checkbox.className = 'checkbox-item form-check';
            checkbox.innerHTML = `
                <input class="form-check-input" type="checkbox" id="league-${league}" name="leagues" value="${league}">
                <label class="form-check-label" for="league-${league}">${league}</label>
            `;
            leaguesContainer.appendChild(checkbox);
        });
    }
    
    function renderStatistics(statistics) {
        statisticsContainer.innerHTML = '';
        statistics.forEach((statistic, index) => {
            const radio = document.createElement('div');
            radio.className = 'radio-item form-check';
            radio.innerHTML = `
                <input class="form-check-input" type="radio" id="stat-${statistic}" name="statistic" value="${statistic}" ${index === 0 ? 'checked' : ''}>
                <label class="form-check-label" for="stat-${statistic}">${statistic}</label>
            `;
            statisticsContainer.appendChild(radio);
        });
    }
    
    function updateStatusContainer() {
        if (Object.keys(activeJobs).length === 0) {
            statusContainer.innerHTML = '<p>No active jobs.</p>';
            return;
        }
        
        statusContainer.innerHTML = '';
        Object.entries(activeJobs).forEach(([jobId, job]) => {
            const statusClass = getStatusClass(job.status);
            const statusItem = document.createElement('div');
            statusItem.className = `status-item ${statusClass}`;
            statusItem.innerHTML = `
                <p><strong>Job ID:</strong> ${jobId}</p>
                <p><strong>Leagues:</strong> ${job.leagues.join(', ')}</p>
                <p><strong>Statistic:</strong> ${job.statistic}</p>
                <p><strong>Status:</strong> ${job.status}</p>
                ${job.output_file ? `
                    <button class="btn btn-sm btn-primary results-button" data-job-id="${jobId}" data-file="${job.output_file}">View Results</button>
                    <a href="/api/download/${job.output_file}" class="btn btn-sm btn-success" download>Download CSV</a>
                ` : ''}
                ${job.error ? `<p class="text-danger"><strong>Error:</strong> ${job.error}</p>` : ''}
            `;
            statusContainer.appendChild(statusItem);
        });
        
        // Add event listeners for result buttons
        document.querySelectorAll('.results-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const jobId = e.target.getAttribute('data-job-id');
                const filename = e.target.getAttribute('data-file');
                viewResults(filename);
            });
        });
    }
    
    function getStatusClass(status) {
        switch (status) {
            case 'starting':
            case 'running':
                return 'status-running';
            case 'completed':
                return 'status-completed';
            case 'failed':
                return 'status-failed';
            default:
                return '';
        }
    }
    
    function updateJobStatus(jobId, data) {
        activeJobs[jobId] = data;
        
        // If job is still running, poll for updates
        if (data.status === 'starting' || data.status === 'running') {
            setTimeout(() => {
                pollJobStatus(jobId);
            }, 5000);
        }
        
        updateStatusContainer();
    }
    
    function pollJobStatus(jobId) {
        fetch(`/api/job/${jobId}`)
            .then(response => response.json())
            .then(data => {
                updateJobStatus(jobId, data);
            })
            .catch(error => {
                console.error(`Error polling job ${jobId}:`, error);
            });
    }
    
    function viewResults(filename) {
        // Clear the table
        resultsTable.innerHTML = '';
        
        // Set the download link
        downloadLink.href = `/api/download/${filename}`;
        
        // Fetch and display the data
        fetch(`/api/data/${filename}`)
            .then(response => response.json())
            .then(result => {
                const data = result.data || [];
                
                if (data.length === 0) {
                    resultsTable.innerHTML = '<tr><td colspan="6">No data available</td></tr>';
                    return;
                }
                
                data.forEach(row => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${row.game}</td>
                        <td>${row.player}</td>
                        <td>${row.team}</td>
                        <td>${row.statistic}</td>
                        <td>${row.value}</td>
                        <td>${row.odds}</td>
                    `;
                    resultsTable.appendChild(tr);
                });
                
                // Show the modal
                dataModal.show();
            })
            .catch(error => {
                console.error('Error fetching results:', error);
                resultsTable.innerHTML = '<tr><td colspan="6">Error loading data</td></tr>';
                dataModal.show();
            });
    }
    
    // Form submission handler
    scraperForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // Get selected leagues
        const selectedLeagues = Array.from(
            document.querySelectorAll('input[name="leagues"]:checked')
        ).map(input => input.value);
        
        // Get selected statistic
        const selectedStatistic = document.querySelector('input[name="statistic"]:checked')?.value;
        
        // Validate selection
        if (selectedLeagues.length === 0) {
            alert('Please select at least one league');
            return;
        }
        
        if (!selectedStatistic) {
            alert('Please select a statistic');
            return;
        }
        
        // Disable form while job is starting
        const scrapeButton = document.getElementById('scrape-button');
        scrapeButton.disabled = true;
        scrapeButton.textContent = 'Starting...';
        
        // Send request to start scraping
        fetch('/api/scrape', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                leagues: selectedLeagues,
                statistic: selectedStatistic
            }),
        })
        .then(response => response.json())
        .then(data => {
            // Re-enable form
            scrapeButton.disabled = false;
            scrapeButton.textContent = 'Start Scraping';
            
            // Check for error
            if (data.error) {
                alert(`Error: ${data.error}`);
                return;
            }
            
            // Add job to active jobs
            const jobId = data.job_id;
            activeJobs[jobId] = {
                leagues: selectedLeagues,
                statistic: selectedStatistic,
                status: 'starting',
                output_file: null
            };
            
            // Update UI
            updateStatusContainer();
            
            // Start polling for job status
            pollJobStatus(jobId);
        })
        .catch(error => {
            console.error('Error starting scrape:', error);
            scrapeButton.disabled = false;
            scrapeButton.textContent = 'Start Scraping';
            alert('An error occurred while starting the scrape');
        });
    });
});