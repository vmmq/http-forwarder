import websockets
import asyncio
import requests
import json


async def listen():
    url = "ws://161.35.102.255:7890"
    async with websockets.connect(url) as ws:
        await ws.send("Hello Server!")
        while True:
            msg = await ws.recv()
            print(f"Received from Server: {msg}")
            await forward_request(msg)


async def forward_request(msg):
    try:
        request_data = json.loads(msg)

        method = request_data.get("method")
        path = request_data.get("path")
        headers = request_data.get("headers")
        body = request_data.get("body")

        # Prepare the forwarding URL
        forward_url = f"http://localhost:3000{path}"

        # Remove headers causing issues in the request forwarding
        headers.pop("Host", None)
        headers.pop("Content-Length", None)  # Let requests compute this

        # Forward the request
        response = requests.request(method, forward_url, headers=headers, data=body)

        print(
            f"Forwarded Request: {method} {path}, Status Code: {response.status_code}"
        )

    except Exception as e:
        print(f"Error occurred: {e}")


asyncio.get_event_loop().run_until_complete(listen())
