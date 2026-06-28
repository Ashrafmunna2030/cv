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
        
        # Health check
        if path == '/api/health' or path == '/':
            self._send_json({
                "status": "success",
                "message": "Garena Fresh Cookie API - Per Request",
                "version": "3.0",
                "endpoints": {
                    "get_player": "/api/player/{uid}",
                    "health": "/api/health"
                }
            })
            return
        
        # Player info
        if path.startswith('/api/player/'):
            uid = path.split('/api/player/')[1].strip()
            if uid:
                result = self._fetch_player(uid)
                self._send_json(result)
                return
        
        # 404
        self._send_json({"status": "error", "message": "Not found"}, 404)
    
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
                
                self._send_json(result)
            except Exception as e:
                self._send_json({"status": "error", "message": str(e)}, 400)
        else:
            self._send_json({"status": "error", "message": "Not found"}, 404)
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _send_json(self, data, status=200):
        """Helper to send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def _fetch_player(self, uid):
        """Fetch player with fresh cookies"""
        try:
            api = GarenaPlayerAPI()
            result = api.get_player_info(uid)
            return result
        except Exception as e:
            return {
                "status": "error",
                "uid": uid,
                "nickname": None,
                "message": str(e)
            }
