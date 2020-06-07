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
    def forceLock(self):
        #force lock
        self.locked = True
        self.locker = -1
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