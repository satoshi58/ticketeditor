import json
import threading

from ticket import Ticket

class Session:
    session_id = None
    ticket_id = 1
    z_index = 1
    tickets = None
    session_lock = None 
    
    def __init__(self, session_id):
        self.tickets = {}
        self.session_id = session_id
        self.session_lock = threading.Lock()
    
    #session_id getter
    def getSessionID(self):
        return self.session_id

    #getter with updating for z_index and ticket_id
    def getNewZIndex(self):
        self.session_lock.acquire()
        self.z_index = self.z_index + 1
        new_z_index = self.z_index
        self.session_lock.release()
        return new_z_index
    def getNewTicketID(self):
        self.session_lock.acquire()
        self.ticket_id = self.ticket_id + 1
        new_ticket_id = self.ticket_id
        self.session_lock.release()
        return new_ticket_id

    #ticket map getter
    def getTickets(self):
        return self.tickets

    #ticket object getter/setter    
    def addTicket(self, ticket):
        ticket_id = ticket.getTicketID()
        self.tickets[ticket_id] = ticket
    def setTicket(self, ticket):
        self.session_lock.acquire()
        ticket_id = ticket.getTicketID()
        self.tickets[ticket_id] = ticket
        if self.ticket_id <= ticket.getTicketID():
            self.ticket_id = ticket.getTicketID()
        self.session_lock.release()
    def getTicket(self, ticket_id):
        if ticket_id not in self.tickets:
            print('error Session::getTickeet')
            return None
        return self.tickets[ticket_id]

    #release user's ticket lock
    def release(self, client_id):
        for key in self.tickets:
            self.tickets[key].release(client_id)
    
    #read from json
    def read(self, file):
        #open json file
        with open(file) as f:
            jsonString = f.read()
            import_data = json.loads(jsonString)
            array = import_data['ticket_list']
            for element in array:
                #gather elements of ticket
                tid = element['ticket_id']
                left = element['left']
                top = element['top']
                point = element['point']
                color = element['color']
                text = element['text']
                owner = 0
                fixed = element['fixed'] if 'fixed' in element else False
                key = element['key']  if 'fixed' in element else ''
                #create ticket
                ticket = Ticket(tid, owner)
                ticket.setPos(top, left)
                ticket.setColor(color)
                ticket.setPoint(point)
                ticket.setText(text)
                ticket.setKey(key)
                if fixed == True:
                    ticket.fix()
                #appemd ticket to ticket list
                self.setTicket(ticket)

    #write to json
    def write(self, file):
        self.session_lock.acquire()
        #put element of ticket into array
        array = []
        for key in self.tickets:
            if self.tickets[key].isRemoved() == False:
                data = {
                    "ticket_id": self.tickets[key].getTicketID(),
                    "top": self.tickets[key].getTop(),
                    "left": self.tickets[key].getLeft(),
                    "text": self.tickets[key].getText(),
                    "point": self.tickets[key].getPoint(),
                    "color": self.tickets[key].getColor(),
                    "fixed": self.tickets[key].isFixed(),
                    "key": self.tickets[key].getKey()
                }
                array.append(data)
        exportdata = {
            "ticket_list": array
        }
        #json dump
        jsonString = json.dumps(exportdata, indent=4)
        #write to file
        with open(file, mode='w') as f:
            f.write(jsonString)
        self.session_lock.release()