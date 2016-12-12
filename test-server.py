import random
import socketserver
import string
import time
import http.server
from threading import Thread

try:
    from http.server import HTTPStatus
except ImportError:
    class HTTPStatus:
        OK = 200
        NOT_FOUND = 404

class TestTCPServer(socketserver.ThreadingTCPServer):
    def __init__(self, server_port, request_handler_class):
        self.allow_reuse_address = True
        super().__init__(('0.0.0.0', server_port), request_handler_class)


class TestHTTPServer(http.server.HTTPServer):
    def __init__(self, server_port, request_handler_class):
        self.allow_reuse_address = True
        super().__init__(('0.0.0.0', server_port), request_handler_class)


def run_server(server):
    Thread(target=lambda: server.serve_forever()).start()


class SimpleTestHTTPHandler(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server, name):
        self.path = ""
        self.name = name
        super().__init__(request, client_address, server)

    def finish(self):
        print(self.name, self.request.getpeername(), self.path)
        self.request.close()

    def response_404(self):
        self.request.sendall(
            b'HTTP/1.1 404 Not Found\r\nConnection: Close\r\n\r\n'
        )

    def handle(self):
        self.path = ""
        head = self.request.recv(1024)
        space_p = head.find(b' ')
        if space_p < 0:
            self.response_404()
            return
        head = head[space_p + 1:]
        space_p = head.find(b' ')
        if space_p < 0:
            self.response_404()
            return
        self.path = head[: space_p]
        self.handle_route(self.path)

    def handle_route(self, path):
        pass


class BrokenRspHandler(SimpleTestHTTPHandler):
    def __init__(self, request, client_address, server):
        head200 = b'HTTP/1.1 200 OK\r\n'
        self.rsp_list = {
            b'/test/0': b'HTTP1.1 OK\r\n',
            b'/test/1': b'HTTP/1.1 200OK\r\n',
            b'/test/2': head200,
            b'/test/3': head200 + b'brokenHeader-)^-=-34haneda=\n',
            b'/test/4': head200 + b': it is broken',
            b'/test/5': head200 + b'ebisu :\r\n',
            b'/test/6': head200 + b'Connection: Close\r\nContent-Length: 4294967299\r\n\r\n',
            b'/test/7': head200 + b'Content-Length: -2147483649\r\n\r\nshinagawa',
            b'/test/8': head200 + b'Transfer-Encoding: chunked\r\n\r\n-3\r\nakihabara',
        }
        super().__init__(request, client_address, server, "Broken Response")

    def handle_route(self, path):
        rsp = self.rsp_list.get(path)
        if rsp is None:
            self.response_404()
            return
        self.request.sendall(rsp)


random_string_128 = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(128))


class SleepRspHandler(SimpleTestHTTPHandler):
    def __init__(self, request, client_address, server):
        head200 = b'HTTP/1.1 200 OK\r\n'
        self.rsp_list = {
            b'/test/10': head200 + b'Connection: Close\r\n\r\nHello World!',
            b'/test/11': head200 + b'Content-Length: 10\r\n\r\nJavaScript',
            b'/test/12': head200 + b'Content-Length: 128\r\n\r\n' + bytes(random_string_128, encoding='utf8')
        }
        super().__init__(request, client_address, server, "Delayed Response")

    def handle_route(self, path):
        rsp = self.rsp_list.get(path)
        if rsp is None:
            self.response_404()
            return
        mid_len = int(len(rsp) / 2)
        self.request.sendall(rsp[:mid_len])
        time.sleep(1)
        self.request.sendall(rsp[mid_len:])


