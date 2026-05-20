#!/bin/bash

export OLLAMA_KEEP_ALIVE=24h
export OMP_NUM_THREADS=4

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
