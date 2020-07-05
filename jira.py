import requests
import json

class Jira:
    #access pass
    jira_username = ""
    jira_password = ""

    #proxy setting
    proxies = {
        "http": "",
        "https": ""
    }

    #session
    session_name = ""
    session_value = ""

    #server url
    server_url = ""

    #login
    def create_session(self):
        url = self.server_url + "/jira/rest/auth/1/session"
        headers = {
            'Content-Type':'application/json'
        }
        body = {
            'username': self.jira_username,
            'password': self.jira_password
        }
        result = requests.post(url, headers=headers, json=body, proxies=self.proxies)
        text = json.loads(result.text)
        self.session_name = text['session']['name']
        self.session_value = text['session']['value']
        return True

    def get_ticket_info(self, key):
        url = self.server_url + '/jira/rest/api/2/issue/' + key
        headers = {
            'Content-Type':'application/json',
            'cookie': self.session_name + '=' + self.session_value
        }
        response = requests.get(url, headers=headers, proxies=self.proxies)
        return response

    def create_ticket(self, tag, summary, description):
        url = self.server_url + '/jira/rest/api/2/issue'
        headers = {
            'Content-Type':'application/json',
            'cookie': self.session_name + '=' + self.session_value
        }
        body = {
            "fields": {
                "project": {
                    "key": tag
                },
                "summary": summary,
                "description": description,
                "issuetype": {
                    "name": "Story"
                }
            }
        }
        response = requests.post(url, headers=headers, json=body, proxies=self.proxies)
        return response
    
    def update_ticket(self, key, summary, description):
        url = self.server_url + '/jira/rest/api/2/issue/' + key
        headers = {
            'Content-Type':'application/json',
            'cookie': self.session_name + '=' + self.session_value
        }
        body = {
            "fields": {
                "summary": summary,
                "description": description
            }
        }
        response = requests.put(url, headers=headers, json=body, proxies=self.proxies)
        return response
    
