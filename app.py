from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from supabase import create_client, Client
import os
import requests
from functools import wraps

app = Flask(__name__, template_folder='.')
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True
app.secret_key = os.environ.get('SECRET_KEY', 'autodms-secret-key-change-in-prod')
CORS(app)

# Supabase
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://owuvfxarzktcmrueculg.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', 'sb_publishable_YoeY5zssfd_KBDQgktrM9w_tE4drnYC')
sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Ziptax
ZIPTAX_KEY = os.environ.get('ZIPTAX_KEY', 'ziptax_sk_x2FuBXtlB04LsRxJ8rylLgm5V1MpP7')

# Google Maps
GOOGLE_KEY = os.environ.get('GOOGLE_KEY', 'AIzaSyCBvsj_8zry1RbXDSQaQw0uXKzcZmlveQI')

# ── Auth ──────────────────────────────────────────────────────────────────────

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

# ── Inventory ─────────────────────────────────────────────────────────────────

@app.route('/api/inventory', methods=['GET'])
@login_required
def get_inventory():
    try:
        res = sb.table('inventory').select('*').order('created_at', desc=True).execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory', methods=['POST'])
@login_required
def add_vehicle():
    data = request.json
    try:
        res = sb.table('inventory').insert(data).execute()
        return jsonify(res.data[0])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/<int:vehicle_id>', methods=['PUT'])
@login_required
def update_vehicle(vehicle_id):
    data = request.json
    try:
        res = sb.table('inventory').update(data).eq('id', vehicle_id).execute()
        return jsonify(res.data[0])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/<int:vehicle_id>', methods=['DELETE'])
@login_required
def delete_vehicle(vehicle_id):
    try:
        sb.table('inventory').delete().eq('id', vehicle_id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── Deals ─────────────────────────────────────────────────────────────────────

@app.route('/api/deals', methods=['GET'])
@login_required
def get_deals():
    try:
        res = sb.table('deals').select('*').order('created_at', desc=True).execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/deals', methods=['POST'])
@login_required
def save_deal():
    data = request.json
    try:
        # Upsert by deal_num
        res = sb.table('deals').upsert(data, on_conflict='deal_num').execute()
        return jsonify(res.data[0])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/deals/<deal_num>', methods=['PUT'])
@login_required
def update_deal(deal_num):
    data = request.json
    try:
        res = sb.table('deals').update(data).eq('deal_num', deal_num).execute()
        return jsonify(res.data[0])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/deals/<deal_num>', methods=['DELETE'])
@login_required
def delete_deal(deal_num):
    try:
        sb.table('deals').delete().eq('deal_num', deal_num).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── Repair Orders ─────────────────────────────────────────────────────────────

@app.route('/api/repair-orders', methods=['GET'])
@login_required
def get_ros():
    try:
        res = sb.table('repair_orders').select('*').order('created_at', desc=True).execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/repair-orders', methods=['POST'])
@login_required
def save_ro():
    data = request.json
    try:
        res = sb.table('repair_orders').upsert(data, on_conflict='ro_num').execute()
        return jsonify(res.data[0])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── Users ─────────────────────────────────────────────────────────────────────

@app.route('/api/users', methods=['GET'])
@login_required
def get_users():
    try:
        res = sb.table('users').select('id,first,last,username,role,active').execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['POST'])
@login_required
def save_user():
    data = request.json
    try:
        if data.get('id'):
            res = sb.table('users').update(data).eq('id', data['id']).execute()
        else:
            res = sb.table('users').insert(data).execute()
        return jsonify(res.data[0])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── Tax Lookup (Ziptax proxy) ─────────────────────────────────────────────────

@app.route('/api/tax-lookup')
@login_required
def tax_lookup():
    address = request.args.get('address', '')
    if not address:
        return jsonify({'error': 'No address provided'}), 400
    try:
        res = requests.get(
            f'https://api.zip-tax.com/request/v60?address={address}',
            headers={'X-API-KEY': ZIPTAX_KEY},
            timeout=5
        )
        return jsonify(res.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── VIN Decoder ───────────────────────────────────────────────────────────────

@app.route('/api/vin/<vin>')
@login_required
def decode_vin(vin):
    try:
        res = requests.get(
            f'https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{vin}?format=json',
            timeout=5
        )
        return jsonify(res.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── Frontend ──────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html', google_key=GOOGLE_KEY)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
