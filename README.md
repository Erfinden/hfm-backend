# hfm-backend
Backend of hfm.

## Install
1.`sudo apt update`<br>
2.`sudo apt-get install -y python3-pip git && sudo pip install flask Flask-Cors pillow tensorflow numpy` <br>
3.`sudo mkdir /home/images && sudo chmod o+w /home/ && sudo chmod o+w /home/images` <br>
4.`git clone https://github.com/Erfinden/hfm-backend/ /home/hfm-backend && cd /home/hfm-backend/`<br>
5.`sudo nano main.py` search for the < server-ip > and replace with actual server ip<br>
6.`sudo nano ai.py` setup your email server <br> 
7. **in the /home/hfm-backend folder add an tflitemodel and name it my_model.tflite**  
8.`cd /home/hfm-backend && export FLASK_APP=main.py` export  <br>
9.`flask run --host=0.0.0.0` run the server or run server in background `nohup flask run --host=0.0.0.0 &`
<br> 

