import sys
import random
import socket
import os
import json

from _thread import *
from threading import Timer

locations = ['Santa Clara, CA','San Francisco, CA','Dallas, TX','Miami, FL','New York, NY','Boston, MA']
weatherTopics = ['Daily', 'Weekly', 'Warning']
subscriptions = {}
clientList = []

FLtopicDetails = {'Daily' : ['Min./Max. temperatures today: 49 / 65, Humidity: 58%, Wind speed: 5mph','Min./Max. temperatures today: 35 / 50','Humidity: 58%, Wind speed: 2mph'],
'Weekly' : ['Weekly Min/Max Temperatures: 45/65, Avg. Humidity: 58%','Weekly Min/Max Temperatures: 45/74, Avg. Humidity: 54%'],
'Warning' : ['Hurricane Warning!','Hurricane Warning!']}

CAtopicDetails = {'Daily' : ['Min./Max. temperatures today: 33 / 74, Humidity: 25%, Wind speed: 1mph', 'Min./Max. temperatures today: 39 / 65,  Humidity: 38% , Wind speed: 0mph'],
'Weekly' : ['Weekly Min/Max Temperatures: 33/74, Avg. Humidity: 36%','Weekly Min/Max Temperatures: 33/74, Avg. Humidity: 54%'],
'Warning' : ['Earthquake Warning!','Earthquake Warning!']}

TXtopicDetails = {'Daily' : ['Min./Max. temperatures today: 49 / 65, Humidity: 58%, Wind speed: 5mph','Min./Max. temperatures today: 52 / 71, Humidity: 18%, Wind speed: 3mph'],
'Weekly' : ['Weekly Min/Max Temperatures: 49/71, Avg. Humidity: 54%', 'Weekly Min/Max Temperatures: 45/74, Avg. Humidity: 54%'],
'Warning' : ['Heat Warning!','Heat Warning!']}

NYtopicDetails = {'Daily' : ['Min./Max. temperatures today: 49 / 65, Humidity: 58%, Wind speed: 6mph','Min./Max. temperatures today: 49 / 65, Humidity: 58%, Wind speed: 4mph'],
'Weekly' : ['Weekly Min/Max Temperatures: 45/74, Avg. Humidity: 58%','Weekly Min/Max Temperatures: 40/75, Avg. Humidity: 30%'],
'Warning' : ['Snow Warning!','Snow Warning!']}

MAtopicDetails = {'Daily' : ['Min./Max. temperatures today: 49 / 65, Humidity: 60%, Wind speed: 5mph','Min./Max. temperatures today: 55 / 63, Humidity: 49%, Wind speed: 5mph'],
'Weekly' : ['Weekly Min/Max Temperatures: 45/74, Avg. Humidity: 54%','Weekly Min/Max Temperatures: 60/74, Avg. Humidity: 45%'],
'Warning' : ['Flood Warning!','Flood Warning!']}

generatedEvents = dict()
dataPublished = dict()

def getCity():
    city = random.choice(locations)
    print("city chosen: " + city)
    generateEvent(city)

def generateEvent(city):
    event = ""
    if city=='Santa Clara, CA':
        topic = random.choice(weatherTopics)
        print("This is topic: ", topic)
        msg = CAtopicDetails[topic]
        print("This is msg: ", msg)
        event = msg[random.choice(list(range(0, len(msg)-1)))]
    if city == 'San Francisco, CA':
        topic = random.choice(weatherTopics)
        print("This is topic: ", topic)
        msg = CAtopicDetails[topic]
        print("This is msg: ", msg)
        event = msg[random.choice(list(range(0, len(msg)-1)))]
    elif city=='Dallas, TX':
        topic = random.choice(weatherTopics)
        print("This is topic: ", topic)
        msg = TXtopicDetails[topic]
        print("This is msg: ", msg)
        event = msg[random.choice(list(range(0, len(msg)-1)))]
    elif city == 'Miami, FL':   
        topic = random.choice(weatherTopics)
        print("This is topic: ", topic)
        msg = FLtopicDetails[topic]
        print("This is msg: ", msg)
        event = msg[random.choice(list(range(0, len(msg)-1)))]
    elif city == 'New York, NY':    
        topic = random.choice(weatherTopics)
        print("This is topic: ", topic)
        msg = NYtopicDetails[topic]
        print("This is msg: ", msg)
        event = msg[random.choice(list(range(0, len(msg)-1)))]
    elif city == 'Boston, MA':   
        topic = random.choice(weatherTopics)
        print("This is topic: ", topic)
        msg = MAtopicDetails[topic]
        print("This is msg: ", msg)
        event = msg[random.choice(list(range(0, len(msg)-1)))]

    if (os.getenv("SERVER_ROLE") == "Secondary"):
        # print("City before publish"+city)
        publish(topic, event, city, False)
    else:
        # print("City before publish, in else"+city)
        publish(topic, event, city, True)
    #return event

def publish(topic, event,city, indicator):
    event = topic + ' - ' + city + ' - ' + event
    if indicator == True:
        for name, (topic, location) in subscriptions.items() :
            if topic in weatherTopics:
                if location in locations:
                    if name in generatedEvents.keys():
                        generatedEvents[name].append(event)
                    else:
                        generatedEvents.setdefault(name, []).append(event)
                    dataPublished[name] = 1
            else:
                print("Topic does not exist")

    else:
        print("subscriptions ", subscriptions)
        for name, (topic, location) in subscriptions.items() :
            if name in clientList: # only for clients
                if topic in weatherTopics:
                   if location in locations:
                        if name in generatedEvents.keys():
                            generatedEvents[name].append(event)
                        else:
                            generatedEvents.setdefault(name, []).append(event)
                        dataPublished[name] = 1

    t = Timer(random.choice(list(range(10,16))), getCity)
    t.start()

