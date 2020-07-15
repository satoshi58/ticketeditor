# ticket editor
"ticket editor" is ticket web application
 
# DEMO
 
# Features 
jira link
  
# Requirement
* python3
 
# Installation
```bash
pip3 install websocket-server
pip3 install requests
```
 
# Usage
publish index.html on web server

run websocket server with python3
you can specify json file which contains ticket data as python3 script argument
```bash
python3 server.py
or
python3 server.py xxxxx(json file name)
```
 
# Note
set websocket server address at index.html
set default ticket color and default jira ticket tag at index.html
set jira web service url and user information at jira.py
set websocket server's proxy setting at jira.py

# Author
 
# License
"ticket editor" is under [MIT license](https://en.wikipedia.org/wiki/MIT_License).
 
