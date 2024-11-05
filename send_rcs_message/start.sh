cd send_rcs_message
export $(grep -v '^#' .env | xargs)
source venv/bin/activate
python3 flow.py
