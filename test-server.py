import socketserver


class TestTCPServer(socketserver.TCPServer):
    def __init__(self, server_port, request_handler_class):
        self.allow_reuse_address = True
        super().__init__(('0.0.0.0', server_port), request_handler_class)
        self.serve_forever()


class SimpleTestHTTPHandler(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server, name):
        super().__init__(request, client_address, server)
        self.path = ""
        self.name = name

    def finish(self):
        print(self.name, self.request.raddr, self.path)
        self.request.close()

    def response_404(self):
        self.request.sendall(
            b'''404 Not Found HTTP/1.1\r\nConnection: Close\r\n\r\n'''
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
        super().__init__(request, client_address, server, "Broken Response")

    def handle_route(self, path):
        head200 = b'200 OK HTTP/1.1\r\n'
        rsp = {
            b'/test/0': b'200 OK HTTP1.1\r\n',
            b'/test/1': b'200 OK HTTP1.1\r\n',
        }.get(path)
        if rsp is None:
            self.response_404()
            return
        self.request.sendall(rsp)



def main():
    TestTCPServer(8031, BrokenRspHandler)


if __name__ == '__main__':
    main()
