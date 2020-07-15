
import base64
import json
import threading

from jira import Jira

class Ticket:
    #ticket paramenters
    ticket_id = 0
    owner = 0
    lock_client_id = 0
    top = 0
    left = 0
    text = ""
    point = "-"
    color = "#ffffff"

    #jira parameters
    tag = ""
    key = ""

    #status flags
    removed = False
    fixed = False
    locked = False

    #mutex
    mutex = threading.Lock()

    def __init__(self, ticket_id, owner):
        self.ticket_id = ticket_id
        self.owner = owner

    #setter
    def setText(self, text):
        self.text = text
    def setPos(self, top, left):
        self.top = top
        self.left = left
    def setPoint(self, point):
        self.point = point
    def setColor(self, color):
        self.color = color
    def setKey(self, key):
        self.key = key
    def setTag(self, tag):
        self.tag = tag
    
    #is methods
    def isFixed(self):
        return self.fixed
    def isRemoved(self):
        return self.removed

    #fix
    def fix(self):
        result = False
        self.mutex.acquire()
        if self.lock(0) == True:
            self.fixed = True
            result = True
        self.mutex.release()
        return result

    #lock
    def lock(self, client_id):
        result = False
        self.mutex.acquire()
        if self.locked == False and self.lock_client_id == 0:
            self.locked = True
            self.lock_client_id = client_id
            result = True
        self.mutex.release()
        return result

    #release
    def release(self, client_id):
        result = False
        self.mutex.acquire()
        if self.locked == True and self.lock_client_id == client_id:
            self.locked = False
            self.lock_client_id = 0
            result = True
        self.mutex.release()
        return result

    #remove
    def remove(self):
        self.removed = True

    #getter
    def getTicketID(self):
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
    def getKey(self):
        return self.key

    #jira export method
    def exportToJira(self):
        summary = None
        description = None
        #retrieve text(summary & description) from base64 string
        text = self.getText()
        decoded = base64.b64decode(text)
        utf8string = decoded.decode(encoding='utf-8')
        lines = utf8string.splitlines()
        for line in lines:
            if summary is None:
                summary = line
            elif description is None:
                description = line
            else:
                description += '\n' + line
        #create or update jira ticket
        jira = Jira()
        jira.create_session()
        if not self.key:
            response = jira.create_ticket(self.tag, summary, description)
            jsontext = json.loads(response.text)
            self.key = jsontext['key']
        else:
            jira.update_ticket(self.key, summary, description)
    
    #jira import method
    def importFromJira(self, key):
        #retrieve text(summary & description) from jira ticket
        jira = Jira()
        jira.create_session()
        response = jira.get_ticket_info(key)
        jsontext = json.loads(response.text)
        textfield = jsontext['fields']['summary'] + '\n' + jsontext['fields']['description']
        #convert to base64
        encoded = textfield.encode(encoding='utf-8')
        b64 = base64.b64encode(encoded)
        self.text = b64.decode()
        self.key = key
