import json
import asyncio
import websockets
import queue
from http.server import SimpleHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

# Using a thread-safe Queue from the queue module
message_queue = queue.Queue()

# Set of connected WebSocket clients
connected_clients = set()


class AsyncServer:
    def __init__(self):
        self.loop = asyncio.new_event_loop()

    async def websocket_server(self):
        server = await websockets.serve(self.handler, "localhost", 7890)
        await server.wait_closed()

    async def handler(self, websocket, path):
        connected_clients.add(websocket)
        try:
            while websocket.open:
                if not message_queue.empty():
                    message = message_queue.get_nowait()
                    await websocket.send(message)
                else:
                    await asyncio.sleep(0.1)
        finally:
            connected_clients.remove(websocket)

    def run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.websocket_server())


class LoggingHandler(SimpleHTTPRequestHandler):
    def print_request(self, body=None):
        request_dict = {
            "method": self.command,
            "path": self.path,
            "headers": dict(self.headers),
        }
        if body:
            request_dict["body"] = body
        message = json.dumps(request_dict, indent=4)
        message_queue.put(message)  # Putting messages in the thread-safe Queue

    def do_GET(self):
        self.print_request()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode()
        self.print_request(body)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def do_PUT(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode()
        self.print_request(body)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def do_DELETE(self):
        self.print_request()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def do_PATCH(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode()
        self.print_request(body)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def do_COPY(self):
        self.print_request()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


async_server = AsyncServer()

# Running the Websocket server in a separate thread
import threading

threading.Thread(target=async_server.run, daemon=True).start()

# HTTP Server Setup
httpd = ThreadingHTTPServer(("", 80), LoggingHandler)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("Shutting down server...")
    httpd.shutdown()