def subscribeToTopic(clientData):
    subscriptions[clientData['clientName']] = tuple([clientData['topic'], clientData['location']])

def threadedClient(connection, clientRecvdData):
    print("Received data inside threaded client: ", clientRecvdData)
    while True:
        dataPublished[clientRecvdData['clientName']] = 0
        subscribeToTopic(clientRecvdData)

        print("Client data received:", clientRecvdData)

        print("subscriptions", subscriptions[clientRecvdData['clientName']])
        
        subscriptionInfo = 'Your subscriptions are : ' + str(subscriptions[clientRecvdData['clientName']])
        connection.send(subscriptionInfo.encode())

        while True:
            if dataPublished[clientRecvdData['clientName']] == 1:
                notify(connection, clientRecvdData['clientName'])
    connection.close()

def notify(connection, clientName):
    print("generated events: ", generatedEvents)
    if clientName in generatedEvents.keys():
        for msg in generatedEvents[clientName]:
            print("Ready to send to .. "+ clientName)
            msg = msg  + str("\n")
            print("message: "+ msg)
            connection.send(msg.encode())
            print("Sent to "+ clientName)
        del generatedEvents[clientName]
        print("dataPublished from notify before ", dataPublished)
        dataPublished[clientName] = 0
        print("dataPublished from notify after ", dataPublished)


#Method for server 2
def threadedPrimaryReceiver(secondarySocket):
    print("Inside primary receiver method")
    while True:
        print("in loop")
        data = secondarySocket.recv(2048).decode()
        print("data len", len(data))
        if data != "":
            print("data from primary:", data)
            print("data len", len(data))
            secondaryServerData = json.loads(data)
            if secondaryServerData:
                start_new_thread(threadedClient, (secondarySocket,secondaryServerData))
                # topic = secondaryServerData['topic']
                # getCity(secondaryServerData['location'])
        else:
            print("no data from server")
    secondarySocket.close()

#method for server 2
def threadedPrimarySender(secondarySocket):
    print("primary sender method")
    while True:
        dataPublished['primary'] = 0
        subscriptions['primary'] = ""
        #subscriptionInfo = 'Your subscriptions are: '+ str(subscriptions['primary'])
        subscriptionInfo = str(subscriptions['primary'])
        secondarySocket.send(subscriptionInfo.encode())
        while True:
            if dataPublished['primary']==1:
                notify(secondarySocket,'primary')
    secondarySocket.close()

#method for server 1 (when it sees request from server 2)
def threadedServerReceiver(connection,data):
    while True:
        data = connection.recv(2048).decode()
        secondaryServerData = json.loads(data)
        print("Received from Primary: ", secondaryServerData)
        if secondaryServerData:
            topic = secondaryServerData['topic']
            getCity(secondaryServerData['location'])
    connection.close()

def main():

    host = ''
    print("starting main ..")
    if (os.getenv("SERVER_ROLE") == "Secondary"):
        serverPort = int(os.getenv('SECONDARY_SERVER_PORT'))
        serverName = 'server002'
        sockId = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        sockId.bind((host,serverPort))
        print("Socket bind completed to port :", serverPort)
        sockId.listen(5)
        print("Socket is now listening for new connection ...")
        serverThread = Timer(random.choice(list(range(4,7))), getCity)
        serverThread.start()

        primaryHost = 'server001' #env variable
        primaryPort = int(os.getenv('PRIMARY_SERVER_PORT'))
        secondarySocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        secondarySocket.connect((primaryHost,primaryPort))   
        serverSubscriptionData = {'clientName':'server002','location':'Santa Clara, CA','topic':'Daily'}
        stringData = json.dumps(serverSubscriptionData)  
        print("string data", stringData)
        secondarySocket.send(stringData.encode())
        start_new_thread(threadedPrimaryReceiver, (secondarySocket,))
        #start_new_thread(threadedClient, (secondarySocket,stringData))
        #start_new_thread(threadedPrimarySender, (secondarySocket,))
    else:
        serverPort = int(os.getenv('PRIMARY_SERVER_PORT'))

        sockId = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        sockId.bind((host,serverPort))
        print("Socket bind completed to port :", serverPort)
        sockId.listen(5)
        print("Socket is now listening for new connection ...")
    
        serverThread = Timer(random.choice(list(range(4,7))), getCity)
        serverThread.start()

    while True:

        connection, addr = sockId.accept() 
        print('Connected to :', addr[0], ':', addr[1])
        data = connection.recv(2048).decode()    

        print("this is data", data)

        # convert string to dict
        clientData = json.loads(data)
        
        if clientData['clientName'] == 'client-01' or clientData['clientName'] == 'client-02':
            clientList.append(clientData['clientName'])
            print("client list", clientList)
            start_new_thread(threadedClient, (connection,clientData))
            
        if clientData['clientName']=='server002':
            clientList.append(clientData['clientName'])
            start_new_thread(threadedClient, (connection,clientData))
            #start_new_thread(threadedServerSender, (connection,clientData))
            #start_new_thread(threadedServerReceiver, (connection,clientData))
    sockId.close()

if __name__ == '__main__':
    main()