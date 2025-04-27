import http.server
import socketserver

PORT = 4000

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Hello, World!')

print(f"Starting simple HTTP server on port {PORT}")
httpd = socketserver.TCPServer(("0.0.0.0", PORT), Handler)
httpd.serve_forever()