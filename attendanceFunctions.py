#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 12:16:10 2023

@author: pk
"""

import cv2
import face_recognition
from datetime import datetime
#import for sql 
import mysql.connector
from PIL import Image, ImageTk
import numpy as np

#set up database connection 
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="capstone_attendance"
)

####SQL statements 
mycursor= mydb.cursor()
insertencodingsql = "INSERT INTO face_encodings (student, encoding) VALUES (%s, %s)"

images = []

#find encodings for images 
def findEncodings(images):
    encodeList=[]
    for img in images:
        img = cv2.cvtColor(img ,cv2.COLOR_BGR2RGB)
        #finding their encodings
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


def markAttendance(name):
    with open ('attendance.csv', 'r+') as f:
        #read lines so if someones name is already there we do not repeat it 
        myDataList= f.readlines()
        #print (myDataList)
        nameList = []
        for line in myDataList:
            entry= line.split(',')
            nameList.append(entry[0])
        
        ##check if current name is prestn  or not 
        if name not in nameList:
            now = datetime.now()
            timeString = now.strftime('%H:%M:%S')
            dtString = now.strftime('%Y-%m-%d')
            f.writelines(f'\n{name},{timeString},{dtString}')

#markAttendance('a')

#######
studentName= []

def markbarcodeAttendance(name):
    with open ('BARattendance.csv', 'r+') as f:
        #read lines so if someones name is already there we do not repeat it 
        myDataList= f.readlines()
        #print (myDataList)
        nameList = []
        for line in myDataList:
            entry= line.split(',')
            nameList.append(entry[0])
        #print (nameList)
        ##check if current name is prestn  or not 
        if name not in nameList:
            now = datetime.now()
            timeString = now.strftime('%H:%M:%S')
            dtString = now.strftime('%Y-%m-%d')
            f.writelines(f'\n{name},{timeString},{dtString}')
            

def encodingList(encodings):
    with open ('face_encodings.csv', 'r+') as f:
        #read lines so if someones name is already there we do not repeat it 
        myDataList= f.readlines()
        #print (myDataList)
        nameList = []
        for line in myDataList:
            entry= line.split(',')
            nameList.append(entry[0])
        
        ##check if current name is prestn  or not 
        if encodings not in nameList:
# =============================================================================
#             now = datetime.now()
#             timeString = now.strftime('%H:%M:%S')
#             dtString = now.strftime('%Y-%m-%d')
#             f.writelines(f'\n{name},{timeString},{dtString}')
# =============================================================================
            f.writelines(f'\n{encodings}')


#find encodings for images 
def findEncoding(image):
    with open ('face_encodings.csv', 'r+') as f:
        #read lines so if someones name is already there we do not repeat it 
        myDataList= f.readlines()
        #print (myDataList)
        nameList = []
        for line in myDataList:
            entry= line.split(',')
            nameList.append(entry[0])
        

    img = cv2.cvtColor(image ,cv2.COLOR_BGR2RGB)
    #finding their encodings
    encode = face_recognition.face_encodings(img)[0]

    if encode not in nameList:
        f.writelines(f'\n{encode}')
    
    return encode

def encodeImage(image,image_name):
    #find encodings for images 
    #image= cv2.resize(image,(0,0),None,0.50,0.50)
    img = cv2.cvtColor(image ,cv2.COLOR_BGR2RGB)
    #finding their encodings
    encode = face_recognition.face_encodings(img)[0]

    encoding= [image_name,encode]

    orderedEncoding=[]
    #lengthofEncoding=0

    orderedEncoding.append([encoding[0], encoding[1]])
    
    ##insert into db
    insertEncodingVals= (f'{encoding[0]}',f'{encoding[1]}')
    mycursor.execute(insertencodingsql, insertEncodingVals)
    insertresults = mycursor.fetchall()
    mydb.commit()
    #print(mycursor.rowcount, "record inserted.")
    
    #lengthofEncoding=lengthofEncoding+1
    
    #print(orderedEncodings[0])
    encodingList(orderedEncoding)
    print("Encoding complete.")
    
def encodeSelectedImage(image,image_name):
    #find encodings for images 
    #image= cv2.resize(image,(0,0),None,0.50,0.50)
    image=np.array(image)
    image= cv2.UMat(image)
    img = cv2.cvtColor(image ,cv2.COLOR_BGR2RGB)
    #finding their encodings
    encode = face_recognition.face_encodings(img)[0]

    encoding= [image_name,encode]

    orderedEncoding=[]
    #lengthofEncoding=0

    orderedEncoding.append([encoding[0], encoding[1]])
    
    ##insert into db
    insertEncodingVals= (f'{encoding[0]}',f'{encoding[1]}')
    mycursor.execute(insertencodingsql, insertEncodingVals)
    insertresults = mycursor.fetchall()
    mydb.commit()
    #print(mycursor.rowcount, "record inserted.")
    
    #lengthofEncoding=lengthofEncoding+1
    
    #print(orderedEncodings[0])
    encodingList(orderedEncoding)
    print("Encoding complete.")
    
    
def convertTuple(tup):
	return ''.join([str(x) for x in tup])

    
            