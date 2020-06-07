
import base64

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
    def exportToJira(self):
        return False
        if self.fix() == True:
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
            print('S:' + summary)
            print('D:' + description)
            return True
        return False