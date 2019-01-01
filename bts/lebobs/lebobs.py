import json

from websocket import create_connection


def switchToscene(scenename):
    _sendToOBS({"request-type": "SetCurrentScene", "scene-name": scenename, "message-id": "lebobs"})

def setTransition(transitionname):
    _sendToOBS({"request-type": "SetCurrentTransition", "transition-name": transitionname, "message-id": "lebobs"})
    
def startRec():
    _sendToOBS({"request-type": "StartRecording", "message-id": "lebobs"})

def stopRec():
    _sendToOBS({"request-type": "StopRecording", "message-id": "lebobs"})

def startStream():
    _sendToOBS({"request-type": "StartStreaming", "message-id": "lebobs"})

def stopStream():
    _sendToOBS({"request-type": "StopStreaming", "message-id": "lebobs"})


def _sendToOBS(obj):
    ws = create_connection("ws://localhost:4444")
    ws.send(json.dumps(obj))
    """result =  ws.recv()
    jsn = json.loads(result)
    if jsn["message-id"] == "lebobs" and "status" in jsn:
        if jsn["status"] == "ok":
            print("ok")
    else:
        print(jsn)
        print("Failed to connect to OBS")"""  
    ws.close()
