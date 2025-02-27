#!/bin/bash

# Create project directory structure
mkdir -p sports_scraper/{api,frontend,scraper,static/{css,js},templates}

# Create virtual environment
python3 -m venv sports_scraper/venv

# Activate virtual environment
source sports_scraper/venv/bin/activate

# Install required packages
pip install selenium webdriver-manager flask flask-cors pandas requests

# Install frontend development tools (if using React)
# Uncomment if you want to use React
 brew install node
 npm init -y
 npm install react react-dom

# Create a requirements.txt file
cat > sports_scraper/requirements.txt << EOF
selenium==4.14.0
webdriver-manager==4.0.1
flask==2.3.3
flask-cors==4.0.0
pandas==2.1.1
requests==2.31.0
EOF

echo "Project setup complete. Activate the virtual environment with:"
echo "source sports_scraper/venv/bin/activate"