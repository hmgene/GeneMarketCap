# Use miniconda3 image as base
FROM continuumio/miniconda3:latest

# Set working directory
WORKDIR /app

# Copy environment.yml and install dependencies
COPY env.yml .
RUN conda env create -f env.yml

# Activate the environment
SHELL ["conda", "run", "-n", "pubmed_env", "/bin/bash", "-c"]

# Copy scripts and data
COPY scripts/ ./scripts
COPY data/ ./data

# Set the entrypoint to the Python script
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "pubmed_env", "python", "scripts/dn.py"]

