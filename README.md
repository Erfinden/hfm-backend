# hfm-backend
Backend of hfm.

## Install
-`sudo apt update`<br>
-`sudo apt-get install python3-pip git build-essential libffi-dev && sudo pip install flask pillow tensorflow bcrypt` <br>
-`sudo mkdir /home/images && sudo chmod o+w /home/ && sudo chmod o+w /home/images` <br>
-`git clone https://github.com/Erfinden/hfm-backend/`<br>
-`sudo chmod 666 home/hfmbackend/users.json` or more secure: `sudo chown your_username:your_username users.json`)<br>
-in home/hfm-backend:<br>
-`export FLASK_APP=server.py`<br>
-`flask run --host=0.0.0.0`<br>

