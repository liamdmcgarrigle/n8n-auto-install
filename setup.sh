#!/bin/bash

# Activate the virtual environment
source n8n-auto-install/n8n_venv/bin/activate

# Install requirements
n8n-auto-install/n8n_venv/bin/pip install -r n8n-auto-install/requirements.txt -q

# Run the Python script
python3 n8n-auto-install/main.py