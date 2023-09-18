# Capstone Applied Project: Improving Attendance Tracking in Tertiary Institutions using Automated Face Recognition and QR Code Technology

This applied capstone project aims to improve attendance taking in tertiary institutions (specifically Ashesi University) by creating an automated attendance system that uses face recognition and QR code technology. The system employs a two-step authentication process to mark students present, which makes it more difficult for dishonest students to bypass attendance tracking

## Authors

- [@PaaKwesiAddae](https://github.com/Ashesi-Org/attendaceSystem_PaaKwesiAddae.git)
 

## Installation

To run this program successfully you must have the folder
- [attendaceSystem_PaaKwesiAddae](https://github.com/Ashesi-Org/attendaceSystem_PaaKwesiAddae)

Or a directory containing the following files within it:

- [arrangedCode.py]: Code for student side detection using face recognition and QR code technology.
- [attendanceFunctions.py]: functions for use in student side and admin (lecturer/FI) end of program.
- [attendanceOOP.py]: Object oriented programming to seperate face recognition from QR recognition code.
- [adminWindow.py]: Admin end of program for adding students, sending out QR and printing csv files of attendance.
- [attendance.csv]
- [BARattendance.csv]
- [face_encodings.csv]

### Dependencies 
The following python libraries are needed to run this program. 
- tkinter
- cv2
- PIL 
- mysql.connector
- numpy 
- face_recognition
- datetime 
- pyzbar
- os
- sys
- qrcode
- uuid
- hashlib

The following python libraries were used as a workaround for sending emails via Outlook through a [shortcut](https://stackoverflow.com/questions/61529817/automate-outlook-on-mac-with-python) on macOS
- appscript import app, k
- mactypes import Alias
- pathlib import Path


The following must also be called in both the admin end and student end: 
- attendanceFunctions: [attendanceFunctions.py]
- attendanceOOP: [attendanceOOP.py]


## Appendix

This project was programmed on an M1 MacBook pro. This caused a lot of problems with the installation of dependencies and running the program.
For the sake of protection of the system and the dependencies a virtual environment was used. 
Spyder, running python 3.1.13, in [Anaconda-Navigator](https://docs.anaconda.com/free/navigator/) was used. 


## Acknowledgements
 - [Vardan Agarwal ML model](https://github.com/vardanagarwal/Proctoring-AI)

 - [Jayme Gordon AppleScript for automating Outlook on macOS](https://stackoverflow.com/questions/61529817/automate-outlook-on-mac-with-python)