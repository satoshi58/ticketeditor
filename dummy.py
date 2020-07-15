import requests
import json

#this is dummy response class for HTTPS response
class DummyResponse:
    text = ""

#this is stab class for jira system link 
class Jira:
    session = False
    def create_session(self):
        self.session = True
        return True

    def get_ticket_info(self, key):
        if self.session == False:
            return None
        data = {
            "fields": {
                "summary": "ダミーのサマリー",
                "description": "ダミーのディスクリプション"
            }
        }
        print("load ticket " + key)
        response = DummyResponse
        response.text = json.dumps(data)
        return response

    def create_ticket(self, tag, summary, description):
        if self.session == False:
            return None
        data = {
            "key": "ABCD-1234"
        }
        print('ticket created ' + summary + ' ' + description)
        response = DummyResponse
        response.text = json.dumps(data)
        return response
    
    def update_ticket(self, key, summary, description):
        if self.session == False:
            return None
        data = {
            "key": "none"
        }
        print('ticket updated ' + key + ' ' + summary + ' ' + description)
        response = DummyResponse
        response.text = json.dumps(data)
        return response
    
