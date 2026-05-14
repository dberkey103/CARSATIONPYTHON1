from flask import Flask, request, jsonify, session, Response
from flask_cors import CORS
from supabase import create_client, Client
import os
import requests
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'autodms-secret-key-change-in-prod')
CORS(app)

SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://owuvfxarzktcmrueculg.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im93dXZmeGFyemt0Y21ydWVjdWxnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODY2MjU0OSwiZXhwIjoyMDk0MjM4NTQ5fQ.C9slu-9TawNuRWZDQgBObG3Dd7nSuT_zaFUbReE70Oc')
sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

ZIPTAX_KEY = os.environ.get('ZIPTAX_KEY', 'ziptax_sk_x2FuBXtlB04LsRxJ8rylLgm5V1MpP7')
CARSXE_KEY = os.environ.get('CARSXE_KEY', 'mic8bjexk_upjyimztj_vioyxn1xd')
GOOGLE_KEY = os.environ.get('GOOGLE_KEY', 'AIzaSyCBvsj_8zry1RbXDSQaQw0uXKzcZmlveQI')

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    try:
        res = sb.table('users').select('*').eq('username', username).eq('password', password).eq('active', True).execute()
        if res.data:
            user = res.data[0]
            session['user'] = user
            return jsonify({'success': True, 'user': user})
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'success': True})

@app.route('/api/me')
def me():
    if 'user' in session:
        return jsonify(session['user'])
    return jsonify({'error': 'Not logged in'}), 401

@app.route('/api/inventory', methods=['GET'])
@login_required
def get_inventory():
    try:
        res = sb.table('inventory').select('*').order('created_at', desc=True).execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.ro
