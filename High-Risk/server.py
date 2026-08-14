import os, gspread, urllib3
from collections import defaultdict
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS
from google.oauth2.service_account import Credentials

# SSL bypass only needed on Shopee corporate network
if os.environ.get('CORPORATE_PROXY'):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    os.environ['PYTHONHTTPSVERIFY'] = '0'
    import requests
    _orig_send = requests.Session.send
    def _no_verify_send(self, *args, **kwargs):
        kwargs['verify'] = False
        return _orig_send(self, *args, **kwargs)
    requests.Session.send = _no_verify_send

app = Flask(__name__)
CORS(app)

BASE      = os.path.dirname(os.path.abspath(__file__))
CREDS     = os.path.join(BASE, 'google_credentials.json')
SHEET_ID  = '1JyDsRwD4llPZn46-r-e1pYlb1FRRrPaAcuhFFBO5npU'
HIGH_RISK = {'A3', 'A4', 'B1', 'B2'}
SCOPES    = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def get_credentials():
    # Cloud: read from env var; local: read from file
    import json as _json
    raw = os.environ.get('GOOGLE_CREDENTIALS_JSON')
    if raw:
        info = _json.loads(raw)
        return Credentials.from_service_account_info(info, scopes=SCOPES)
    return Credentials.from_service_account_file(CREDS, scopes=SCOPES)

def parse_date(raw):
    for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S'):
        try:
            return datetime.strptime(str(raw).split(' ')[0], fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return None

def fetch_data():
    creds = get_credentials()
    gc    = gspread.authorize(creds)
    sh    = gc.open_by_key(SHEET_ID)

    # Mail Picker → allowed map
    mp_rows = sh.worksheet('Mail Picker').get_all_values()
    allowed = {}
    for row in mp_rows[1:]:
        if len(row) >= 3 and row[1].strip():
            allowed[row[1].strip().lower()] = {'id': row[0].strip(), 'name': row[2].strip()}

    # Data sheet → group by (date, email), merge zones
    data_rows = sh.worksheet('data').get_all_values()
    day_email = defaultdict(lambda: defaultdict(set))
    for row in data_rows[1:]:
        if len(row) < 4:
            continue
        picked_date, _, email, zone = row[0], row[1], row[2].strip(), row[3].strip()
        if not email or zone not in HIGH_RISK:
            continue
        ds = parse_date(picked_date)
        if not ds:
            continue
        day_email[ds][email].add(zone)

    logs = {}
    for ds in sorted(day_email):
        entries = []
        for email, zones in day_email[ds].items():
            m  = allowed.get(email.lower(), {})
            ok = bool(m)
            entries.append({'email': email, 'zones': sorted(zones),
                            'ok': ok, 'id': m.get('id',''), 'name': m.get('name','')})
        entries.sort(key=lambda x: (not x['ok'], x['email']))
        logs[ds] = entries

    return {'logs': logs, 'allowed': allowed}

@app.route('/data')
def data():
    try:
        return jsonify(fetch_data())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return 'High Risk Zone API — running OK'

if __name__ == '__main__':
    print('Server running at http://localhost:8080')
    app.run(port=8080, debug=False)
