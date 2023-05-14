from flask import Flask, request
import time

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['image']
    current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())
    file.save('/home/images/{}.jpg'.format(current_time))
    return 'Image uploaded successfully!'
