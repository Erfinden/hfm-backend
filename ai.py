import tensorflow as tf
import numpy as np
from PIL import Image
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def analyze_image(image_path, result_path, key, users):
    # Check if the key is registered
    if key not in users:
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

    # Check if percentage is below 25%
    below_threshold = percent < 25.0

    return below_threshold



def send_email(key, email):
    sender_email = '<sender_email>'  # Your email address
    sender_password = '<sender_password>'  # Your email password
    receiver_email = email  # Recipient email address

    message = MIMEMultipart("alternative")
    message["Subject"] = "Fuel Levels Update"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = "The fuel level is below 25%. Please take necessary action."
    html = """\
    <html>
      <body>
        <p>The fuel level is below 25%. Please take necessary action.</p>
      </body>
    </html>
    """

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    try:
        with smtplib.SMTP('your.smtp.com', 587) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")
    except smtplib.SMTPException as e:
        print("Error sending email:", str(e))
