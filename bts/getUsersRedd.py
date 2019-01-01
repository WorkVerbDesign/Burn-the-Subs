#sudo apt-get install python3-requests
#app had to be registered properly from the reddit thread steps
#https://www.reddit.com/r/Twitch/comments/6ycems/an_example_python_script_to_retrieve_a_list_of/

import json

from requests import Session
from requests.adapters import HTTPAdapter

from bts import codes

##########################################################
#                Configure your stuff here               #
##########################################################
 
clientId = codes.clientId  #Register a Twitch Developer application and put its client ID here
accessToken = codes.twitchOAuth #Generate an OAuth token with channel_subscriptions scope and insert your token here

channelName = codes.channelName  #Put your channel name here
saveLocation = "/home/pi/bts/subscriberListTest.txt" #Put the location you'd like to save your list here
 
###################################################################
 
session=Session()
channelId = "" 
 
 
channelIdUrl="https://api.twitch.tv/kraken/users?login=" + channelName
 
retryAdapter = HTTPAdapter(max_retries=2)
session.mount('https://',retryAdapter)
session.mount('http://',retryAdapter)
 
#Find the Channel ID
response = session.get(channelIdUrl, headers={
'Client-ID': clientId,
'Accept': 'application/vnd.twitchtv.v5+json',
'Content-Type': 'application/json'
})

try:
    result = json.loads(response.text)
except:
    result = None
 
if (result):
    channelId = result["users"][0]["_id"]
 
print(channelId)
 
result = None
response = None
offset = 0
limit = 100
subList = []
 
while (True):
    apiRequestUrl="https://api.twitch.tv/kraken/channels/" + channelId + "/subscriptions?limit=" + str(limit) + "&offset=" + str(offset)
 
    #Do the API Lookup
    response = session.get(apiRequestUrl, headers={
    'Client-ID': clientId,
    'Accept': 'application/vnd.twitchtv.v5+json',
    'Authorization': 'OAuth ' + accessToken,
    'Content-Type': 'application/json'
    })
 
    try:
        result = json.loads(response.text)
    except:
        result = None
 
    if (result):
        print(result) #looking for errors
        
        for sub in result["subscriptions"]:
            name=sub['user']['display_name']
            if name!=channelName:
                print(name)
                subList.append(sub['user']['display_name'])
    else:
        break
 
    if (len(result["subscriptions"])==limit):
        offset+=limit
    else:
        print("Done")
        break
 
 
if(result):
    f = open(saveLocation,'w')
    for sub in subList:
        f.write(sub+"\n")
    f.close()