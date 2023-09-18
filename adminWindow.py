#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 12:57:16 2023

@author: pk
"""

import os
import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import PhotoImage
import cv2
from PIL import Image, ImageTk
import sys
from attendanceFunctions import encodeImage
from attendanceFunctions import encodeSelectedImage
import qrcode
import mysql.connector
import uuid
import hashlib
from tkinter import messagebox
from datetime import datetime
import attendanceOOP


#set up database connection 
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="capstone_attendance"
)

mycursor= mydb.cursor()

#SQL statements 
subjectSQL= "SELECT subject_name FROM courses"
subjectIDSql= "SELECT subject_id FROM courses WHERE subject_name = %s"
insertKEY= "INSERT INTO qrKeys (subject_id,qr_key) VALUES (%s,%s)"
dateSQL= "SELECT date FROM calc1 WHERE subjectID = %s"

studentinfo_sql= "SELECT * FROM student_information WHERE student_id= %s"
#defnie function called hello tto print hello world
def hello():
    print("Hello World!")


#define function that opens camera using openCV
def openCamera():
    #start camera
    cap = cv2.VideoCapture(0)
    #set camera size
    cap.set(3,640)
    cap.set(4,480)
    #set camera brightness
    #cap.set(10,100)
    #set camera loop

    img_counter=0
    while True:
        #read camera frame
        success, img = cap.read()
        #display camera frame
        cv2.imshow("Camera",img)
        #set camera loop to break and camera window to close when q is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        #else if spacebar is pressed, capture frame
        elif cv2.waitKey(1)%256 == 32:
            img_name= "test_image_{}.png".format(img_counter)
            cv2.imwrite(img_name,img)
            print("Picure taken.")
            img_counter+=1

    # Release the VideoCapture object
    cap.release()

    # Destroy all windows
    cv2.destroyAllWindows()

 # Define function to show frame
def show_frames():
    global img
    global cap
    global label1
    # Get the latest frame and convert into Image
    cv2image = cv2.cvtColor(cap.read()[1], cv2.COLOR_BGR2RGB)
    img = Image.fromarray(cv2image)
    # Convert image to PhotoImage
    imgtk = ImageTk.PhotoImage(image=img)
    label1.imgtk = imgtk
    label1.configure(image=imgtk)
    # Repeat after an interval to capture continuously
    label1.after(20, show_frames)

def saveAndExit(event = 0):
    global img
    global cap
    global image_name
    if (len(sys.argv) < 2):
        #filepath = "imageCap.png"
        filepath = "dataset/{}.jpeg".format(image_name.get())
    else:
        filepath = sys.argv[1]
    
    print ("Output file to: " + filepath)
    img.save(filepath)
    #if (encodeImage(cap.read()[1], image_name.get())):
    #    messagebox.showinfo("Message", "Student Added Successfully.")
        
    try:
        encodeImage(cap.read()[1], image_name.get())
    except:
           messagebox.showerror("Error", "An Error Occured")
    else:
        messagebox.showinfo("Message", "Student Added Successfully")
        
    
def remove_disable(*args):
    global image_name
    global capture_btn
    if(len(image_name.get())>0):
        capture_btn.config(state="normal")
    elif(len(image_name.get())==0):
        capture_btn.config(state="disabled")

def fileUpload():
    global rootWindow
    global selectedimg
    f_types =[('Png files','*.png'),('Jpg Files', '*.jpg')]
    #filename = filedialog.askopenfilename()
    #print('Selected:', filename)
    
    
    filepath = filedialog.askopenfilename(filetypes=f_types)
    filename = os.path.basename(filepath)
    
    if filepath:
        #if error in encoding, dipslay messagebox saying 
        #"An Error Occured" and close btn
        #else dipslay messagebox saying 
        #"Student Added Successfully"

        try:
            split_filename = os.path.splitext(filename)
            actual_studentname=split_filename[0]
            encodethisimg=cv2.imread(filepath)
            encodeImage(encodethisimg, actual_studentname)
        except:
            messagebox.showerror("Error", "An Error Occured")
        else:
            messagebox.showinfo("Message", "Student Added Successfully")

def click(event):
    global imagename_box
    imagename_box.config(state="normal")
    imagename_box.delete(0,"end")
    
    # if file_path is not None:
    #     pass

# function to open a new window
# on a button click
def openNewWindow():
    global cap
    global label1
    global rootWindow
    global image_name
    global capture_btn
    global imagename_box
    # Toplevel object which will
    # be treated as a new window
    newWindow = Toplevel(rootWindow)

    # sets the title of the
    # Toplevel widget
    newWindow.title("Capture Student")

    # sets the geometry of toplevel
    newWindow.geometry("500x700")

    #create frame for video
    vidFrame=tkinter.Frame(newWindow)
    vidFrame.pack()

    # Create a Label to capture the Video frames
    label1 = Label(vidFrame,height=500)
    label1.pack()
    cap = cv2.VideoCapture(0)
    #set camera size
    cap.set(3,640)
    cap.set(4,480)
    
    show_frames()
    
    #create frame for capture btn
    btnFrame=tkinter.Frame(newWindow)
    btnFrame.pack()

    #set variable for image name entry string 
    image_name = tkinter.StringVar(btnFrame)

     #define label and pack it to add to window
    studentInfo_label =tkinter.Label(vidFrame,text = "Enter Student Name and ID",font=(None, 14))
    studentInfo_label.pack(pady=2)
    
    #create an entry box for the image name
    imagename_box = tkinter.Entry(btnFrame,textvariable=image_name)
    imagename_box.insert(0,"studentName_studentID")
    imagename_box.config(state="disabled")
    imagename_box.bind("<Button-1>",click)
    imagename_box.pack(pady=4)

    #Compact Camera icon by Icons8 "https://icons8.com" 
    camera_button=PhotoImage(file='icons/cameraicon.png')

    camerabtn_label=tkinter.Label(btnFrame,image=camera_button)
    #camerabtn_label.pack()

    # A btn widget to show in second frame
    capture_btn=tkinter.Button(btnFrame, text="Capture", command=saveAndExit, state="disabled")
    capture_btn.pack()

    #check for entry and execute state=normal for capture button
    image_name.trace("w", remove_disable)
    
def openQrWindow():
    global rootWindow
    global menu
    
    # Toplevel object which will
    # be treated as a new window
    qrWindow = Toplevel(rootWindow)

    # sets the title of the
    # Toplevel widget
    qrWindow.title("Send QR")

    # sets the geometry of toplevel
    qrWindow.geometry("500x600")
    
    #Set the Menu initially
    menu= StringVar()
    menu.set("Select Subject")
    
    #list out options to select from
    dropdown_options=[]
    
    #execute get subject sql
    mycursor.execute(subjectSQL)
    getSubjectresults = mycursor.fetchall()
    mydb.commit()
    
    for subjects in getSubjectresults:
        data =  (subjects[0])
        dropdown_options.append(data)
        #print (data)
        
    #subject_names=getSubjectresults
    #print(subject_names)
    
    #Create a dropdown Menu
    dropdown_menu= OptionMenu(qrWindow, menu, *dropdown_options)
    dropdown_menu.pack(pady=5)
    
    #defnie btn to create qrcode and pack it to add to window
    generateQr_btn= tkinter.Button(qrWindow, text="Generate QR", width=20, height=2, font=(None, 12), command=subject_selection)
    generateQr_btn.pack()
    
   
    qrWindow.mainloop() 
    
#function to select date   
#e is event that happened when bind action took place(selected,clikecd,etc) 
def select_date(e):
    global subjectdropdown_menu
    global datedropdown_menu
    global seletedsubject_courseID
    
    if subjectdropdown_menu.get():
       #list out the dates available based on selected subject
       datedropdown_option=[]
       
       #selected date 
       seletced_subject=subjectdropdown_menu.get()
       
       mycursor.execute(subjectIDSql,[seletced_subject])
       SubjectIDresults = mycursor.fetchall()
       mydb.commit()
       
       for subjectIDs in SubjectIDresults:
           data = (subjectIDs[0])
           seletedsubject_courseID=data
           
       dateVals=((seletedsubject_courseID,))
       #execute get subject sql
       mycursor.execute(dateSQL,dateVals)
       Dateresults = mycursor.fetchall()
       mydb.commit()
       
       for dates in Dateresults:
          data =  (dates[0])
          if (data) in datedropdown_option:
              pass
          else:
              datedropdown_option.append(data)
       
       datedropdown_menu.config(value=datedropdown_option)
       
def displaydate_records():
    global datedropdown_menu
    global attendacnerecords_win
    global seletedsubject_courseID
    global records_table
    selectrecordsSQL= "SELECT stud_name, stud_id, date FROM calc1 WHERE subjectID=%s AND date=%s AND present=1"
    
    if datedropdown_menu.get():
        for row in records_table.get_children():
           records_table.delete(row)
           
        selectrecordsVals=(seletedsubject_courseID,datedropdown_menu.get())
        mycursor.execute(selectrecordsSQL,selectrecordsVals)
        getrecords_Results = mycursor.fetchall()
        mydb.commit()
        
        #displaytable_label= Label(attendacnerecords_win, text=getrecords_Results)
        #displaytable_label.pack()
        
        for record in getrecords_Results:
            records_table.insert("","end", values=record)
            
def downloaddate_records():
    global datedropdown_menu
    global attendacnerecords_win
    global seletedsubject_courseID
    global records_table
    downloadrecordsSQL= "SELECT * FROM calc1 WHERE subjectID=%s AND date=%s"
    
    if datedropdown_menu.get():
        #try:
            selectrecordValues=(seletedsubject_courseID,datedropdown_menu.get())
            mycursor.execute(downloadrecordsSQL,selectrecordValues)
            downloadrecords_Results = mycursor.fetchall()
            mydb.commit()
            
            #displaytable_label= Label(attendacnerecords_win, text=getrecords_Results)
            #displaytable_label.pack()
            
            
            # path 
            path = 'records'
            selected_date= datedropdown_menu.get() 
            selectedcourse_ID= seletedsubject_courseID
            # Create the directory 
            # 'records'  
            try: 
                os.mkdir(path) 
                #filename format: record_date_subjectID.csv
                records_filename="records/record_{}_{}.csv".format(selected_date,selectedcourse_ID)
                f = open(records_filename, "w")
                
                f.write("Name,Student ID,Subject ID,Face Rec,QR rec,Date,Present\n")
                for record in downloadrecords_Results:
                    #print (record)
                    record=list(record)
                    record[5]=record[5].strftime('%d/%m/%Y')
                    #print(record)
                    f.write(str(record)[1:-1]+ '\n')
                    
                    
                f.close()  
                
            except FileExistsError: 
                records_filename="records/record_{}_{}.csv".format(selected_date,selectedcourse_ID)
                f = open(records_filename, "w")
                
                f.write("Name,Student ID,Subject ID,Face Rec,QR rec,Date,Present\n")
                for record in downloadrecords_Results:
                    #print (record)
                    record=list(record)
                    record[5]=record[5].strftime('%d/%m/%Y')
                    #print(record)
                    f.write(str(record)[1:-1]+ '\n')
                    
                f.close()  
        #except:
         #   messagebox.showerror("Error", "Subject or Date is invlaid")
 
    
    
def getRecords_win():
    global rootWindow
    global attendacnerecords_win
    global subjectdropdown_menu
    global datedropdown_menu
    global records_table
    # Toplevel object which will
    # be treated as a new window
    attendacnerecords_win = Toplevel(rootWindow)

    # sets the title of the
    # Toplevel widget
    attendacnerecords_win.title("Records 2")

    # sets the geometry of toplevel
    attendacnerecords_win.geometry("600x600")
    
    #define label and pack it to add to window
    subject_label =tkinter.Label(attendacnerecords_win,text = "Select Course",font=(None, 20))
    subject_label.pack(pady=6)
    
    #list out subjects to choose from 
    subjectdropdown_options=[]
    
    #execute get subject sql
    mycursor.execute(subjectSQL)
    getSubjectresults = mycursor.fetchall()
    mydb.commit()
    
    #put all subjects in subjectdropdown_options list
    for subjects in getSubjectresults:
        data =  (subjects[0])
        subjectdropdown_options.append(data)
        
    #make subject select dropdown
    subjectdropdown_menu= ttk.Combobox(attendacnerecords_win, value=subjectdropdown_options)
    
    #set dropdown default to first subject in subjectdropdown_options lsit
    subjectdropdown_menu.current(0)
    subjectdropdown_menu.pack()
    
    #bind select subject dropdown; 
    #to make it perform an action if it is clicked on
    subjectdropdown_menu.bind("<<ComboboxSelected>>", select_date)
    
    
    #make subject select dropdown
    datedropdown_menu= ttk.Combobox(attendacnerecords_win, value=["  "])
    
    #set dropdown default to first subject in subjectdropdown_options lsit
    datedropdown_menu.current(0)
    datedropdown_menu.pack(pady=3)
  
    #defnie btn to display records data in window
    seeRecords_btn= tkinter.Button(attendacnerecords_win, text="Display", width=20, height=2, font=(None, 12), command=displaydate_records)
    seeRecords_btn.pack(pady=3)
    
    #defnie btn to download records data in window
    downloadRecords_btn= tkinter.Button(attendacnerecords_win, text="Download", width=20, height=2, font=(None, 12), command=downloaddate_records)
    downloadRecords_btn.pack(pady=3)
    
    #table for selected course/date data
    tbl_style = ttk.Style()
    tbl_style.theme_use('clam')
    
    # Configure the style of Heading in Treeview widget
    tbl_style.configure('Treeview.Heading', background="black", foreground="white", font=(None, 18))
    tbl_style.configure('Treeview', font=(None, 16))
    
    # create a table
    records_table = ttk.Treeview(attendacnerecords_win, columns=("Name", "Student_ID", "Date"), show="headings")
    
    records_table.column("Name",anchor=CENTER)
    records_table.heading("Name", text="Name")
    
    records_table.column("Student_ID",anchor=CENTER)
    records_table.heading("Student_ID", text="Student_ID")
    
    records_table.column("Date",anchor=CENTER)
    records_table.heading("Date", text="Date")
    
    # pack the table
    records_table.pack(pady=10, fill="both", expand=True)
    
    
def subject_selection():
    global menu
    global subjectID
    
    if (menu.get()=="Select Subject"):
        print("Nothing selected")
    else:
        selected_option = menu.get()
        print("Selected option:", selected_option)
    
        #execute get subject_id sql
        #selectsubjectIDval=(selected_option)
        mycursor.execute(subjectIDSql,[selected_option])
        getSubjectIDresults = mycursor.fetchall()
        mydb.commit()
        
        for subjectIDs in getSubjectIDresults:
            global subjectID
            data = (subjectIDs[0])
            subjectID=data
            
        print("Subject ID:", subjectID)
        
        qr_Key=generate_key()
        print (qr_Key)
        
        createQR_func(subjectID, qr_Key)
    #generate_key()

    
def generate_key():
    global keyID
    global subjectID
    global hash_hex
    keyID  = uuid.uuid4()
    #print("Secure unique string id", keyID)
    
    # Generate a SHA-256 hash of the entry
    hash_object = hashlib.sha256(str(keyID).encode())
    hash_hex = hash_object.hexdigest()
    #print("Hash coded:", hash_hex)
    insertKEYvals=(subjectID,hash_hex)
    mycursor.execute(insertKEY,insertKEYvals)
    getKinsertkey= mycursor.fetchall()
    mydb.commit()
    return hash_hex

def convertTuple(tup):
	return ''.join([str(x) for x in tup])

    
def createQR_func(subject_id,qr_key):
    #global selectCourseStudents_tbl
    # enter the data
    #Data="Person A Surname,66792045,CS410"
    
  
    
    selectCourseStudents_tbl=subject_id
    #global selectCourseStudents_tbl
    selectCourseStudents= "SELECT stud_id FROM "+ selectCourseStudents_tbl
    
    #selectCourseStudents_vals=subject_id
    try:
        mycursor.execute(selectCourseStudents)
        selectCourseStudents_results = mycursor.fetchall()
        mydb.commit()
    except:
        messagebox.showerror("Error", "There are no students in this class.")
    
    print("These are the students in the class: ", selectCourseStudents_results)
    
    try:
        for i in (selectCourseStudents_results):
            selectCourseStudents_tuple = i
            selectCourseStudents_tuple_str= convertTuple(selectCourseStudents_tuple)
            print("These are the students in the class, string: ", selectCourseStudents_tuple_str)
        
        
            studentinfo_vals = selectCourseStudents_tuple_str.split(',')
            mycursor.execute(studentinfo_sql,studentinfo_vals)
            studentinfo_results = mycursor.fetchall()
            mydb.commit()
            
            now = datetime.now()
            #timeString = now.strftime('%H:%M:%S')
            dtString = now.strftime('%Y-%m-%d')  
            
            #name,id,subjectId,key
            
            
            for i in range(len(studentinfo_results)): 
                #print (studentinfo_results[i][1])
                QrData="{},{},{},{}".format(studentinfo_results[i][1],studentinfo_results[i][0],subject_id,qr_key)
                print ("qr data is: ",QrData)
        
                # generate the qrcode
                student_qrcode=qrcode.make(QrData)
                
                #create a filename
                filename="qrcodes/qrcode_{}_{}_{}.png".format(studentinfo_results[i][1],subject_id,dtString)
        
                # save the image
                # the image will be saved in
                # the same directory
                # you can also give a path
                student_qrcode.save(filename)
                attendanceOOP.create_message_with_attachment(studentinfo_results[i][2],filename)
    except:
         messagebox.showerror("Error", "An Error Occured")
    else:
         messagebox.showinfo("Message", "QR Generated and Deployed Successfully")


if __name__ == '__main__':
    global rootWindow

    #start tkinter window
    rootWindow= tkinter.Tk()

    #set window title
    rootWindow.title("ADMIN WINDOW")

    #set window size
    rootWindow.geometry("1000x1000")

    
    #create frame
    frame1=tkinter.Frame(rootWindow)
    frame1.pack()


    #define label and pack it to add to window
    addSpace_label =tkinter.Label(frame1,text = " ")
    addSpace_label.pack(pady=20)

    #define label and pack it to add to window
    addStud_label =tkinter.Label(frame1,text = "Add student face to database.",font=(None, 35))
    addStud_label.pack(pady=6)
    #addStud_label.grid(row=0,column=5)

    #defnie btn to take picture and pack it to add to window
    camera_btn= tkinter.Button(frame1, text="Camera", width=25, height=2, font=(None, 25),command=openCamera)
    #camera_btn.pack(pady=6)

    #defnie btn to take open new window and pack it 
    camera_window_btn= tkinter.Button(frame1, text="Camera", width=25, height=2, font=(None, 25),command=openNewWindow)
    camera_window_btn.pack(pady=6)

    #define btn to upload picture and pack to add to window
    upload_btn= tkinter.Button(frame1, width=30, height=2,font=(None, 25),text="Upload Image",command=fileUpload)
    upload_btn.pack()
    
    #define label and pack it to add to window
    addSpace2_label =tkinter.Label(frame1,text = " ")
    addSpace2_label.pack(pady=10)
    
    #define label and pack it to add to window
    qrcode_label =tkinter.Label(frame1,text = "Create and Send QR code.",font=(None, 35))
    qrcode_label.pack(pady=6)
    
    #defnie btn to create qrcode and pack it to add to window
    createQr_btn= tkinter.Button(frame1, text="Qr Code", width=25, height=2, font=(None, 25), command=openQrWindow)
    createQr_btn.pack()
    
    #define label and pack it to add to window
    addSpace3_label =tkinter.Label(frame1,text = " ")
    addSpace3_label.pack(pady=10)
    
    #define label and pack it to add to window
    printSchedule_label =tkinter.Label(frame1,text = "Schedule",font=(None, 35))
    printSchedule_label.pack(pady=6)
    
    #defnie btn to create qrcode and pack it to add to window
    printRecords_btn= tkinter.Button(frame1, text="Print Records", width=25, height=2, font=(None, 25), command=getRecords_win)
    printRecords_btn.pack()

    #set window loop
    rootWindow.mainloop()