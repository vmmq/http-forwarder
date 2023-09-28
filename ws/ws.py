import asyncio
import websockets

# A set to hold all connected WebSocket clients
connected_clients = set()


async def relay_message_to_others(message, sender):
    for client in connected_clients:
        # Send the message to all clients, except the sender
        if client != sender:
            await client.send(message)


async def handler(websocket, path):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Received message: {message}")
            await relay_message_to_others(message, websocket)
    finally:
        connected_clients.remove(websocket)


# Start the WebSocket server
start_server = websockets.serve(handler, "localhost", 7890)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
