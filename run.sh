
if python -c "import sys; exit(0 if sys.prefix != sys.base_prefix else 1)"; then
    echo "venv is ACTIVE"
else
    source venv/bin/activate
fi
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

