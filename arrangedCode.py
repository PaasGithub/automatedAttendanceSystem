#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 18 13:16:06 2023

@author: pk
"""

import tkinter
from tkinter import *
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
from attendanceFunctions import *
import attendanceOOP
#import for sql 
import mysql.connector



# Define function to show frame
def show_frames():
    global vid 
    global label1
    # Get the latest frame and convert into Image
    cv2image = cv2.resize(vid.read()[1],(0,0),None,0.50,0.50)
    cv2image = cv2.cvtColor(vid.read()[1], cv2.COLOR_BGR2RGB)
    
    '''
    face recognition part 
    '''
    attendanceOOP.attendance_facerecognition().face_rec(cv2image)
    '''
    end face rec part
    '''
    
    '''
    start qr section
    '''
    attendanceOOP.attendance_qrrecognition().qr_rec(cv2image,vid)
    '''
    end qr rec part
    '''
   
    img = Image.fromarray(cv2image)
    # Convert image to PhotoImage
    imgtk = ImageTk.PhotoImage(image=img)
    label1.imgtk = imgtk
    label1.configure(image=imgtk)
    # Repeat after an interval to capture continuously
    label1.after(20, show_frames)
    
def updateAttendance_tbl():
    global table
    global mydb
    ####SQL statements 
    #selectpresentsql= "SELECT stud_name, stud_id, date FROM calc1 where present=1 AND date='2023-03-28'"
    selectpresentsql= "SELECT stud_name, stud_id, date FROM calc1 where present=1 AND date=CURDATE()"
    selectpresentresults=mycursor.execute(selectpresentsql)
    selectpresenttbl=mycursor.fetchall()
    mydb.commit()
    studentNum=0
    
    for row in table.get_children():
       table.delete(row)
       
    for student in selectpresenttbl:
        print (student)
        #delete data in table
        #reinsert updated data
        table.insert("","end", values=student)
           
# =============================================================================
#             if student in table.item(child)["values"]:
#                 #pass
#                 print ("Yes")
#             else:
#                 #table.insert("","end", values=student)
#                print ("No")
# =============================================================================
            
# =============================================================================
#             if student[0] in table.item(child)["values"]:
#                 pass
#             else:
#                 table.insert("","end", values=student)
# =============================================================================

            
# =============================================================================
#         for child in table.get_children():
#             print(table.item(child)["values"])
#             if student in table.item(child)["values"]:
#                 #pass
#                 print ("Yes")
#             else:
#                 #table.insert("","end", values=student)
#                 print ("No")
# =============================================================================

def main():
    global vid 
    global label1 
    global table
    #set up database connection 
    mydb = mysql.connector.connect(
      host="localhost",
      user="root",
      password="",
      database="capstone_attendance"
    )
     
    rootWindow=Tk()
    
    frame1 = Frame(rootWindow)
    frame1.pack(side=LEFT, expand=True, fill=BOTH)
    
    winHeight=frame1.winfo_screenheight()
    
    # Create a Label to capture the Video frames
    label1 = Label(frame1, width=600, height=winHeight)
    label1.pack(padx=20, pady=20)
    vid = cv2.VideoCapture(0)
    #print (vid)
    
    show_frames()
        
        
    frame2 = Frame(rootWindow, background="green")
    frame2.pack(side=RIGHT, expand=True, fill=BOTH)
    
    style = ttk.Style()
    style.theme_use('clam')
    
    # Configure the style of Heading in Treeview widget
    style.configure('Treeview.Heading', background="black", foreground="white", font=(None, 15))
    style.configure('Treeview', font=(None, 15))
    
    # create a table
    table = ttk.Treeview(frame2, columns=("Name", "ID", "Date"), show="headings")
    
    table.column("Name",anchor=CENTER)
    table.heading("Name", text="Name")
    
    table.column("ID",anchor=CENTER)
    table.heading("ID", text="ID")
    
    table.column("Date",anchor=CENTER)
    table.heading("Date", text="Date")

     
# =============================================================================
#     for student in selectpresenttbl:
#         table.insert("","end", values=student)
#     studentNum=studentNum+1
# =============================================================================

    # configure the font of the table
    #table.tag_configure("Treeview", font=("Helvetica", 20))
    
    # pack the table
    table.pack(fill="both", expand=True)
    
    #defnie btn to take update records table and pack it 
    updateRecords_btn= tkinter.Button(frame2, text="Update", width=25, height=2, font=(None, 25),command=updateAttendance_tbl)
    updateRecords_btn.pack(pady=6)
    
    rootWindow.attributes("-fullscreen", True)
    rootWindow.mainloop()
    
if __name__== '__main__':
    main()
