# Send RCS Flow
This flow provides options to:
1) Check if a number is RCS-enabled.
2) Sends a message to a provided RCS-enabled number. Choose from a few pre-defined messages.

## Quickstart
1) Install the pacakges from `requirements.txt`:
```bash
pip install -r requirements.txt
```
2) Update the `.env` file with your `PINNACLE_API_KEY`
3) Update your webhook at https://dashboard.trypinnacle.app/settings/testing.
4) Run your flow:
```bash
python flow.py
```