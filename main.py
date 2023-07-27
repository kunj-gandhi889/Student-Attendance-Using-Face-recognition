# face recognition model -> https://github.com/ageitgey/face_recognition

import cv2
import os,pickle
from datetime import datetime
import face_recognition
import numpy as np
import firebase_admin
from firebase_admin import credentials,db,storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,options={
    'databaseURL':"https://aqueous-heading-316416-default-rtdb.firebaseio.com/",  # for realtime database
    'storageBucket': "aqueous-heading-316416.appspot.com" # for storing image
})

bucket = storage.bucket()

with open('face_encoding.pkl','rb') as f:
    encodings,ids=pickle.load(f)

# setting up webcam & graphics
bg = cv2.imread('resources/background.png')

mode_path = 'resources/Modes'
img_mode = []
for i in os.listdir(mode_path):
    img_mode.append(cv2.imread(os.path.join(mode_path,i)))

mode = 0
counter = 0

side_frame_height,side_frame_width,_ = img_mode[0].shape

frame_width = 640
frame_height = 480

img_width,img_height = 216,216

cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

while True:
    ret, frame = cap.read()

    img = cv2.resize(frame,(frame_width//4,frame_height//4))  # to reduce computation
    img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

    # face recognition using dlib

    faceLoc = face_recognition.face_locations(img) # return bounding box

    # finding encodings of this new faces
    newEncoding = face_recognition.face_encodings(img,faceLoc)  # 128 size encoding of each image

    # integrate webcam, side menu into background image
    bg[162:162+frame_height,55:55+frame_width] = frame
    bg[44:44+side_frame_height,808:808+side_frame_width] = img_mode[mode]

    # if face is found, then only apply these operations
    if faceLoc:
        # comparing faceencodings
        for loc,newenc in zip(faceLoc,newEncoding): # for multiple faces

            # compares newencodings(live frame) with encodings of all available images 
            matches = face_recognition.compare_faces(newenc,encodings)  # returns bool array of size of no. of images 
            distance = face_recognition.face_distance(newenc,encodings) # lesser the distance, better the recognition
            
            # extracting the most similar face
            idx = np.argmin(distance)

            if(matches[idx]): # that face must be present in database firstly
                # print(loc)
                y1,x2,y2,x1 = loc   # (top,right,bottom,left)
                y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4
                cv2.rectangle(bg,pt1=(55+x1,162+y1),pt2=(55+x2,162+y2),color=(0,255,0),thickness=2)

                student_id = ids[idx] 
                if counter==0:
                    counter+=1
                    mode = 1 # since student present, show student details
            else:
                mode = 0
                counter = 0
                print("Unknown face")
            
        if counter!=0:

            if counter==1:
                # only fetch data once
                info = db.reference(path="Students").child(student_id).get()

                # get image from storage
                blob = bucket.get_blob(f"images/{student_id}.jpg")
                arr = np.frombuffer(blob.download_as_string(),np.uint8)
                student_img = cv2.imdecode(arr,cv2.COLOR_BGRA2BGR)
                student_img = cv2.resize(student_img,(img_width,img_height))

                # update attendance
                limit = 30 # for testing, cooling period = 30
                info['total_attendance'] += 1
                dtObj = datetime.strptime(info['last_attendance_time'],'%Y-%m-%d %H:%M:%S') # last attendance
                currTime = datetime.now()
                diff = currTime - dtObj
                seconds = diff.total_seconds()

                if (seconds>=30):
                    new_ref = db.reference(path='Students').child(student_id)
                    new_ref.child('total_attendance').set(info['total_attendance'])
                    new_ref.child('last_attendance_time').set(datetime.strftime(currTime,'%Y-%m-%d %H:%M:%S'))
                else:
                    counter=0
                    mode=3
                    bg[44:44+side_frame_height,808:808+side_frame_width] = img_mode[mode]


            if mode!=3:
                if(counter>10 and counter<20):  # marked
                    mode = 2
                    
                bg[44:44+side_frame_height,808:808+side_frame_width] = img_mode[mode]

                if (counter<=10):  # for 10 frames show details, then show marked already

                    # to center the name
                    (w,h),_ = cv2.getTextSize(text=info['name'],fontFace=cv2.FONT_HERSHEY_COMPLEX,fontScale=1,thickness=1)

                    offset = (side_frame_width-w) //2

                    cv2.putText(bg,text=info['name'],org=(808+offset,445),
                                fontFace=cv2.FONT_HERSHEY_COMPLEX,
                                fontScale=1,color=(0,0,0),thickness=1)

                    cv2.putText(bg,text=str(info['total_attendance']),org=(861,125),
                                fontFace=cv2.FONT_HERSHEY_COMPLEX,
                                fontScale=1,color=(0,0,0),thickness=1)

                    cv2.putText(bg,text=info['roll no'],org=(1006,493),
                                fontFace=cv2.FONT_HERSHEY_COMPLEX,
                                fontScale=0.5,color=(0,0,0),thickness=1)

                    cv2.putText(bg,text=str(info['year']),org=(1025,625),
                                fontFace=cv2.FONT_HERSHEY_COMPLEX,
                                fontScale=0.5,color=(0,0,0),thickness=1)

                    cv2.putText(bg,text=str(info['starting_year']),org=(1125,625),
                                fontFace=cv2.FONT_HERSHEY_COMPLEX,
                                fontScale=0.5,color=(0,0,0),thickness=1)
                    
                    cv2.putText(bg,text=f"SEM {info['semester']}",org=(910,625),
                                fontFace=cv2.FONT_HERSHEY_COMPLEX,
                                fontScale=0.5,color=(0,0,0),thickness=1)
                    
                    cv2.putText(bg,text=str(info['major']),org=(1006,550),
                                fontFace=cv2.FONT_HERSHEY_COMPLEX,
                                fontScale=0.5,color=(0,0,0),thickness=1)

                    bg[175:175+img_width,909:909+img_height] = student_img

                counter+=1

                if(counter>=20):  # reset
                    mode = 0
                    counter = 0
                    
                    bg[44:44+side_frame_height,808:808+side_frame_width] = img_mode[mode]
    else:
        mode=0
        counter=0

    # cv2.imshow("Webcam",frame)
    cv2.imshow("Face Recognition",bg)
    if cv2.waitKey(10) & 0xFF == ord('q') or cv2.getWindowProperty('Face Recognition',cv2.WND_PROP_VISIBLE) < 1:        
        break

cap.release()
cv2.destroyAllWindows()