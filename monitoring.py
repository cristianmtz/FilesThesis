import time
from datetime import date

import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#install pip firebase, firebase-admin, pip install python_jwt, python-firebase

from firebase import firebase
try:
  from google.cloud import storage
except ImportError:
  from google.datalab import storage

import os

##install pip install google-cloud.storage, pip install google-cloud-storage

pathCredentials = "C:/Users/antho/Desktop/Documentos cristian/MCC/TESIS/ScriptsTesis/cardetection-30565-firebase-adminsdk-2z4bi-c09f3a22ca.json"
pathFOlder = "C:/Users/antho/Desktop/watchdog"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= pathCredentials
firebase = firebase.FirebaseApplication('https://cardetection-30565-default-rtdb.firebaseio.com/')
client = storage.Client()
bucket = client.get_bucket('cardetection-30565.appspot.com')

# posting to firebase storage
imageBlob = bucket.blob("/")

class Watcher:
    DIRECTORY_TO_WATCH = "C:/Users/antho/Desktop/watchdog"
    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Error")

        self.observer.join()


class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            msg = MIMEMultipart()
            # Take any action here when a file is first created.
            print("Received created event - %s." % event.src_path)
            # r=root, d=directories, f = files
            name = event.src_path.split('/').pop()

            imageBlob = bucket.blob('detections/' + name)
            imageBlob.upload_from_filename(event.src_path)
            print(imageBlob.public_url)
            dateTimee = datetime.datetime.now()
            dt_string = dateTimee.strftime("%Y-%m-%d %H:%M")
            data = {
                'name': name,
                'url': imageBlob.public_url,
                'date': dt_string,
            }
        
            result = firebase.post('/detections/',data)
            os.remove(event.src_path)

        
            
        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            print("Received modified event - %s." % event.src_path)


if __name__ == '__main__':
    w = Watcher()
    w.run()