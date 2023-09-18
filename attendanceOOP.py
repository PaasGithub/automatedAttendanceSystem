#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 15:35:41 2023

@author: pk
"""
import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
from attendanceFunctions import *
from appscript import app, k
from mactypes import Alias
from pathlib import Path

# Import the decode() function from the pyzbar library
from pyzbar.pyzbar import decode

#import for sql 
import mysql.connector

#set up database connection 
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="capstone_attendance"
)


mycursor= mydb.cursor()



class attendance_facerecognition:
    
    
    selectEncodingssql= "SELECT encoding FROM face_encodings"
    selectEncodingNamessql= "SELECT student FROM face_encodings"

    path = '/Users/pk/Desktop/capstone_python/dataset'


    studentNames=[]

    ###get student names from face encoidng 
    ###place names in array
    mycursor.execute(selectEncodingNamessql)
    studentEncodingName = mycursor.fetchall()

    for names in studentEncodingName:
        untuplednames=''.join(names)
        studentNames.append(untuplednames)
    print("student names mine;",studentNames)
    ##
    #pull encodings for images from db
    mycursor.execute(selectEncodingssql)
    selectEncodingsresults = mycursor.fetchall()
    mydb.commit()
    encodeListKnown_unicode=selectEncodingsresults
    

    
    def face_rec(self,cv2image):
        ##face sql
        insertfacesql = "INSERT INTO facetest (stud_name, stud_id, time, date) VALUES (%s, %s, %s, %s)"
        existfacesql = "SELECT stud_id FROM facetest WHERE EXISTS(SELECT stud_id FROM facetest WHERE date = %s AND stud_id = %s)"

        checkcoursetblSQL= "SELECT stud_id FROM calc1 WHERE EXISTS(SELECT stud_id FROM calc1 WHERE stud_name = %s AND stud_id = %s AND date= %s)"
        insertFaceCoursesql= "INSERT INTO calc1 (stud_name, stud_id, face_check, date) VALUES (%s, %s, %s, %s)"
        updateFaceCourseSql= "UPDATE calc1 SET face_check = %s WHERE stud_name = %s AND stud_id = %s AND date= %s"
        updatePresentsql="UPDATE calc1 SET present = (CASE WHEN face_check = 1 AND barcode_check = 1 AND stud_name = %s AND stud_id = %s AND date= %s THEN %s ELSE 0 END) WHERE stud_name = %s AND stud_id = %s AND date= %s"

         
        facesCurrentFrame= face_recognition.face_locations(cv2image)
        #finding encoding of webcam 
        encodeCurrentFrame = face_recognition.face_encodings(cv2image,facesCurrentFrame)
        
        
        #finding the matches 
        #iterate through all faces in current frame  
        #compare them with emcodings we found before
        
        for encodeFace,faceLocation in zip(encodeCurrentFrame,facesCurrentFrame):
            encodeListKnown=[]
            for item in attendance_facerecognition.encodeListKnown_unicode:
                arr_str = item[0]
                arr = np.fromstring(arr_str[1:-1], sep=' ')
                encodeListKnown.append(arr)
                
            matches = face_recognition.compare_faces(encodeListKnown,encodeFace,tolerance=0.5)
            name = "Unknown"
            
            ##lowest distance is best match  
            faceDistance = face_recognition.face_distance(encodeListKnown,encodeFace)
            print(faceDistance)
            
            ##find lowest element in list, that is your face match 
            matchIndex= np.argmin(faceDistance)
            
            print (matches[matchIndex])
            
            y1,x2,y2,x1 = faceLocation
            #print(faceLocation)
            
            #y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4
            #print(y1)
            #print(img)
            cv2.rectangle(cv2image,(x1,y1),(x2,y2),(255,0,0),2)
            cv2.rectangle(cv2image,(x1,y2-35),(x2,y2),(255,0,0),cv2.FILLED)
      
            cv2.putText(cv2image,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),2)
            markAttendance(name)
            
            ##bounding box and dispaly name
            if matches[matchIndex]:
                name = attendance_facerecognition.studentNames[matchIndex]
                #print ("MAtch index is:",matchIndex)
                print (name)
                
                now = datetime.now()
                timeString = now.strftime('%H:%M:%S')
                dtString = now.strftime('%Y-%m-%d')
                Insertname= name.split('_')
                insertfaceval = (f'{Insertname[0]}',f'{Insertname[1]}',f'{timeString}',f'{dtString}')
                #check if already exists in db 
                existfaceVal = (dtString,Insertname[1])
                mycursor.execute(existfacesql, existfaceVal)
                facerows = mycursor.fetchall()
                
                 
                y1,x2,y2,x1 = faceLocation
                #print(faceLocation)
                
                #y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4
                #print(y1)
                #print(img)
                cv2.rectangle(cv2image,(x1,y1),(x2,y2),(0,255,0),2)
                cv2.rectangle(cv2image,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
          
                cv2.putText(cv2image,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),2)
                markAttendance(name)
                
                if (len(facerows)>0):
                    print ('Exists.')
                    
                    #check course table(calc1) if record exists
                    #if no, insert record appropriately 
                    #if yes, update record
                    checkCourTblVal= (f'{Insertname[0]}',f'{Insertname[1]}',f'{dtString}')
                    mycursor.execute(checkcoursetblSQL,checkCourTblVal)
                    checkCourseTblresults=mycursor.fetchall()
                    
                    if (len(checkCourseTblresults)>0):
                        print("Course record exists in Calc1.")
                        updateCourseRecordVals = (1,f'{Insertname[0]}',f'{Insertname[1]}',f'{dtString}')
                        mycursor.execute(updateFaceCourseSql,updateCourseRecordVals)
                        updateresults=mycursor.fetchall()
                        mydb.commit()
                        print(mycursor.rowcount, "record updated.")
                        
                        #update present 
                        updatePresentVals= (f'{Insertname[0]}',f'{Insertname[1]}',f'{dtString}',1,f'{Insertname[0]}',f'{Insertname[1]}',f'{dtString}')
                        mycursor.execute(updatePresentsql,updatePresentVals)
                        updatePresentresults=mycursor.fetchall()
                        mydb.commit()
                        
                    else:
                        print("Course record does not exist in Calc1.")
                        insertCourserecordVals=(f'{Insertname[0]}',f'{Insertname[1]}',1,f'{dtString}')
                        mycursor.execute(insertFaceCoursesql,insertCourserecordVals)
                        insertCourserecordResults=mycursor.fetchall()
                        mydb.commit()
                        print(mycursor.rowcount, "course record inserted.")
                  
                else:
                    #execute insert into db
                    mycursor.execute(insertfacesql, insertfaceval) 
                    insertresults = mycursor.fetchall()
                    mydb.commit()
                    print(mycursor.rowcount, "record inserted.")
                    
                    #check course table(calc1) if record exists
                    #if no, insert record appropriately 
                    #if yes, update record
                    checkCourTblVal= (f'{Insertname[0]}',f'{Insertname[1]}',f'{dtString}')
                    mycursor.execute(checkcoursetblSQL,checkCourTblVal)
                    checkCourseTblresults=mycursor.fetchall()
                    
                    if (len(checkCourseTblresults)>0):
                        print("Course record exists in Calc1.")
                    else:
                        print("Course record does not exist in Calc1.")
                        insertCourserecordVals=(f'{Insertname[0]}',f'{Insertname[1]}',1,f'{dtString}')
                        mycursor.execute(insertFaceCoursesql,insertCourserecordVals)
                        insertCourserecordResults=mycursor.fetchall()
                        mydb.commit()
                        print(mycursor.rowcount, "course record inserted.")
      
            
class attendance_qrrecognition:
    
    def qr_rec(self,cv2image,vid):
        
    
        ###barcode sql
        #barcode sql statemetns 
        insertbarcodesql = "INSERT INTO barcodetest (stud_name, stud_id, subject_id, time, date) VALUES (%s, %s, %s, %s, %s)"
        existsql = "SELECT stud_id FROM barcodetest WHERE EXISTS(SELECT stud_id FROM barcodetest WHERE date = %s AND stud_id = %s AND subject_id = %s)"
        
        checkcoursetblSQL= "SELECT stud_id FROM calc1 WHERE EXISTS(SELECT stud_id FROM calc1 WHERE stud_name = %s AND stud_id = %s AND subjectID = %s AND date= %s)"
        insertCourserecordsql= "INSERT INTO calc1 (stud_name, stud_id, subjectID, barcode_check, date) VALUES (%s, %s, %s, %s, %s)"
        updateCourseRecordSql= "UPDATE calc1 SET barcode_check = %s, subjectID= %s WHERE stud_name = %s AND stud_id = %s AND date= %s"
        updatePresentsql="UPDATE calc1 SET present = (CASE WHEN face_check = 1 AND barcode_check = 1 AND stud_name = %s AND stud_id = %s AND subjectID = %s AND date= %s THEN %s ELSE 0 END) WHERE stud_name = %s AND stud_id = %s AND subjectID = %s AND date= %s"
        
        checkQRkey= "SELECT qr_key from qrKeys WHERE subject_id=%s and date=%s ORDER BY key_id DESC LIMIT 1"

        # Check if the img was successfully read
        if vid.read()[0]:
            # Convert the img to grayscale
            gray = cv2.cvtColor(vid.read()[1], cv2.COLOR_BGR2GRAY)

            # Use the decode() function from the pyzbar library to detect and decode barcodes in the img
            barcodes = decode(gray)

            # Loop through the detected barcodes
            for barcode in barcodes:
                # Extract the data from the barcode
                barcode_data = barcode.data.decode("utf-8")
                if (barcode_data):
                    #name= barcode_data.split(',') or barcode_data.split() 
                    #split barcode data by markers , or _ or a space
                    try:
                        name=barcode_data.split(',') 
                        now = datetime.now()
                        timeString = now.strftime('%H:%M:%S')
                        dtString = now.strftime('%Y-%m-%d')
                        existVal = (dtString,name[1],name[2])
                        print (name)
                    except Exception as underscore:
                        name=barcode_data.split('_') 
                        now = datetime.now()
                        timeString = now.strftime('%H:%M:%S')
                        dtString = now.strftime('%Y-%m-%d')
                        existVal = (dtString,name[1],name[2])
                        print (name)
                    except Exception as e:
                        name=barcode_data.split(' ') 
                        now = datetime.now()
                        timeString = now.strftime('%H:%M:%S')
                        dtString = now.strftime('%Y-%m-%d')
                        existVal = (dtString,name[1],name[2])
                        print (name)
                   
                    
                
                #if qrkey is the same as one in the database
                #make box green 
                #else make box red
                dtString = now.strftime('%Y-%m-%d')
                checkQRkey_vals=(name[2],dtString)
                #execute check if exists 
                mycursor.execute(checkQRkey, checkQRkey_vals)
                checkQRrow = mycursor.fetchall()
                mydb.commit()
                QRkey_check=convertTuple(checkQRrow)
                #QRkey_checkStr, = QRkey_check
                
                formatted_list = [(name[3],)]
                
                print ("This is fetch all:")
                print (checkQRrow)
                print ("THis is check QR: ")
                #checkQRrow[0]= str(checkQRrow[0[0]])
                print (QRkey_check)
                #print (checkQRrow[0])
                print ("This is qr key: " + name[3])
                print ("This is updated qr key: " )
                print(formatted_list)
                if (checkQRrow==formatted_list):
                    # Extract the bounding box coordinates of the barcode
                    (x, y, w, h) = barcode.rect

                    # Draw a rectangle around the barcode
                    cv2.rectangle(cv2image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    
                    # Display the data on the img
                    cv2.putText(cv2image, name[0], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
               
                    #execute check if exists 
                    mycursor.execute(existsql, existVal)
                    rows = mycursor.fetchall()
                    
                    if (len(rows)>0):
                        print("Exists")
                       
                        
                        #check course table(calc1) if record exists
                        #if no, insert record appropriately 
                        #if yes, update record
                        checkCourTblVal= (f'{name[0]}',f'{name[1]}',f'{name[2]}',f'{dtString}')
                        mycursor.execute(checkcoursetblSQL,checkCourTblVal)
                        checkCourseTblresults=mycursor.fetchall()
                        
                        if (len(checkCourseTblresults)>0):
                            print("Course record exists in Calc1.")
                            updateCourseRecordVals = (1,f'{name[2]}',f'{name[0]}',f'{name[1]}',f'{dtString}')
                            mycursor.execute(updateCourseRecordSql,updateCourseRecordVals)
                            updateresults=mycursor.fetchall()
                            mydb.commit()
                            print(mycursor.rowcount, "record updated.")
                            
                            #update present 
                            updatePresentVals= (f'{name[0]}',f'{name[1]}',f'{name[2]}',f'{dtString}',1,f'{name[0]}',f'{name[1]}',f'{name[2]}',f'{dtString}')
                            mycursor.execute(updatePresentsql,updatePresentVals)
                            updatePresentresults=mycursor.fetchall()
                            mydb.commit()
                            
                        else:
                            print("Course record does not exist in Calc1.")
                            insertCourserecordVals=(f'{name[0]}',f'{name[1]}',f'{name[2]}',1,f'{dtString}')
                            mycursor.execute(insertCourserecordsql,insertCourserecordVals)
                            insertCourserecordResults=mycursor.fetchall()
                            mydb.commit()
                            print(mycursor.rowcount, "course record inserted.")
                        
                    else:
                        print("None exists")
                        insertbarcodeval = (f'{name[0]}',f'{name[1]}',f'{name[2]}',f'{timeString}',f'{dtString}')
                        #check if already exists in db 
                        
                        #execute insert into db
                        mycursor.execute(insertbarcodesql, insertbarcodeval)
                        insertresults = mycursor.fetchall()
                        mydb.commit()
                        print(mycursor.rowcount, "record inserted.")
                        
                        #check course table(calc1) if record exists
                        #if no, insert record appropriately 
                        #if yes, update record
                        checkCourTblVal= (f'{name[0]}',f'{name[1]}',f'{name[2]}',f'{dtString}')
                        mycursor.execute(checkcoursetblSQL,checkCourTblVal)
                        checkCourseTblresults=mycursor.fetchall()
                        
                        if (len(checkCourseTblresults)>0):
                            print("Course record exists in Calc1.")
                        else:
                            print("Course record does not exist in Calc1.")
                            insertCourserecordVals=(f'{name[0]}',f'{name[1]}',f'{name[2]}',1,f'{dtString}')
                            mycursor.execute(insertCourserecordsql,insertCourserecordVals)
                            insertCourserecordResults=mycursor.fetchall()
                            mydb.commit()
                            print(mycursor.rowcount, "course record inserted.")
          
                    ##mark attendance 
                    markbarcodeAttendance(name[0])
                    
                else:
                    # Extract the bounding box coordinates of the barcode
                    (x, y, w, h) = barcode.rect


                    # Draw a rectangle around the barcode
                    cv2.rectangle(cv2image, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    
                    # Display the data on the img
                    cv2.putText(cv2image, "WRONG QR", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                    
# =============================================================================
#                     # Draw a rectangle around the barcode
#                     cv2.rectangle(cv2image, (x, y), (x + w, y + h), (0, 255, 0), 2)
#                     
#                     # Display the data on the img
#                     cv2.putText(cv2image, name[0], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
# =============================================================================
               
                        
 
                
 #email sectino of code
    
def create_message_with_attachment(to_recip,path):
    subject = 'QR code'
    body = 'Attached is your qr code for class today.'
    to_recip = [to_recip]

    msg = Message(subject=subject, body=body, to_recip=to_recip)

    # attach file
    #p = Path('/Users/pk/Desktop/capstone_python/qrcodes/qrcode_P.K.Addae_BUSA405_2023-03-25.png')
    p= path
    msg.add_attachment(p)

    #msg.show()
    msg.send()


class Outlook(object):
    def __init__(self):
        self.client = app('Microsoft Outlook')

class Message(object):
    def __init__(self, parent=None, subject='', body='', to_recip=[], cc_recip=[], show_=True):

        if parent is None: parent = Outlook()
        client = parent.client

        self.msg = client.make(
            new=k.outgoing_message,
            with_properties={k.subject: subject, k.content: body})

        self.add_recipients(emails=to_recip, type_='to')
        self.add_recipients(emails=cc_recip, type_='cc')

        #if show_: self.show()

    def show(self):
        self.msg.open()
        self.msg.activate()

    def add_attachment(self, p):
        # p is a Path() obj, could also pass string

        p = Alias(str(p)) # convert string/path obj to POSIX/mactypes path

        attach = self.msg.make(new=k.attachment, with_properties={k.file: p})

    def add_recipients(self, emails, type_='to'):
        if not isinstance(emails, list): emails = [emails]
        for email in emails:
            self.add_recipient(email=email, type_=type_)

    def add_recipient(self, email, type_='to'):
        msg = self.msg

        if type_ == 'to':
            recipient = k.to_recipient
        elif type_ == 'cc':
            recipient = k.cc_recipient

        msg.make(new=recipient, with_properties={k.email_address: {k.address: email}})
        
    def send(self):
        self.msg.send()
        
#create_message_with_attachment()

        