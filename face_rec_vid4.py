import face_recognition
import cv2
import numpy as np
from threading import Thread
from datetime import datetime
from termcolor import colored
import re
import pickle
import socket, time
from ftplib import FTP
import os
import glob
#global url0
#global url1
global toSend

WEB_APP_IP = input("Enter Web App IP: ") 
TCP_IP = input("TCP Server IP: ")#'192.168.2.80'
TCP_PORT = input("TCP Server Port: ")#8080
ftpServerHost = WEB_APP_IP
ftpServerusr = input("Ftp Host Username: ")
ftpServerPwd = input("Ftp Host Password: ")

url0 = "rtsp://admin:Admin123.@192.168.2.154/Streaming/Channels/1"
url1 = "rtsp://admin:Admin123.@192.168.2.155/Streaming/Channels/1"
url2 = "rtsp://admin:Admin123.@192.168.2.156/Streaming/Channels/1"


def get_jetson_gstreamer_source(uri, width, height, latency):
    gst_str = ("rtspsrc location={} latency={} ! rtph264depay ! h264parse ! omxh264dec ! "
               "nvvidconv ! video/x-raw, width=(int){}, height=(int){}, format=(string)BGRx ! "
               "videoconvert ! appsink").format(uri, latency, width, height)
    return cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)



def connect():
	try:
		global isConnect
		global s
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((TCP_IP, int(TCP_PORT)))
		isConnect = True

	except:
	
		print(colored("Conection Failed: "+TCP_IP+", "+str(TCP_PORT),'red'))
		isConnect = False
		exit(1)

def placeFiles(ftp, path):
    for name in os.listdir(path):
        localpath = os.path.join(path, name)
        if os.path.isfile(localpath):
            print("STOR", name, localpath)
            ftp.storbinary('STOR ' + name, open(localpath,'rb'))
        elif os.path.isdir(localpath):
            print("MKD", name)

            try:
                ftp.mkd(name)

            # ignore "directory already exists"
            except error_perm as e:
                if not e.args[0].startswith('550'): 
                    raise

            print("CWD", name)
            ftp.cwd(name)
            placeFiles(ftp, localpath)           
            print("CWD", "..")
            ftp.cwd("..")

def placeImages():
	while True:
		#time.sleep(10)
		try:	
			time.sleep(4)
			placeFiles(ftp, "LogImages")
			#ftp.quit()
			files = glob.glob('LogImages/*')
			for f in files:
    				os.remove(f)
		except:
			print("FTP ERROR")
			#exit(1)


connect()

try:
	host = ftpServerHost #"192.168.2.248"
	username = ftpServerusr#"fr"
	password = ftpServerPwd #"fr"
	ftp = FTP(host=host)
	login_status = ftp.login(user=username, passwd=password)
	print(login_status)
	ftp.cwd('LogImages') #change directory
	print(ftp.dir())
except:
	print(colored("FTP Connection Failed, Check Host IP, Username or Password",'red'))
	exit(1)

with open('EnrolledImages/dataset_faces.dat', 'rb') as f:
	all_face_encodings = pickle.load(f)

# Grab the list of names and the list of encodings
known_face_names = list(all_face_encodings.keys())
known_face_encodings = np.array(list(all_face_encodings.values()))

def sendToServer(toSend):
	s.send(toSend)

#def processor(url):
def processor(url,window):
	video_capture = get_jetson_gstreamer_source(url,1920,1080,100)
	face_locations = []
	face_encodings = []
	face_names = []
	process_this_frame = True
	cameraIP=re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url).group()
	final=""
	byt=b''
	global dateTime
	
	while True:
		ret, frame = video_capture.read()
		small_frame = cv2.resize(frame, (0, 0), fx=0.50, fy=0.50)
		rgb_small_frame = small_frame[:, :, ::-1]
		if process_this_frame:
        	# Find all the faces and face encodings in the current frame of video
			face_locations = face_recognition.face_locations(rgb_small_frame)
			face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
			face_names = []
			for face_encoding in face_encodings:
				matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
				name = "Unknown"
				if True in matches:
					first_match_index = matches.index(True)
					name=known_face_names[first_match_index]
				face_names.append(name)
				if(name!="Unknown"):
					currentDT = datetime.now()
					dateTime= str(currentDT.year)+str(currentDT.month)+str(currentDT.day)+str(currentDT.hour)+str(currentDT.minute)+str(currentDT.second)
					imgName=name+"_"+dateTime+".jpg"
					for (top, right, bottom, left), name in zip(face_locations, face_names):
						top *= 2
						right *= 2
						bottom *= 2
						left *= 2
						cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

		        # Draw a label with a name below the face
						cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
						font = cv2.FONT_HERSHEY_DUPLEX
						cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (0, 0, 0), 1)
					img = cv2.resize(frame,(300,180))
					cv2.imwrite("LogImages/"+imgName,img)
					final = "http://"+WEB_APP_IP+"/Home/SaveLog?intObjectID=["+name+"]&strDt=["+dateTime+"]&strIP=["+cameraIP+"]&strImgName=["+imgName+"]"
					print(colored(final, 'green'))
					byt=str.encode(final)
					sendToServer(byt)
				else:
					final=""
					byt=str.encode(final)
					sendToServer(byt)
				
		process_this_frame = not process_this_frame
			

th0 = Thread(target=processor,args=(url0,"video0"))
th1 = Thread(target=processor,args=(url1,"video1"))
th2 = Thread(target=processor,args=(url2,"video2"))
thPlaceImages = Thread(target=placeImages,)

#th0 = Thread(target=processor,args=(url0,))
#th1 = Thread(target=processor,args=(url1,))
#th2 = Thread(target=processor,args=(url2,))
th0.start()
th1.start()
th2.start()
thPlaceImages.start()

