import websocket, threading, time, json, random, re
import settings
import codes #py file containing secret keys and ID info
from dataBaseClass import Sub
from datetime import datetime
from frontPanel import LED_Blue

#make sure to install the websocket module with: sudo pip3 install websocket-client

#to get user id: https://api.twitch.tv/kraken/users/<name>?client_id=apitoken
#to get channel id: https://api.twitch.tv/kraken/channels/<name>?client_id=apitoken

#user name vs display name:
#need to check if display name has non ^[a-zA-Z0-9_]{4,25}$ chars use username instead 

pingstarttime = 0
pingTwitch = 0
SUBdidWork = 0

twitchOAuthToken = codes.twitchOAuth # this is generated at https://twitchapps.com/tokengen/ with scope "channel_subscriptions" and the api token from the dev dasboard
channelID = codes.channelID #oh_bother number code
userID = settings.pubSubUserId #lebtvlive

#e4t5v345nz3sm is just a unique code we set to check for in the return from twitch
#listenrequest = {"type": "LISTEN", "nonce": "e4t5v345nz3sm", "data": { "topics": ["whispers." + userID], "auth_token": twitchOAuthToken}} #this is what i tested it with for whisper messages
listenrequest = {"type": "LISTEN", "nonce": "e4t5v345nz3sm", "data": { "topics": ["channel-subscribe-events-v1." + channelID], "auth_token": twitchOAuthToken}} #this is for sub events
ws1 = ""

def ws1_on_message(ws, message):
    jsonReturn = json.loads(message)
    if "type" in jsonReturn:
        if jsonReturn["type"] == "PONG": #Take care of pong responses
            pingstarttime = 0
            print("PONG received")
            LED_Blue.on()
        elif jsonReturn["type"] == "RECONNECT": #Close if twitch tells us so and reconnect
            print(jsonReturn)
            ws.close()
        elif jsonReturn["type"] == "RESPONSE": #We get this as a response to our subToTopic request
            if jsonReturn["nonce"] == "e4t5v345nz3sm" and jsonReturn["error"] == "": #validate this is the right response and there was no error
                print("Sub successful")
                SUBdidWork = 1
            else: #If there was something wrong
                print(jsonReturn)
        elif jsonReturn["type"] == "MESSAGE": #This is the message you get when an event itself happens
            #print(jsonReturn["data"]["message"])
            makeEntry(json.loads(jsonReturn["data"]["message"]))
        else:
            print(jsonReturn) #if there is anything else, just print it(shouldn't be the case)

def makeEntry(message):
    if 'recipient_user_name' in message.keys():
        repName = message['recipient_display_name']
        repUser = message['recipient_user_name']
        
        if checkName(repName):
            enterDb(repName)
            #print(repName)
        else:
            enterDb(repUser)
            #print(repUser)
    else:
        dispName = message['display_name']
        usrName = message['user_name']

        if checkName(dispName):
            enterDb(dispName)
            #print(dispName)
        else:
            enterDb(usrName)
            #print("fuck you buddy")

def checkName(name):
    if re.search(r'[^a-zA-Z0-9_]', name):
        return False
    else:
        return True
        
def enterDb(entry):
    print("pubSub: entering " + entry)
    dateTime = datetime.utcnow()
    dbEntry = Sub.create(
                        userName = entry,
                        entryTime = dateTime
                    )
    dbEntry.save()
       
def ws1_on_error(ws, error): #get's called when there was a websocket connection error
    global pingTwitch, SUBdidWork
    print (error)
    pingTwitch = 0
    SUBdidWork = 0
    LED_Blue.blink()

def ws1_on_close(ws): #get's called when the websocket connection was closed
    global pingTwitch, SUBdidWork
    print("### ws1 closed ###")
    pingTwitch = 0
    SUBdidWork = 0
    LED_Blue.off()

def ws1_on_open(ws): #get's called when the websocket connection was opened (connected to the server and handshake successfull)
    global pingTwitch
    print("### ws1 opened ###")
    pingTwitch = 1
    subToTopics()

def ws1_start(): #this is the main server loop
    while True:
        ws1.run_forever()
        print("### ws1 restart ###")

def subToTopics(): #send our listen request
    ws1.send(json.dumps(listenrequest))

def pingTwitchServersToKeepTheConnectionAliveTask(): #This PINGs the server every 4 minutes as per twitch api docs
    while True:
        if pingTwitch:
            print("Pinging Twitch")
            ws1.send(json.dumps({"type": "PING"}))
            LED_Blue.off()
            pingstarttime = time.time() #we could later do something with this time but we don't have to
            time.sleep(10) #wait 10 sec for ping response
            if not pingstarttime: #is pingstarttime was not reset, close the connection
                ws.close()
            time.sleep(240 + random.randrange(-10, 10)) #Sleep 4 min +/- 10sec (random is required by twitch api)

def webSocketInit():
    global ws1
    print("pubSub started, opening socket")
    ws1 = websocket.WebSocketApp("wss://pubsub-edge.twitch.tv", on_message = ws1_on_message, on_error = ws1_on_error, on_close = ws1_on_close) #Create Websocket Client Object
    ws1.on_open = ws1_on_open
    threading.Thread(target=ws1_start).start() #Start Websocket Thread
    threading.Thread(target=pingTwitchServersToKeepTheConnectionAliveTask).start() # Start PING Thread
 
if __name__ == "__main__":
    webSocketInit()
    threading.Thread(target=ws1_start).start() #Start Websocket Thread
    threading.Thread(target=pingTwitchServersToKeepTheConnectionAliveTask).start() # Start PING Thread
