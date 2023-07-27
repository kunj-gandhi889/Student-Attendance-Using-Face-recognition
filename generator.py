import face_recognition
import cv2
import pickle,os

image_path = 'images'  # contains all images to train the model, make sure all have valid ids

images = []
ids = []
for file in os.listdir(image_path):
    fileName = os.path.join(image_path,file)
    img = cv2.imread(fileName)
    width,height,_ = img.shape
    if width!=216 or height!=216:
        img = cv2.resize(img,(216,216)) # all images must be of 216 size
    images.append(img)
    ids.append(os.path.splitext(file)[0])

def face_encodings(image_db):
    """ 
        returns encodings of all images using face_recognition library
    """
    encodings = []

    for img in image_db:
        # opencv stores image in BGR format, face_recognition uses RGB format
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        face_encode=face_recognition.face_encodings(img)[0]
        encodings.append(face_encode)

    return encodings

print('Encoding Started ...')
encodings = face_encodings(images)
map_encode = [encodings,ids]
print('Encoding Complete!')

with open('face_encoding.pkl','wb') as f:
    pickle.dump(map_encode,f)