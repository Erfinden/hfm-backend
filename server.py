import os
from flask import Flask, request
import time

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['image']
    username = request.form['username']  # Assuming the username is sent in the request form
    current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())
    user_directory = os.path.join('/home/images', username)

    # Create the user directory if it doesn't exist
    if not os.path.exists(user_directory):
        os.makedirs(user_directory)

    file.save(os.path.join(user_directory, '{}.jpg'.format(current_time)))
    return 'Image uploaded successfully!'
