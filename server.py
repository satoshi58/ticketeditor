from websocket_server import WebsocketServer
import os
import json
import datetime
import sys

from ticket import Ticket
from session import Session

#global objects
session_map = {}
client_map = {}
filename = datetime.datetime.now().strftime('%Y%m%d')

def new_client(client, server):
    client_id = client['id']
    #notify client ID
    data = {
        "method": "notifyClientID",
        "client_id": client_id
    }
    jsonString = json.dumps(data)
    server.send_message(client, jsonString)

def client_left(client, server):
    global session_map
    global client_map
    global filename

    #aruire session_id from client_id
    client_id = client['id']
    if client_id not in client_map:
        print('error client_left, no client_id in client_map')
        return 
    session_id = client_map[client_id]

    #acquire detached user's session
    if session_id not in session_map:
        print('error client_left, no session_id in session_map')
        return 
    session = session_map[session_id]

    #write to json file    
    jsonfile = './' + filename + '_' +  session_id  + '.json'
    session.write(jsonfile)
    #release all tickets
    session.release(client_id)
 
def message_received(client, server, message):
    global session_map
    global client_map
    global filename

    #get parameters
    recv = json.loads(message)

    #validation
    if 'method' not in recv:
        print('error message_received, no method in recv')
        return
    if 'client_id' not in recv:
        print('error message_received, no client_id in recv')
        return
    client_id = recv['client_id']

    if recv['method'] == 'connect':
        #validation for connect
        if 'session_id' not in recv:
            print('error message_received, no sessio_id in recv (method=connect)')
            return
        session_id = recv['session_id']

        #acquire session object
        if session_id in session_map:
            #use existing session object
            session = session_map[session_id]
        else:
            #use new session object
            session = Session(session_id)
            #if data is in jsonfile, read it
            jsonfile = './' + filename + '_' + session_id +'.json'
            if os.path.isfile(jsonfile):
                session.read(jsonfile)
            session_map[session_id] = session

        #init tickets
        tickets = session.getTickets()
        for key in tickets:
            if tickets[key].isRemoved() == False:
                data = {
                    "method": "initTicket",
                    "ticket_id": tickets[key].getTicketID(),
                    "top": tickets[key].getTop(),
                    "left": tickets[key].getLeft(),
                    "text": tickets[key].getText(),
                    "point": tickets[key].getPoint(),
                    "color": tickets[key].getColor(),
                    "fixed": tickets[key].isFixed()
                }
                jsonString = json.dumps(data)
                server.send_message(client, jsonString)       
        #now add session_id on client_map
        client_map[client_id] = session_id
        return

    #get session_id and session object
    if client_id not in client_map:
        print('error message_received, no client_id in client_map')
        return
    session_id = client_map[client_id]
    if session_id not in session_map:
        print('error message_received, no session_id in session_map')
        return
    session = session_map[session_id]

    if recv['method'] == "addTicket":
        #create new ticket
        ticket_id = session.getNewTicketID()
        ticket = Ticket(ticket_id, client_id)
        ticket.setColor(recv['color'])
        session.addTicket(ticket)
        #reply
        recv['ticket_id'] = ticket_id
        recv['session_id'] = session_id
        jsonString = json.dumps(recv)
        server.send_message_to_all(jsonString)
    if recv['method'] == "deleteTicket":
        #delete
        ticket_id = int(recv['ticket_id'])
        tickets = session.getTickets()
        ticket = tickets[ticket_id]
        if(ticket.lock(client_id)):
            #NOT delete
            tickets[ticket_id].remove()
            recv['session_id'] = session_id
            jsonString = json.dumps(recv)
            #reply
            server.send_message_to_all(jsonString)
    if recv['method'] == "lockTicket":
        ticket_id = int(recv['ticket_id'])
        tickets = session.getTickets()
        ticket = tickets[ticket_id]
        if(ticket.lock(client_id)):
            recv['result'] = "OK"
        else:
            recv['result'] = "NG"
        #reply result
        if recv['next'] == "moveTicket":
            recv['zindex'] = session.getNewZIndex()
            recv['session_id'] = session_id
            jsonString = json.dumps(recv)
            server.send_message_to_all(jsonString)
        else:
            recv['session_id'] = session_id
            jsonString = json.dumps(recv)
            server.send_message(client, jsonString)
    if recv['method'] == "releaseTicket":
        #release
        ticket_id = int(recv['ticket_id'])
        tickets = session.getTickets()
        ticket = tickets[ticket_id]
        if ticket.release(client_id):
            recv['result'] = "OK"
        else:
            recv['result'] = "NG"
        recv['session_id'] = session_id
        #reply result
        jsonString = json.dumps(recv)
        server.send_message(client, jsonString)
    if recv['method'] == "moveTicket":
        #set position
        ticket_id = int(recv['ticket_id'])
        tickets = session.getTickets()
        ticket = tickets[ticket_id]
        ticket.setPos(recv['top'], recv['left'])
        #reply
        recv['session_id'] = session_id
        jsonString = json.dumps(recv)
        server.send_message_to_all(jsonString)
    if recv['method'] == "fixTicket":
        #set position
        ticket_id = int(recv['ticket_id'])
        tickets = session.getTickets()
        ticket = tickets[ticket_id]
        ticket.setPos(recv['top'], recv['left'])
        #reply
        recv['session_id'] = session_id
        jsonString = json.dumps(recv)
        server.send_message_to_all(jsonString)
    if recv['method'] == "editTicket":
        #set text
        ticket_id = int(recv['ticket_id'])
        tickets = session.getTickets()
        ticket = tickets[ticket_id]
        ticket.setText(recv['text'])
        #reply
        recv['session_id'] = session_id
        jsonString = json.dumps(recv)
        server.send_message_to_all(jsonString)
    if recv['method'] == "setPoint":
        #set ticket point
        ticket_id = int(recv['ticket_id'])
        tickets = session.getTickets()
        ticket = tickets[ticket_id]
        ticket.setPoint(recv['point'])
        #reply
        recv['session_id'] = session_id
        jsonString = json.dumps(recv)
        server.send_message_to_all(jsonString)
    if recv['method'] == "setColor":
        #set color
        ticket_id = int(recv['ticket_id'])
        tickets = session.getTickets()
        ticket = tickets[ticket_id]
        ticket.setColor(recv['color'])
        #reply
        recv['session_id'] = session_id
        jsonString = json.dumps(recv)
        server.send_message_to_all(jsonString)
    if recv['method'] == "save":
        #write to json file
        jsonfile = './' + filename + '_' + session_id + '.json'
        #write to json file
        session.write(jsonfile)
    if recv['method'] == "exportToJira":
        #set color
        ticket_id = int(recv['ticket_id'])
        tickets = session.getTickets()
        ticket = tickets[ticket_id]
        ticket.setTag(recv['tag'])
        ticket.exportToJira()
    if recv['method'] == "importFromJira":
        #create new ticket
        ticket_id = session.getNewTicketID()
        ticket = Ticket(ticket_id, client_id)
        ticket.setColor(recv['color'])
        ticket.importFromJira(recv['key'])
        session.addTicket(ticket)
        #reply
        recv['ticket_id'] = ticket.getTicketID()
        recv['text'] = ticket.getText()
        recv['session_id'] = session_id
        jsonString = json.dumps(recv)
        server.send_message_to_all(jsonString)

if __name__ == '__main__':
    args = sys.argv
    if len(args) > 1 and os.path.isfile(args[1]):
        filename = args[1]

    server = WebsocketServer(9999, host="0.0.0.0")
    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)
    server.set_fn_message_received(message_received)
    server.run_forever()