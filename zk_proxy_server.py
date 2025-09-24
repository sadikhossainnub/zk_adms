#!/usr/bin/env python3
import http.server
import socketserver
import urllib.request
import urllib.parse
from urllib.error import URLError

class ZKProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.proxy_request()
    
    def do_POST(self):
        self.proxy_request()
    
    def proxy_request(self):
        try:
            # Get request data
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else None
            
            # Build target URL
            query_string = urllib.parse.urlparse(self.path).query
            target_url = f"http://localhost:8000/iclock/?{query_string}"
            
            # Create request
            req = urllib.request.Request(target_url, data=post_data, method=self.command)
            req.add_header('Content-Type', self.headers.get('Content-Type', 'application/x-www-form-urlencoded'))
            
            # Forward request
            with urllib.request.urlopen(req) as response:
                self.send_response(response.status)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(response.read())
                
        except URLError as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"ERROR")

if __name__ == "__main__":
    PORT = 7788
    with socketserver.TCPServer(("", PORT), ZKProxyHandler) as httpd:
        print(f"ZK Proxy server running on port {PORT}")
        httpd.serve_forever()