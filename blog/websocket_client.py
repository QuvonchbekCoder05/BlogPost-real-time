import websocket
import json


# Xabar kelganda ishlaydigan funksiya
def on_message(ws, message):
    data = json.loads(message)
    print(json.dumps(data, indent=4))


# Xato yuz berganda ishlaydigan funksiya
def on_error(ws, error):
    print(f"Xato yuz berdi: {error}")


# Aloqa yopilganda ishlaydigan funksiya
def on_close(ws, close_status_code, close_msg):
    print("🔵 WebSocket aloqasi yopildi")


# Aloqa ochilganda ishlaydigan funksiya
def on_open(ws):
    print("🟢 WebSocket aloqasi ochildi")


# WebSocket ulanishini sozlash
ws = websocket.WebSocketApp(
    "ws://127.0.0.1:8000/ws/posts/",  # 📌 URL to‘g‘ri ekanligiga ishonch hosil qiling
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
    on_open=on_open,
)

# WebSocket-ni doimiy ishga tushirish
ws.run_forever()
