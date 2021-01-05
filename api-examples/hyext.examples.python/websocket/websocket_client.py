import websocket
import json
import time
import threading
import logging
from urllib.parse import urlencode

class WebsocketClient(object):
    """docstring for WebsocketClient"""
    def __init__(self, address, message_callback=None):
        super(WebsocketClient, self).__init__()
        self.address = address
        self.message_callback = message_callback

    def on_message(self, ws, message):
        print("on_client_message:", message)
        if self.message_callback:
            self.message_callback(message)
        data = json.loads(message)
        if "command" == data.get("notice"):
            print("-------- 监听事件：{} 成功--------".format(data.get("data")))
        if "getSendItemNotice" == data.get("notice"):
            print("-------- 粉丝勋章：{},粉丝等级:{},礼物id:{},贵族等级:{},房间号:{},送礼连击数:{},送礼者昵称:{},用户等级:{} --------"
                  .format(data.get("data").get("badgeName"),
                          data.get("data").get("fansLevel"),
                          data.get("data").get("itemId"),
                          data.get("data").get("nobleLevel"),
                          data.get("data").get("roomId"),
                          data.get("data").get("sendItemCount"),
                          data.get("data").get("sendNick"),
                          data.get("data").get("senderLevel")))

    def on_error(self, ws, error):
        logging.exception(error)

    def on_close(self, ws):
        print("### client closed ###")
        self.ws.close()
        self.is_running = False

    def on_open(self, ws):
        self.is_running = True
        print("on open")

    def close_connect(self):
        self.ws.close()

    def send_message(self, message):
        try:
            self.ws.send(message)
        except Exception as err:
            logging.exception(err)


    def run(self):
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(self.address,
                                         on_message = lambda ws,message: self.on_message(ws, message),
                                         on_error = lambda ws, error: self.on_error(ws, error),
                                         on_close = lambda ws :self.on_close(ws))
        self.ws.on_open = lambda ws: self.on_open(ws)
        self.is_running = False
        while True:
            print(self.is_running)
            if not self.is_running:
                self.ws.run_forever()
            time.sleep(3)


class WSClient(object):
    def __init__(self, address, call_back):
        super(WSClient, self).__init__()
        self.client = WebsocketClient(address, call_back)
        self.client_thread = None

    def run(self):
        self.client_thread = threading.Thread(target=self.run_client)
        self.client_thread.start()

    def run_client(self):
        self.client.run()

    def send_message(self, message):
        print(message)
        self.client.send_message(message)


appId = "hda4989c0d21502c"
roomId = "18628950"
socket_uri = "ws://ws-apiext.huya.com/index.html?"
jwt = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjcmVhdG9yIjoiU1lTIiwicm9sZSI6IlAiLCJwcm9maWxlSWQiOiJ1bjFGeE5BUFFmdytCTkN0VmRKbFNEMWNlTU12VlpxUk5KIiwiYXBwSWQiOiJoZGE0OTg5YzBkMjE1MDJjIiwiZXh0SWQiOiJyZzhkY2QyMSIsImV4cCI6MTYwOTgzOTE5NiwidXNlcklkIjoidW4xRnhOQVBRZncrQk5DdFZkSmxTRDFjZU1NdlZacVJOSiIsImlhdCI6MTYwOTgzNTU5Niwicm9vbUlkIjoiMTg2Mjg5NTAifQ.GCpBjS66KV20YsACXSI--GMJvHGvDWosy-8WVd9k4vA"

params = {
    "iat": 1609835596,
    "exp": 1609839196,
    "sToken": jwt,
    "appId": appId,
    "roomId": 942020,
    "do": "comm",
}
socket_uri += urlencode(params)
print(socket_uri)
ws_client = WSClient(socket_uri, lambda message: print("call_back message:", message))
ws_client.run()

while True:
    message = {
        "command": "subscribeNotice",
        "data": ["getSendItemNotice"],
        "reqId": int(time.time())
    }
    message = json.dumps(message).encode()
    ws_client.send_message(message)
    time.sleep(5)
