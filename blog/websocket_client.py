# import websocket
# import json


# def on_message(ws, message):
#     data = json.loads(message)
    
#     print(json.dumps(data, indent=4))


# def on_error(ws, error):
    


# def on_close(ws, close_status_code, close_msg):
#     print("🔵 WebSocket aloqasi yopildi")


# def on_open(ws):
    


#  ws = websocket.WebSocketApp(
#     "ws://127.0.0.1:8000/ws/posts/",  # 📌 URL to‘g‘ri bo‘lishi kerak
#     on_message=on_message,
#     on_error=on_error,
#     on_close=on_close,
# )
# ws.run_forever()
