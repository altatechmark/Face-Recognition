import cv2
import numpy as np
import time
import os
from threading import Thread
from ftplib import FTP
from termcolor import colored
import face_recognition
import pickle
import numpy as np
global keepRunning
import threading
import glob

#image1 = cv2.imread("img1.jpg")[:,:,:3]





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
        

url1 = "rtsp://admin:Admin123.@192.168.2.154/Streaming/Channels/1"
def get_jetson_gstreamer_source(uri, width, height, latency):
    gst_str = ("rtspsrc location={} latency={} ! rtph264depay ! h264parse ! omxh264dec ! "
               "nvvidconv ! video/x-raw, width=(int){}, height=(int){}, format=(string)BGRx ! "
               "videoconvert ! appsink").format(uri, latency, width, height)
    return cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)

def getFrame():
	while True:
		ret,frame= cap.read()
		#cv2.imshow("run",frame)
		# cv2.waitKey(1)
		return frame
		
	#cv2.destroyAllWindows()
		
		
def showim():
	global done
	done=False
	global direction
	lock = threading.Lock()
	font = cv2.FONT_HERSHEY_DUPLEX
	while not done:
		with lock:
			rt,frm = cap0.read()
			cv2.putText(frm, direction, (960, 540), font, 3.0, (255, 0, 0), 2,cv2.LINE_AA)
			im = cv2.resize(frm,(500,300))
			cv2.imshow("run",im)
			cv2.waitKey(1)
	cv2.destroyAllWindows()
	cap0.release()

def train():
	global all_face_encodings
	all_face_encodings = {}
	global direction
	direction = "***"
	global done
	done=False
	count=0
	countEnc=1

	try:	
		print(colored("Connecting to FTP Server",'green'))
		ftp = FTP(host=host)
		login_status = ftp.login(user=username, passwd=password)
		print(login_status)
		ftp.cwd('EnrolledImages') #change directory
		print(ftp.dir())
		filelist=ftp.nlst()
		print(filelist)
		for file in filelist:
			time.sleep(0.05)
			try:
				fp = open("EnrolledImages/"+file, 'wb')
				ftp.retrbinary('RETR ' + file, fp.write, 1024)
				print ("Downloaded: " + file)
			except:
				print ("Error: File could not be downloaded " + file)

	except:
		print(colored("FTP Connection Failed, Check Host IP, Username or Password",'red'))
		exit(1)

	filelist = [] #to store all files
	ftp.retrlines('LIST',filelist.append)    # append to list  
	f=0


	while (count<=4):
	#take 5 images
	
		print(count)
		if(count==0):
			direction="Look strait to camere"
			print("Look strait to camere")
			time.sleep(5)
			cv2.imwrite(str(count)+'.jpg',getFrame())
			count+=1
		
		elif(count==1):
			direction="Look up"
			print("Look upside")
			time.sleep(5)
			cv2.imwrite(str(count)+'.jpg',getFrame())
			count+=1
		elif(count==2):
			direction="Look right"
			print("Look right")
			time.sleep(5)
			cv2.imwrite(str(count)+'.jpg',getFrame())
			count+=1
		elif(count==3):
			direction="Look left"
			print("Look left")
			time.sleep(5)
			cv2.imwrite(str(count)+'.jpg',getFrame())
			count+=1
		elif(count==4):
			direction="Look down"
			print("Look down")
			time.sleep(5)
			cv2.imwrite(str(count)+'.jpg',getFrame())
			count+=1
			keepRunning=False
	done=True
		
	
	#read 5 images
	image1 = cv2.imread("0.jpg")[:,:,:3]
	image2 = cv2.imread("1.jpg")[:,:,:3]
	image3 = cv2.imread("2.jpg")[:,:,:3]
	image4 = cv2.imread("3.jpg")[:,:,:3]
	image5 = cv2.imread("4.jpg")[:,:,:3]


	#append all 5 images in one jpg format
	m = Montage(image1)
	m.append(image2)
	m.append(image3)
	m.append(image4)
	m.append(image5)
	#remove images to save memory
	os.remove("0.jpg")
	os.remove("1.jpg")
	os.remove("2.jpg")
	os.remove("3.jpg")
	os.remove("4.jpg")
	print("Image Capturing completed")
	#save appended image
	m.show(id)
	#send appended image to ftp server

	print("Start Face Training")
	while (countEnc<=int(id)):
		
		#name = str(countEnc)+'.jpg'
		#print(colored("Checking if "+name+" is available on server",'blue'))
		#for f in filelist:
		#	if name in f:
		#		print(colored("Getting "+name+" from FTP server",'green'))
		#		fp = open("EnrolledImages/"+str(countEnc)+'.jpg', 'wb')
		#		ftp.retrbinary('RETR ' + str(countEnc)+'.jpg', fp.write, 1024)
		#		fp.close()
		#		f=1
		#if f==0:
		#	print(colored("Image not already found on server...",'red'))		
		
	
		try:
			encoding(countEnc)
			print("Face Training Completed "+str(countEnc/int(id)*100)+"%")
			if (countEnc==int(id)):
				try:
					fp = open('EnrolledImages/'+str(countEnc)+'.jpg', 'rb')
					ftp.storbinary('STOR %s' % os.path.basename(str(countEnc)+'.jpg'), fp, 1024)
					fp.close()
				except:
					print("ftp upload error")
					exit(1)
			#os.remove('EnrolledImages/'+id+'.jpg')
			countEnc+=1
			print(countEnc)
		except:
			countEnc+=1
			print('error')
	
	with open('EnrolledImages/dataset_faces.dat', 'wb') as f:
		pickle.dump(all_face_encodings, f)




	with open('EnrolledImages/dataset_faces.dat', 'rb') as f:
		all_face_encodings = pickle.load(f)

# Grab the list of names and the list of encodings
	face_names = list(all_face_encodings.keys())
	face_encodings = np.array(list(all_face_encodings.values()))

	print (face_names)
	
	try:
		fp = open('EnrolledImages/dataset_faces.dat', 'rb')
		ftp.storbinary('STOR %s' % os.path.basename('dataset_faces.dat'), fp, 1024)
		fp.close()
	except:
		print("ftp upload error")
		exit(1)
#os.remove('EnrolledImages/dataset_faces.dat')
	print(ftp.dir())
	print("Faces trained")
	files = glob.glob('EnrolledImages/*.jpg')
	for f in files:
		os.remove(f)
	fl = ftp.nlst()
	print(fl)



cap = get_jetson_gstreamer_source(url1, 1920, 1080, 100)
cap0 =  get_jetson_gstreamer_source(url1, 1920, 1080, 100)


#th= Thread(target=getFrame)
th0 = Thread(target=train)
th1 = Thread(target = showim)


id = input('Enter the ID: ')
host = input('Enter the host IP Address: ')
username=input('Enter Username: ')
password = input('Enter Password: ')
print("Start capturing Images...")
#th.start()
th0.start()
th1.start()

