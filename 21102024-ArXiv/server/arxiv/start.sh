cd 21102024-ArXiv/server
export $(grep -v '^#' .env | xargs)
source venv/bin/activate
cd arxiv
python3 arxiv.py
