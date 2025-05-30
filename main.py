import psycopg2
import os
from flask import Flask, request, escape, send_from_directory

app = Flask(__name__, static_folder='static')

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/redirect')
def handle_redirect():
    code = request.args.get('code')

    if not code:
        return "Missing URL code", 400

    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()
        cur.execute("SELECT original_url FROM urls WHERE code = %s", (code,))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row:
            return f"""<html><head>
                <meta http-equiv="refresh" content="0; URL='{escape(row[0])}'" />
                </head><body>
                Redirecting...
                </body></html>""", 302
        else:
            return "Short URL not found", 404

    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)