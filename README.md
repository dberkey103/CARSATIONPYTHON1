# AutoDMS - Python Backend

## Local Development

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the app:
   ```
   python app.py
   ```

3. Open http://localhost:5000

## Supabase Setup

Run `supabase_users.sql` in your Supabase SQL Editor to create the users table.

## Deploy to Render

1. Go to render.com and sign up
2. Click "New Web Service"
3. Connect your GitHub repo or upload files
4. Set environment variables:
   - SUPABASE_URL = https://owuvfxarzktcmrueculg.supabase.co
   - SUPABASE_KEY = your_key
   - ZIPTAX_KEY = your_key
   - GOOGLE_KEY = your_key
   - SECRET_KEY = any_random_string

## Login Credentials
- admin / admin123
- sales / sales123  
- finance / finance123
