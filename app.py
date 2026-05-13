from flask import Flask, request, jsonify, render_template, session, Response
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
CARSXE_KEY = os.environ.get('CARSXE_KEY', 'mic8bjexk_upjyimztj_vioyxn1xd')

# Google Maps
GOOGLE_KEY = os.environ.get('GOOGLE_KEY', 'AIzaSyCBvsj_8zry1RbXDSQaQw0uXKzcZmlveQI')

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorat
