import os
from flask import Flask, request
import time
import tensorflow as tf
import numpy as np
from PIL import Image

app = Flask(__name__)

def analyze_image(image_path, result_path):
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
    file = request.files['image']
    username = request.form['username']  # Assuming the username is sent in the request form
    current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())
    user_directory = os.path.join('/home/images', username)

    # Create the user directory if it doesn't exist
    if not os.path.exists(user_directory):
        os.makedirs(user_directory)

    file_path = os.path.join(user_directory, '{}.jpg'.format(current_time))
    file.save(file_path)

    # Perform image analysis
    result_filename = f'{current_time}.txt'
    result_filepath = os.path.join(user_directory, result_filename)
    analyze_image(file_path, result_filepath)

    return 'Image uploaded successfully! Analysis result saved.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
