# A very simple and dumb xAPI LRS server implementation that lets you log incoming statements on a local environment.
# It also allows you to record and server (in RAM) lesson attempt states
import http.server, http.server
from urllib.parse import urlparse, parse_qs
import json

STATES = {}

class MyServerHandler(http.server.SimpleHTTPRequestHandler):


    def parse_params(self):
        url = urlparse(self.path)
        return parse_qs(url.query)

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, X-Experience-API-Version, Authorization, Content-Type, ETag")


    def do_GET(self):
        self.log_request()
        print((self.headers))
        #import pdb; pdb.set_trace()
        params = self.parse_params()
        if 'stateId' in params:
            try:
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header("Content-Type","application/json")
                self.end_headers()
                self.wfile.write(STATES[params['stateId'][0]])
            except Exception as e:
                print(e)
                self.send_response(404)
        else:
            self.send_response(404)


    def do_POST(self):
        self.log_request()
        print((self.headers))
        load = json.loads(self.rfile.read(int(self.headers.getheader('Content-Length'))))
        print((json.dumps(load, indent=4, separators=(',', ': '))))
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')


    def do_PUT(self):
        self.log_request()
        print((self.headers))
        params = self.parse_params()
        if 'stateId' in params:
            load = self.rfile.read(int(self.headers.getheader('Content-Length')))
            STATES[params['stateId'][0]] = load
        else:
            load = json.loads(self.rfile.read(int(self.headers.getheader('Content-Length'))))
            print((json.dumps(load, indent=4, separators=(',', ': '))))
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')


def run(server_class=http.server.HTTPServer,
        handler_class=MyServerHandler):
    server_address = ('', 8040)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()
    
run()