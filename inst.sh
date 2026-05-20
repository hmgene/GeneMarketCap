
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt


ollama pull nomic-embed-text
ollama pull qwen3:14b


sudo ufw delete allow 8000/tcp
sudo ufw delete allow 8000
sudo ufw delete deny 8000

sudo ufw allow 22/tcp
sudo ufw allow 8888/tcp
