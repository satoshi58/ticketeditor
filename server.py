from websocket_server import WebsocketServer
from datetime import datetime
import json
import threading

#global objects
z_index = 1
ticket_id = 1
tickets = {}
lock = threading.Lock()

class Ticket:
    ticket_id = 0
    locked = False
    locker = 0
    text = ""
    owner = 0
    top = 0
    left = 0
    point = "-"
    color = "#ffffff"
    removed = False
    def __init__(self, ticket_id, owner):
        self.ticket_id = ticket_id
        self.owner = owner
    def setText(self, text):
        self.text = text
    def setPos(self, top, left):
        self.top = top
        self.left = left
    def setPoint(self, point):
        self.point = point
    def setColor(self, color):
        self.color = color
    def lock(self, client_id):
        if self.locked == False and self.locker == 0:
            self.locked = True
            self.locker = client_id
            return True
        else:
            return False
    def release(self, client_id):
        if self.locked == True and self.locker == client_id:
            self.locked = False
            self.locker = 0
            return True
        else:
            return False
    def remove(self):
        self.removed = True
    def isRemoved(self):
        return self.removed
    def getTiekctID(self):
        return self.ticket_id
    def getText(self):
        return self.text
    def getTop(self):
        return self.top
    def getLeft(self):
        return self.left
    def getPoint(self):
        return self.point
    def getColor(self):
        return self.color

def new_client(client, server):
    global tickets
    global lock
    #notify client ID
    data = {
        "method": "notifyClientID",
        "client_id": client['id']
    }
    jsonString = json.dumps(data)
    server.send_message(client, jsonString)

    #init tickets
    for key in tickets:
        if tickets[key].isRemoved() == False:
            data = {
                "method": "initTicket",
                "ticket_id": tickets[key].getTiekctID(),
                "top": tickets[key].getTop(),
                "left": tickets[key].getLeft(),
                "text": tickets[key].getText(),
                "point": tickets[key].getPoint(),
                "color": tickets[key].getColor()
            }
            jsonString = json.dumps(data)
            server.send_message(client, jsonString)

def client_left(client, server):
    #release all tickets
    for key in tickets:
        tickets[key].release(client['id'])
 
def message_received(client, server, message):
    global z_index
    global tickets
    global ticket_id
    global lock
    recv = json.loads(message)
    if recv['method'] == "addTicket":
        #lock
        lock.acquire()
        #create new ticket
        ticket = Ticket(ticket_id, recv['client_id'])
        ticket.setColor(recv['color'])
        tickets[ticket_id] = ticket
        #reply
        recv['ticket_id'] = ticket_id
        jsonString = json.dumps(recv)
        ticket_id = ticket_id + 1
        server.send_message_to_all(jsonString)
        lock.release()
    if recv['method'] == "deleteTicket":
        #lock
        lock.acquire()
        #delete
        temp_ticket_id = int(recv['ticket_id'])
        temp_client_id = int(recv['client_id'])
        ticket = tickets[temp_ticket_id]
        if(ticket.lock(temp_client_id)):
            #NOT delete
            tickets[temp_ticket_id].remove()
            #reply
            server.send_message_to_all(message)
        lock.release()
    if recv['method'] == "lockTicket":
        #lock
        lock.acquire()
        #lock
        temp_ticket_id = int(recv['ticket_id'])
        temp_client_id = int(recv['client_id'])
        ticket = tickets[temp_ticket_id]
        if(ticket.lock(temp_client_id)):
            recv['result'] = "OK"
        else:
            recv['result'] = "NG"
        #reply result
        if recv['next'] == "moveTicket":
            recv['zindex'] = z_index
            z_index = z_index + 1
            jsonString = json.dumps(recv)
            server.send_message_to_all(jsonString)
        else:
            jsonString = json.dumps(recv)
            server.send_message(client, jsonString)
        lock.release()
    if recv['method'] == "releaseTicket":
        #lock
        lock.acquire()
        #release
        temp_ticket_id = int(recv['ticket_id'])
        temp_client_id = int(recv['client_id'])
        ticket = tickets[temp_ticket_id]
        if ticket.release(temp_client_id):
            recv['result'] = "OK"
        else:
            recv['result'] = "NG"
        #reply result
        jsonString = json.dumps(recv)
        server.send_message(client, jsonString)
        lock.release()
    if recv['method'] == "moveTicket":
        #set position
        temp_ticket_id = int(recv['ticket_id'])
        ticket = tickets[temp_ticket_id]
        ticket.setPos(recv['top'], recv['left'])
        #reply
        server.send_message_to_all(message)
    if recv['method'] == "fixTicket":
        #set position
        temp_ticket_id = int(recv['ticket_id'])
        ticket = tickets[temp_ticket_id]
        ticket.setPos(recv['top'], recv['left'])
        #reply
        server.send_message_to_all(message)
    if recv['method'] == "editTicket":
        #set text
        temp_ticket_id = int(recv['ticket_id'])
        ticket = tickets[temp_ticket_id]
        ticket.setText(recv['text'])
        #reply
        server.send_message_to_all(message)
    if recv['method'] == "setPoint":
        #set ticket point
        temp_ticket_id = int(recv['ticket_id'])
        ticket = tickets[temp_ticket_id]
        ticket.setPoint(recv['point'])
        #reply
        server.send_message_to_all(message)
    if recv['method'] == "setColor":
        #set color
        temp_ticket_id = int(recv['ticket_id'])
        ticket = tickets[temp_ticket_id]
        ticket.setColor(recv['color'])
        #reply
        server.send_message_to_all(message)

server = WebsocketServer(9999, host="0.0.0.0")
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)
server.run_forever()