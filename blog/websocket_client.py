import websocket
import json


def on_message(ws, message):
    data = json.loads(message)
    print("🔴 WebSocket xabari keldi:")
    print(json.dumps(data, indent=4))


def on_error(ws, error):
    print("⚠️ Xatolik:", error)


def on_close(ws, close_status_code, close_msg):
    print("🔵 WebSocket aloqasi yopildi")


def on_open(ws):
    print("🟢 WebSocket aloqasi o‘rnatildi!")


ws = websocket.WebSocketApp(
    "ws://127.0.0.1:8000/ws/posts/",
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
)
ws.run_forever()
