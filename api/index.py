from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from garena_api import GarenaPlayerAPI

class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Handle GET requests"""
        path = self.path
        
        if path == '/api/health' or path == '/':
            self._send_response({
                "status": "success",
                "message": "Garena Fresh Cookie API - Per Request",
                "version": "3.0",
                "features": "Fresh cookie generated for EVERY request",
                "endpoints": {
                    "get_player": "/api/player/{uid}",
                    "health": "/api/health"
                }
            })
            return
        
        if path.startswith('/api/player/'):
            uid = path.split('/api/player/')[1]
            if uid:
                result = self._fetch_player(uid)
                self._send_response(result)
                return
        
        self._send_response({"status": "error", "message": "Not found"}, 404)
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/player':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data)
                uid = data.get('uid')
                
                if uid:
                    result = self._fetch_player(uid)
                else:
                    result = {"status": "error", "message": "Missing 'uid'"}
                
                self._send_response(result)
            except:
                self._send_response({"status": "error", "message": "Invalid JSON"}, 400)
        else:
            self._send_response({"status": "error", "message": "Not found"}, 404)
    
    def do_OPTIONS(self):
        """CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def _send_response(self, data: dict, status: int = 200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def _fetch_player(self, uid: str) -> dict:
        """Fetch player info with FRESH cookies"""
        print(f"\n{'🔄'*20}")
        print(f"🆕 NEW REQUEST - Generating fresh cookies")
        print(f"🎯 UID: {uid}")
        print(f"⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        api = GarenaPlayerAPI()
        result = api.get_player_info(uid)
        
        print(f"📤 Result: {result.get('status')}")
        print(f"{'='*50}\n")
        
        return result            response = {"status": "success", "message": "API is running"}
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
