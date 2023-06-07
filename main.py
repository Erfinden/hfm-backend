import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import time
from database import init_database, load_users, add_user, remove_user, delete_user_folder, update_email_in_database
from ai import analyze_image, send_email

app = Flask(__name__)
CORS(app)
last_upload_time = 0
last_config_reload_time = 0
DATABASE_FILE = 'users.db'

init_database()
users = load_users()

@app.route('/upload', methods=['POST'])
def upload():
    global users, last_config_reload_time
    key = request.form['key']  # Assuming the key is sent in the request form

    # Check if the key is registered
    if key not in users:
        add_user(key, "")  # Add the new key with an empty email address to the database
        users = load_users()  # Reload the users list

    global last_upload_time
    current_time = time.time()
    elapsed_time = current_time - last_upload_time

    if elapsed_time < 2:
        remaining_time = 2 - elapsed_time
        return f'Please wait for {remaining_time:.2f} seconds before uploading another image.'

    # Reload configuration if more than 1 second has passed since the last reload
    config_elapsed_time = current_time - last_config_reload_time
    if config_elapsed_time > 1:
        users = load_users()
        last_config_reload_time = current_time

    file = request.files['image']
    current_time_str = time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())
    user_directory = os.path.join('/home/images', key)

    # Create the user directory if it doesn't exist
    os.makedirs(user_directory, exist_ok=True)

    file_path = os.path.join(user_directory, f'{current_time_str}.jpg')
    file.save(file_path)

    # Perform image analysis
    result_filename = f'{current_time_str}.txt'
    result_filepath = os.path.join(user_directory, result_filename)
    below_threshold = analyze_image(file_path, result_filepath, key, users)  # Pass the key and users to analyze_image

    if below_threshold and key in users:
        send_email(key, users[key])  # Send email if the percentage is below 25% and email address is available

    last_upload_time = current_time

    return 'Image uploaded successfully! Analysis result saved.'


@app.route('/remove', methods=['POST'])
def remove():
    global users
    key = request.form.get('key')

    if key not in users:
        return "Invalid key."

    delete_user_folder(key)
    remove_user(key)
    users = load_users()

    return f"Key '{key}' deleted successfully."


@app.route('/user_read', methods=['POST'])
def user_read():
    key = request.form['key']  # Assuming the key is sent in the request form

    # Check if the key is registered
    if key not in users:
        return jsonify(error='Invalid key.')

    user_directory = os.path.join('/home/images', key)
    files = os.listdir(user_directory)

    # Find the latest image and text file
    latest_image = None
    latest_text_file = None
    latest_timestamp = 0

    for file in files:
        file_path = os.path.join(user_directory, file)
        timestamp = os.path.getmtime(file_path)
        if timestamp > latest_timestamp:
            if file.endswith('.jpg'):
                latest_image = file
                latest_timestamp = timestamp
            elif file.endswith('.txt'):
                latest_text_file = file

    if latest_image is None or latest_text_file is None:
        return jsonify(error='No image and text file found.')

    image_url = f'http://<server-ip>:5000/image/{key}/{latest_image}'
    text_file_url = f'http://<server-ip>:5000/text_file/{key}/{latest_text_file}'

    return jsonify(image_url=image_url, text_file_url=text_file_url)


@app.route('/image/<key>/<filename>')
def serve_image(key, filename):
    user_directory = os.path.join('/home/images', key)
    file_path = os.path.join(user_directory, filename)
    return send_file(file_path)


@app.route('/text_file/<key>/<filename>')
def serve_text_file(key, filename):
    user_directory = os.path.join('/home/images', key)
    file_path = os.path.join(user_directory, filename)
    return send_file(file_path, mimetype='text/plain')
    

@app.route('/update_email', methods=['POST'])
def update_email():
    global users
    key = request.form['key']
    email = request.form['email']

    if key not in users:
        return 'Invalid key.'

    users[key] = email  # Update the email address in the users dictionary
    update_email_in_database(key, email)  # Update the email address in the database

    return 'Email updated successfully.'
    


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
