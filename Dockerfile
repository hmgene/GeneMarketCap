# Use miniconda3 image as base
FROM continuumio/miniconda3:latest
WORKDIR /app
COPY env.yml .
RUN conda env create -f env.yml
SHELL ["conda", "run", "-n", "pubmed_env", "/bin/bash", "-c"]
COPY scripts/ ./scripts
COPY data/ ./data
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "pubmed_env", "python", "scripts/dn.py"]


