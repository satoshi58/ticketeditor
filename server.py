from websocket_server import WebsocketServer
from datetime import datetime
import os
import json
import threading
import datetime
import sys

from ticket import Ticket

#global objects
z_index = 1
ticket_id = 1
tickets = {}
lock = threading.Lock()

def import_ticket(path):
    global ticket_id
    global tickets
    with open(path) as f:
        jsonString = f.read()
        import_data = json.loads(jsonString)
        array = import_data['ticket_list']
        for element in array:
            tid = element['ticket_id']
            owner = 0
            left = element['left']
            top = element['top']
            point = element['point']
            color = element['color']
            text = element['text']
            fixed = element['fixed']
            ticket = Ticket(tid, owner)
            ticket.setPos(top, left)
            ticket.setColor(color)
            ticket.setPoint(point)
            ticket.setText(text)
            if fixed == True:
                ticket.fix()
            tickets[tid] = ticket
            if(tid >= ticket_id):
                ticket_id = tid + 1

def export_ticket(path):
    global tickets
    array = []
    for key in tickets:
        if tickets[key].isRemoved() == False:
            data = {
                "ticket_id": tickets[key].getTiekctID(),
                "top": tickets[key].getTop(),
                "left": tickets[key].getLeft(),
                "text": tickets[key].getText(),
                "point": tickets[key].getPoint(),
                "color": tickets[key].getColor(),
                "fixed": tickets[key].isFixed()
            }
            array.append(data)
    exportdata = {
        "ticket_list": array
    }
    jsonString = json.dumps(exportdata)
    with open(path, mode='w') as f:
        f.write(jsonString)
    return jsonString

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
                "color": tickets[key].getColor(),
                "fixed": tickets[key].isFixed()
            }
            jsonString = json.dumps(data)
            server.send_message(client, jsonString)

def client_left(client, server):
    jsonfile = './' + datetime.datetime.now().strftime('%Y%m%d') + '.json'
    #lock
    lock.acquire()
    #write to json file
    export_ticket(jsonfile)
    #release
    lock.release()
    #release all tickets
    for key in tickets:
        tickets[key].release(client['id'])
 
def message_received(client, server, message):
    global z_index
    global tickets
    global ticket_id
    global lock
    global jsonfile
    recv = json.loads(message)
    if recv['method'] == "addTicket":
        #lock
        lock.acquire()
        #write to json file
        export_ticket(jsonfile)
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
    if recv['method'] == "save":
        jsonfile = './' + datetime.datetime.now().strftime('%Y%m%d') + '.json'
        #lock
        lock.acquire()
        #write to json file
        export_ticket(jsonfile)
        #release
        lock.release()
    if recv['method'] == "exportToJira":
        #set color
        temp_ticket_id = int(recv['ticket_id'])
        ticket = tickets[temp_ticket_id]
        if ticket.exportToJira() == True:
            server.send_message_to_all(message)

if __name__ == '__main__':
    #load parameter file
    args = sys.argv
    if len(args) > 1 and os.path.isfile(args[1]):
        import_ticket(args[1])
    else:
        jsonfile = './' + datetime.datetime.now().strftime('%Y%m%d') + '.json'
        if os.path.isfile(jsonfile):
            import_ticket(jsonfile)

    server = WebsocketServer(9999, host="0.0.0.0")
    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)
    server.set_fn_message_received(message_received)
    server.run_forever()