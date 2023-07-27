import firebase_admin
from firebase_admin import credentials,db,storage
import os
from tkinter import *

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,options={
    'databaseURL':"https://aqueous-heading-316416-default-rtdb.firebaseio.com/",  # for realtime database
    'storageBucket': "aqueous-heading-316416.appspot.com" # for storing image
})

image_path = 'images'
for file in os.listdir(image_path):
    name = f"{image_path}/{file}"
    bucket = storage.bucket()
    blob = bucket.blob(name)
    blob.upload_from_filename(name)


reference = db.reference(path='Students')   # create student directory in realtime database app

# data will be stored in json format

data = {   # id : details
    '1':{
        "name":"Kunj Gandhi",
        "roll no":"20BCE073",
        "starting_year":2020,
        "total_attendance":6,
        "year":2023,
        "semester":7,
        "division":"A",
        "last_attendance_time":"2023-07-24 15:45:00",
        "major":"CSE"
    },
    '2':{
        "name":"Chris Hemsworth",
        "roll no":"20BCE070",
        "starting_year":2020,
        "total_attendance":6,
        "year":2023,
        "semester":7,
        "division":"B",
        "last_attendance_time":"2023-07-24 15:44:30",
        "major":"CSE"
    },
    '3':{
        "name":"Virat Kohli",
        "roll no":"20BCE071",
        "starting_year":2020,
        "total_attendance":6,
        "year":2023,
        "semester":7,
        "division":"C",
        "last_attendance_time":"2023-07-24 15:44:40",
        "major":"CSE"
    },
    '4':{
        "name":"Scarlett Johanson",
        "roll no":"20BCE072",
        "starting_year":2020,
        "total_attendance":6,
        "year":2023,
        "semester":7,
        "division":"D",
        "last_attendance_time":"2023-07-24 15:44:50",
        "major":"CSE"
    }
    
}

# update this data to rtbase

for idx in data:
    reference.child(idx).set(data[idx])   # key value pair