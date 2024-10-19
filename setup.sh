#!/usr/bin/env bash

# Enable Vertex AI and BigQuery (if not already enabled)
gcloud services enable aiplatform.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable bigquerydatatransfer.googleapis.com

# Install Miniforge (to create an isolated Python environment)
export PYTHON_PREFIX=~/miniforge
curl -Lo ~/miniforge.sh https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
bash ~/miniforge.sh -fbp ${PYTHON_PREFIX}
rm -rf ~/miniforge.sh

# Activate the Python environment and install packages
${PYTHON_PREFIX}/bin/conda init bash
source ~/.bashrc
conda activate base

# Install required Python packages from the requirements file
${PYTHON_PREFIX}/bin/pip install -r requirements.txt

# Run the Streamlit app
${PYTHON_PREFIX}/bin/streamlit run app.py --server.enableCORS=false --server.enableXsrfProtection=false --server.port 8080
