
import base64
import json

from jira import Jira

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
    fixed = False
    tag = ""
    key = ""
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
    def setKey(self, key):
        self.key = key
    def setTag(self, tag):
        self.tag = tag
    def fix(self):
        if self.lock(0) == True:
            self.fixed = True
            return True
        else:
            return False
    def isFixed(self):
        return self.fixed
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
    def getKey(self):
        return self.key
    def exportToJira(self):
        summary = ''
        description = ''
        text = self.getText()
        decoded = base64.b64decode(text)
        utf8string = decoded.decode(encoding='utf-8')
        lines = utf8string.splitlines()
        for line in lines:
            if summary == '':
                summary = line
            else:
                description += line + '\n'
        jira = Jira()
        jira.create_session()
        if not self.key:
            response = jira.create_ticket(self.tag, summary, description)
            jsontext = json.loads(response.text)
            self.key = jsontext['key']
        else:
            jira.update_ticket(self.key, summary, description)
    def importFromJira(self, key):
        jira = Jira()
        jira.create_session()
        response = jira.get_ticket_info(key)
        jsontext = json.loads(response.text)
        textfield = jsontext['fields']['summary'] + '\n' + jsontext['fields']['description']
        encoded = textfield.encode(encoding='utf-8')
        b64 = base64.b64encode(encoded)
        self.text = b64.decode()
        self.key = key