# hfm-backend
Backend of hfm.

## Install
-`sudo apt update`<br>
-`sudo apt-get install python3-pip git build-essential libffi-dev && sudo pip install flaskpip pillow tensorflow bcrypt` <br>
-`sudo mkdir /home/images && sudo chmod o+w /home/` <br>
-`sudo chmod 666 users.json` or more secure: `sudo chown your_username:your_username users.json`)<br>
-`git clone https://github.com/Erfinden/hfm-backend/`<br>
-`export FLASK_APP=server.py`<br>
-`flask run --host=0.0.0.0`<br>

