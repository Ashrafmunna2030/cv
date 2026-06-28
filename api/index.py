from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add parent directory to path to import garena_api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from garena_api import GarenaShopAPI

# Default cookies - Vercel environment variable থেকে নিবে, না থাকলে ডিফল্ট ব্যবহার করবে
DEFAULT_COOKIES = {
    "source": os.environ.get("COOKIE_SOURCE", "mb"),
    "region": os.environ.get("COOKIE_REGION", "MY"),
    "language": os.environ.get("COOKIE_LANGUAGE", "en"),
    "mspid2": os.environ.get("COOKIE_MSPID2", "ae0c8e51334bfb875f1eb0e33133cc7b"),
    "_fbp": os.environ.get("COOKIE_FBP", "fb.1.1776001223054.798432025925868321"),
    "_ga": os.environ.get("COOKIE_GA", "GA1.1.1335857066.1777050809"),
    "_ga_9F1KGGRJHY": os.environ.get("COOKIE_GA_9F1KGGRJHY", "GS2.1.s1777050809$o1$g0$t1777050815$j54$l0$h0"),
    "datadome": os.environ.get("COOKIE_DATADOME", "6ukWBivMKRC7_ksMDmJZvo~Kd8Gygg~55W1IuTcxwJB_rc03q4m5Zo30tHBkrwWNeeyzGAaIauCZSiWw2bu13a8qR2kt1JrqBFcKJGy5X6IewgFIHt92jg0Vtaw0eBfY"),
    "__csrf__": os.environ.get("COOKIE_CSRF", "1CTkCrtNaEP00aQYNNCpYvPlxRco89Xa"),
    "session_key": os.environ.get("COOKIE_SESSION_KEY", "angggqlz8nptju3xj5p4ntvrzlphk8m5"),
}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        # Parse URL path
        path = self.path
        
        # Health check endpoint
        if path == '/api/health' or path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"status": "success", "message": "API is running"}
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Player info endpoint: /api/player/{uid}
        if path.startswith('/api/player/'):
            uid = path.split('/api/player/')[1]
            if uid:
                self._handle_player_request(uid)
                return
        
        # Root endpoint
        if path == '/' or path == '':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "status": "success",
                "message": "Garena Player Info API",
                "endpoints": {
                    "get_player": "/api/player/{uid}",
                    "health": "/api/health"
                }
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        # 404 for unknown routes
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = {"status": "error", "message": "Endpoint not found"}
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/player':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
                uid = data.get('uid')
                if uid:
                    self._handle_player_request(uid)
                else:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {"status": "error", "message": "Missing 'uid' in request body"}
                    self.wfile.write(json.dumps(response).encode())
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {"status": "error", "message": "Invalid JSON"}
                self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"status": "error", "message": "Endpoint not found"}
            self.wfile.write(json.dumps(response).encode())
    
    def _handle_player_request(self, uid):
        """Handle player info request"""
        try:
            api = GarenaShopAPI(DEFAULT_COOKIES)
            resp = api.player_id_login(app_id=100067, login_id=uid)
            resp.raise_for_status()
            data = resp.json()
            
            # Extract nickname from different possible response structures
            nickname = data.get("player_name") or data.get("nickname") or data.get("data", {}).get("name")
            
            if nickname:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    "status": "success",
                    "uid": uid,
                    "nickname": nickname
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    "status": "error",
                    "uid": uid,
                    "nickname": None,
                    "message": "Player not found or unable to fetch nickname"
                }
                self.wfile.write(json.dumps(response).encode())
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "status": "error",
                "uid": uid,
                "nickname": None,
                "message": f"Error: {str(e)}"
            }
            self.wfile.write(json.dumps(response).encode())
