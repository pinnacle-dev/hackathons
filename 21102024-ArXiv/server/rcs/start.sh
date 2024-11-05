cd 21102024-ArXiv/server
export $(grep -v '^#' .env | xargs)
source venv/bin/activate
cd rcs
python3 rcs_server.py