class DifferentEncodingRspHandler(http.server.BaseHTTPRequestHandler):
    gzipped_body = b'\x1f\x8b\x08\x00\x19\x95NX\x00\x03\xd5S\xedR\xdaP\x10\xfd\x7f\x9f"o\xd2Ws/(\x84\x801\x8a\x80\xa2' \
                   b'E\xab\x12\x0c\xc3\x872m)\xa2<\xccro\x92\xb7\xe8\xd9Mu\xfa\xcf\xfe\xedL&\xc9d\xef\x9e=\xe7\xecIy' \
                   b'\xdbe{\xca\xd4g\x8a\xd8\x12\xd3\x88i\xce\xb4\x08\xf2\xc3\x94m\x9b)f:\xd7k^\xdc\xc5\xc5\xae' \
                   b'\x8b\xa3\xc6\xf8a\xcf\x0fR\xa6)\xd3\x11S\xc6t\x89\x83>\x8c\xb4\xf7\x99m\x88\x97\xfdK\xcb\xf7' \
                   b'\x1f\x8c\x8f\x81Pg\x1a\xb3\x8d\x8aF\xe6\x9ahX\xb8e\x02\x1cw\x0f\x88S\x05O\xcd\xfe\x15\x8f\xc8' \
                   b'\xdd\x87lc\xb6-\xa6\xeb\n\xdb/A\xad\xad\x04\xc7\x02dA\xb3i\xdc\xae\x86\xe9.\xd92\xad\x849%(\xb8' \
                   b'\x93\xa1\x12\x18\xea\xc0\x1b\xa6\x990m\x00-\x7f\xdc\x04Z\xfa\xaa\xa5\xd1~\xd3\xf4\xf5\x91\x11' \
                   b'\xc6"\x1e\x85e50\xd0\xfa=F\x08\x07k]k\xe8\xb6?\xf1\xd1E\re\x92\x1a\xe3\x0eC\xa9\xbc>\xe1\xce' \
                   b'\xf4\x86I\xa5\x0c\x83\xccq (\xe2Z*\'j\xe7\xea\xc4\xc2\xb8z\xa6\x02\xc4\xc5\xfc\xe4(\xef>AR>zP' \
                   b'\x9d0\xbcn`\x16\x0e\x16\x19h\xcc\xddI\xc7\x85\x9d\nC\xcd\xad\x07\xc5\x16\xe4:R{\xdd\xfa\xde/\xa6' \
                   b'5XL\xca\xda\xa4\xa4cw\xfc\xa2\x8b\xc8\xc4\x01\xe9\x9b\x06\xc58\x12\x110\x85\xa6\xc5-\xe8\x9cA' \
                   b'\x9a1\xfa\x9c\xef\xd7\xbd\xfc\x1c\xdf\x16\xc2\x1dnRZ\xdel\x95I\xa6\xe2gL\x13\xa3\xdec\xe6\x0f' \
                   b'\xe8\x12\x1d\xe0=\x9c\xabW\x91j\x8a\xe4\x00L\x92cS\xa3\xc6\xb7u\xaa\xac\x19n\x03\x1e\x0b-\xc2g' \
                   b'\xd9\x83\x05\xa9\xa3/F\x15\xdc\x01\xbd\xbc\x06N\\N\x07\x12\x9a\xf5\xe1;`\xa6\x9c.\x85\xe7\x05L,' \
                   b'\xc5.H\xdfA\xc5\x83\xf6f\x12\x04\x1b\x9a?;\xa29\xf2\x85\xce\xc07\xd7\xbe\x96h8\xac\x8b\xe1s\xe2g' \
                   b'\xdf4\xcc\x9a\x18\xb1a$}\xa6\x98\x1c\x14I\xa8\xfb~\xd3k\xc0\xb6\xa6.?*\x83\xfe\xc7\x16o*\xa1\xd0' \
                   b'\xe06\xe3j\x15f\xbf\xee\xb8\x8bI\xde\x9d@r\xd9\xe8\xa8ScmzS\x1ff\xc6\xf5\xae$\x8f\xd6z\xfb\xac' \
                   b'\x85\x9d\x82\x9f\xe9\x95\x06\xbe\x1e\xbbd%\xab\xef\x8e\xd4\xfc\xb6\xfa\x7fV\x19\xfe]Y\xb64e' \
                   b'\x95\xde\x85\x12\xa4\xcaT\x8d\xd6G|@\xe7_\xd5\x98\xbfE\x04\x9f\x88\x90_\xebn\xf9\x9e\xa7\xb0' \
                   b'\xca\x84k6\xf4\x05\xfb\xe8V\\%G\xbe\xb6\x12w\x0fH\xb7?uOHP\xf2\x1f\xff\x1dU\x88?k\x91\x85E' \
                   b'\x1a\xa6\xdf\xe4\x8dm<:\x05\x00\x00'

    def send_rsp_headers(self, code, headers):
        # self.log_request()
        self.send_response(HTTPStatus.OK)
        for k, v in headers.items():
            self.send_header(k, v)
        self.end_headers()

    def do_GET(self):
        headers = dict()
        headers['Connection'] = 'Close'

        if self.path == '/test/20':
            headers['Transfer-Encoding'] = 'chunked'
            self.send_rsp_headers(HTTPStatus.OK, headers)
            self.wfile.write(b'7\r\nHyoka C\r\nd\r\nhitanda Eru\r\n\r\n'
                             b'26\r\nGochumon wa Usagi Desu ka Kafu Chino\r\n\r\n'
                             b'2c\r\nRe Zero kara Hajimeru Isekai Seikatsu Remu\r\n\r\n'
                             b'0\r\n\r\n')

        elif self.path == '/test/21':
            headers['Content-Encoding'] = 'gzip'
            self.send_rsp_headers(HTTPStatus.OK, headers)
            self.wfile.write(self.gzipped_body)

        elif self.path == '/test/22':
            headers['Transfer-Encoding'] = 'chunked'
            headers['Content-Encoding'] = 'gzip'
            self.send_rsp_headers(HTTPStatus.OK, headers)
            p = 0
            while p < len(self.gzipped_body):
                l = random.randint(16, 128)
                if p + l > len(self.gzipped_body):
                    l = len(self.gzipped_body) - p
                self.wfile.write(bytes(hex(l)[2:], 'ascii'))
                self.wfile.write(b'\r\n')
                self.wfile.write(self.gzipped_body[p:p+l])
                self.wfile.write(b'\r\n')
                p = p + l
            self.wfile.write(b'0\r\n\r\n')

        else:
            self.send_response(HTTPStatus.NOT_FOUND)
            self.end_headers()


if __name__ == '__main__':
    run_server(TestTCPServer(8031, BrokenRspHandler))
    run_server(TestTCPServer(8032, SleepRspHandler))
    run_server(TestHTTPServer(8033, DifferentEncodingRspHandler))
