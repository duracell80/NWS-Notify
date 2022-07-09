import sys, os
from http.server import HTTPServer, SimpleHTTPRequestHandler

HOST_NAME = "192.168.2.201"
PORT = 8228


def read_file(path):
    try:
        with open(path) as f:
            file = f.read()
    except Exception as e:
        file = e
    return file


def serve_html(self):
	file = read_file(self.path)
	self.send_response(200, "OK")
	self.end_headers()
	self.wfile.write(bytes(file, "utf-8"))

def serve_error(self):
	self.send_response(403)
	self.end_headers()

def serve_feed(self):
    file = read_file("/tmp/nws_data.xml")
    self.send_response(200, "OK")
    self.send_header("Content-type", 'text/xml')
    self.end_headers()
    self.wfile.write(bytes(file, "utf-8"))



class PythonServer(SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/index':
            self.path = './templates/index.html'
            serve_html(self)
        if self.path == '/data':
            serve_error(self)
        if self.path == '/sql':
            serve_error(self)
        if self.path == '/sensors/':
            serve_error(self)
        if self.path == '/feed':
            serve_feed(self)
        if self.path == '/save':
            self.path = './templates/save.html'
            serve_html(self)
        else:
            #print("superted")
            super().do_GET()


	
if __name__ == "__main__":
    server = HTTPServer((HOST_NAME, PORT), PythonServer)
    print(f"Server started http://{HOST_NAME}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
        print("Server stopped successfully")
        sys.exit(0)
