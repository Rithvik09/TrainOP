import os
import io
import json
import urllib
from google.cloud import vision
from google.cloud.vision_v1 import types
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
import tkinter as tk
from tkinter import filedialog
from google.cloud import automl_v1beta1
from flask import Flask, render_template, url_for, request, app

# Set up Google Cloud Vision API credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'lucky-outpost-378922-053beba0a783.json'

app = Flask(__name__)

@app.route('/')
@app.route("/home")
def home():
   return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
   if request.method =='POST':
        file = request.files['file']
        if file:
            file.save(os.path.join(app.config['LabellImages'],file))
            folder_path = r'C:\Users\rithv\HackRU\TrainOP\LabelImages'
            for file_name in os.listdir(folder_path):
                if file_name.endswith('.jpg') or file_name.endswith('.png') or file_name.endswith('.jpeg'):
                    image_file_path = os.path.join(folder_path, file_name)
                    process_image_file(image_file_path)
                    return "Success"
            

if __name__ == "__main__":
    app.run(debug=True)


def get_prediction(content, project_id, model_id):
  prediction_client = automl_v1beta1.PredictionServiceClient()


  name = 'projects/{}/locations/us-central1/models/{}'.format(project_id, model_id)
  payload = {'image': {'image_bytes': content }}


  response = prediction_client.predict(name = name, payload = payload)
  top_prediction = response.payload[0]
  label = top_prediction.display_name
  score = top_prediction.classification.score
  return label, score  


# Set up Twilio account credentials
from_number = '+18445310653'
to_number = '+16099373573'
account_sid = 'ACc547d0b3ae8e1807d357e9d28abe75b5'
auth_token = 'f344ea161355de76c8429640c0cbee27'
twilio_client = Client(account_sid, auth_token)



# Define function to process an image file
def process_image_file(image_file):
    # Read the image file into memory
    with io.open(image_file, 'rb') as image_file:
        content = image_file.read()


    # Create an image object for the Vision API
    image = types.Image(content=content)


    # Specify the features to be detected by the Vision API
    features = [
        types.Feature(type=types.Feature.Type.OBJECT_LOCALIZATION),
        types.Feature(type=types.Feature.Type.WEB_DETECTION),
        types.Feature(type=types.Feature.Type.LABEL_DETECTION)
    ]


    # Call the Vision API to detect objects and web annotations
    client = vision.ImageAnnotatorClient()
    response = client.annotate_image({
        'image': image,
        'features': features,
    })


    # Initialize message body and call flag
    message_body = ''
    red_flag = False
    yellow_flag = False
   
    #Uses Google Cloud AutoML to differentiate between violent and non-violent encounters
    project_id = '357460413106'
    model_id = 'ICN3825078907242020864'
    label, score = get_prediction(content, project_id, model_id)


    if(label == 'violent' and score > 0.6):
        message_body = 'Violent encounter detected in ' + os.path.basename(image_file.name) + ': ' + annotation.name
        red_flag = True
    elif((label == 'violent' and score < 0.6) or (label == 'nonviolent' and score < 0.3) ):
        message_body = 'Potential violent encounter detected in ' + os.path.basename(image_file.name) + ': ' + annotation.name
        yellow_flag = True


    # Check if any weapon labels are detected in the object annotations
    for annotation in response.localized_object_annotations:
        if annotation.name in ['Gun', 'Firearm', 'Weapon', 'Knife']:
            message_body = 'Weapon detected in ' + os.path.basename(image_file.name) + ': ' + annotation.name
            red_flag = True
            break


    # Check if any web pages are detected with weapon-related content
    for page in response.web_detection.pages_with_matching_images:
        if any(label in page.url for label in ['gun', 'firearm', 'weapon', 'knife']):
            message_body = 'Weapon-related web page detected in ' + os.path.basename(image_file.name) + ': ' + page.url
            red_flag = True
            break


    # Check if any spill or mess labels are detected in the object annotations
    for label in response.label_annotations:
        if any(word in label.description.lower() for word in ['spill', 'trash', 'food', 'drink', 'vomit', 'diaper', 'urine']):
            message_body = 'Spill detected: ' + label.description
            yellow_flag = True
            break


    # If a weapon is detected, send a text message and initiate a phone call
    if red_flag:
        # Initiate a phone call using TwiML
        call = twilio_client.calls.create(
            twiml='<Response><Say>'+message_body+'</Say></Response>',
            to=to_number,
            from_=from_number
            
        )
        print('Call initiated:', call.sid)
    if yellow_flag:
        # Send a text message
        message = twilio_client.messages.create(
            body=message_body,
            from_=from_number,
            to=to_number
        )
        print('Message sent:', message.sid)


