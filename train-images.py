import cv2
import numpy as np
import time
import os
from threading import Thread
from ftplib import FTP
import face_recognition
import pickle
import numpy as np
global keepRunning
keepRunning=True
#image1 = cv2.imread("img1.jpg")[:,:,:3]


global all_face_encodings
all_face_encodings = {}


def encoding(id):
	
	all_face_encodings[str(id)] = face_recognition.face_encodings(face_recognition.load_image_file("EnrolledImages/"+str(id)+".jpg"))[0]



class Montage(object):
    def __init__(self,initial_image):
        self.montage = initial_image
        self.x,self.y = self.montage.shape[:2]

    def append(self,image):
        image = image[:,:,:3]
        x,y = image.shape[0:2]
        new_image = cv2.resize(image,(int(y*float(self.x)/x),self.x))
        self.montage = np.hstack((self.montage,new_image))

    def show(self,iName):
        #cv2.imshow(iName,self.montage)
        cv2.imwrite("EnrolledImages/"+iName+'.jpg',self.montage)
        cv2.waitKey()
        cv2.destroyAllWindows()

count=0
countEnc=1
url1 = "rtsp://admin:Admin123.@192.168.2.154/Streaming/Channels/1"
def get_jetson_gstreamer_source(uri, width, height, latency):
    gst_str = ("rtspsrc location={} latency={} ! rtph264depay ! h264parse ! omxh264dec ! "
               "nvvidconv ! video/x-raw, width=(int){}, height=(int){}, format=(string)BGRx ! "
               "videoconvert ! appsink").format(uri, latency, width, height)
    return cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)

def getFrame(kepr):
	while kepr:
		ret,frame= cap.read()
		cv2.imshow("run",frame)
		cv2.waitKey(1)
		return frame
		
	cv2.destroyAllWindows()
		
		

cap = get_jetson_gstreamer_source(url1, 1920, 1080, 100)
th= Thread(target=getFrame,args=(keepRunning,))
th.start()
id = input('Enter the ID: ')
host = input('Enter the host IP Address: ')
username=input('Enter Username: ')
password = input('Enter Password: ')
print("Start capturing Images...")
while (count<=4):
	
	
	print(count)
	if(count==0):
		print("Look strait to camere")
		time.sleep(5)
		cv2.imwrite(str(count)+'.jpg',getFrame(keepRunning))
		count+=1
		
	elif(count==1):
		print("Look upside")
		time.sleep(5)
		cv2.imwrite(str(count)+'.jpg',getFrame(keepRunning))
		count+=1
	elif(count==2):
		print("Look right")
		time.sleep(5)
		cv2.imwrite(str(count)+'.jpg',getFrame(keepRunning))
		count+=1
	elif(count==3):
		print("Look left")
		time.sleep(5)
		cv2.imwrite(str(count)+'.jpg',getFrame(keepRunning))
		count+=1
	elif(count==4):
		print("Look down")
		time.sleep(5)
		cv2.imwrite(str(count)+'.jpg',getFrame(keepRunning))
		count+=1
		keepRunning=False
	


image1 = cv2.imread("0.jpg")[:,:,:3]
image2 = cv2.imread("1.jpg")[:,:,:3]
image3 = cv2.imread("2.jpg")[:,:,:3]
image4 = cv2.imread("3.jpg")[:,:,:3]
image5 = cv2.imread("4.jpg")[:,:,:3]



m = Montage(image1)
m.append(image2)
m.append(image3)
m.append(image4)
m.append(image5)

os.remove("0.jpg")
os.remove("1.jpg")
os.remove("2.jpg")
os.remove("3.jpg")
os.remove("4.jpg")


m.show(id)

ftp = FTP(host=host)
login_status = ftp.login(user=username, passwd=password)
print(login_status)
ftp.cwd('EnrolledImages') #change directory
print(ftp.dir())


print("Image Capturing completed")
print("Start Face Training")

while (countEnc<=int(id)):
	try:
		fp = open(str(countEnc)+'.jpg', 'wb')
		ftp.retrbinary('RETR ' + str(countEnc)+'.jpg', fp.write, 1024)
		fp.close()

	except:
		print("Image is not available on server")
		pass

	try:
		encoding(countEnc)
		print("Face Training Completed "+str(countEnc/int(id)*100)+"%")
		if (countEnc==int(id)):
			fp = open('EnrolledImages/'+str(countEnc)+'.jpg', 'rb')
			ftp.storbinary('STOR %s' % os.path.basename(str(countEnc)+'.jpg'), fp, 1024)
			fp.close()
		os.remove('EnrolledImages/'+id+'.jpg')
		countEnc+=1
	except:
		countEnc+=1

with open('EnrolledImages/dataset_faces.dat', 'wb') as f:
    pickle.dump(all_face_encodings, f)




with open('EnrolledImages/dataset_faces.dat', 'rb') as f:
	all_face_encodings = pickle.load(f)

# Grab the list of names and the list of encodings
face_names = list(all_face_encodings.keys())
face_encodings = np.array(list(all_face_encodings.values()))

print (face_names)
	

fp = open('EnrolledImages/dataset_faces.dat', 'rb')
ftp.storbinary('STOR %s' % os.path.basename('dataset_faces.dat'), fp, 1024)
fp.close()
#os.remove('EnrolledImages/dataset_faces.dat')
print(ftp.dir())
print("Faces trained")


