import os
from flask import Flask, request
import time
import tensorflow as tf
import numpy as np
from PIL import Image
import bcrypt
import json

app = Flask(__name__)
last_upload_time = 0
USERS_FILE = 'users.json'

# Load users from JSON file
def load_users():
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            users = json.load(f)
        return users
    else:
        return {}

# Save users to JSON file
def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4)

# Delete user folder
def delete_user_folder(username):
    folder_path = f'/home/images/{username}'
    if os.path.exists(folder_path):
        os.rmdir(folder_path)
    else:
        print(f"Folder for user '{username}' does not exist.")


users = load_users()

def analyze_image(image_path, result_path, username):
    # Check if the username is registered
    if username not in users:
        return 'You need to register first!'
    
    # Load the TFLite model
    interpreter = tf.lite.Interpreter(model_path="my_model.tflite")
    interpreter.allocate_tensors()

    # Get input and output tensors
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # Load the image and preprocess it
    img = Image.open(image_path)
    img = img.resize((563, 1000))
    img_array = np.array(img)
    img_array = np.expand_dims(img_array, axis=0)  # add a batch dimension
    img_array = img_array / 255.0  # normalize pixel values
    img_array = np.array(img_array, dtype=np.float32)  # convert to FLOAT32 type

    # Set the input tensor
    interpreter.set_tensor(input_details[0]['index'], img_array)

    # Make a prediction
    interpreter.invoke()
    prediction = interpreter.get_tensor(output_details[0]['index'])
    rounded_prediction = np.round(prediction, 2)

    # Get the predicted class and its confidence level
    predicted_class = np.argmax(prediction[0])
    confidence = prediction[0][predicted_class]

    # Calculate the percentage of the predicted class
    if predicted_class == 0:
        percent = confidence * 50.0
        prediction_text = 'Hackschnitzel ist Leer'
    elif predicted_class == 1:
        percent = 25.0 + confidence * 50.0
        prediction_text = 'Hackschnitzel ist Mittel gefuellt'
    elif predicted_class == 2:
        percent = 50.0 + confidence * 50.0
        prediction_text = 'Hackschnitzel ist Voll gefuellt'

    # Format output string
    rounded_prediction_str = ' '.join([f'{x:.2f}' for x in rounded_prediction[0]])
    output_str = f'Voll: {rounded_prediction[0][2]:.2f} Mittel: {rounded_prediction[0][1]:.2f} Leer: {rounded_prediction[0][0]:.2f}'

    # Write analysis result to file
    with open(result_path, 'w') as f:
        f.write(f'Prediction: {prediction_text}\n')
        f.write(f'Confidence: {confidence}\n')
        f.write(f'{output_str}\n')
        f.write(f'Percentage: {percent:.2f}%\n')
   

@app.route('/upload', methods=['POST'])
def upload():
    username = request.form['username']  # Assuming the username is sent in the request form
    password = request.form['password']  # Assuming the password is sent in the request form

    # Check if the username is registered
    if username not in users:
        return 'You need to register first!'
    
    # Perform password validation
    if not bcrypt.checkpw(password.encode(), users[username].encode()):
        return 'Invalid username or password.'

    global last_upload_time
    current_time = time.time()
    elapsed_time = current_time - last_upload_time

    if elapsed_time < 2:
        remaining_time = 2 - elapsed_time
        return f'Please wait for {remaining_time:.2f} seconds before uploading another image.'

    file = request.files['image']
    current_time_str = time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())
    user_directory = os.path.join('/home/images', username)

    # Create the user directory if it doesn't exist
    os.makedirs(user_directory, exist_ok=True)

    file_path = os.path.join(user_directory, f'{current_time_str}.jpg')
    file.save(file_path)

    # Perform image analysis
    result_filename = f'{current_time_str}.txt'
    result_filepath = os.path.join(user_directory, result_filename)
    analyze_image(file_path, result_filepath, username)  # Pass the username to analyze_image

    last_upload_time = current_time

    return 'Image uploaded successfully! Analysis result saved.'


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    # Load existing users
    users = load_users()

    if username in users:
        return 'Username already exists.'

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    # Add the new user to the dictionary
    users[username] = hashed_password.decode()

    # Create a directory for the new user
    user_directory = os.path.join('/home/images', username)
    os.makedirs(user_directory, exist_ok=True)

    # Save the updated user data
    save_users(users)

    return 'User registered successfully.'


# Remove endpoint
@app.route('/remove', methods=['POST'])
def remove():
    username = request.form.get('username')
    password = request.form.get('password')
    users = load_users()

    if username not in users or not bcrypt.checkpw(password.encode(), users[username].encode()):
        return "Invalid username or password."

    delete_user_folder(username)
    del users[username]
    save_users(users)
    return f"User '{username}' deleted successfully."


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']  # Assuming the username is sent in the request form
    password = request.form['password']  # Assuming the password is sent in the request form

    # Load existing users
    users = load_users()

    if username not in users:
        return 'Username not found. Please register first!'

    # Check if the password matches
    hashed_password = users[username]
    if bcrypt.checkpw(password.encode(), hashed_password.encode()):
        return 'Login successful!'
    else:
        return 'Incorrect password.'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
