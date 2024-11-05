cd rocket
export $(grep -v '^#' .env | xargs)
source venv/bin/activate
python3 flow.py
