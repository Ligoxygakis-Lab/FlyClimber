import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import tkinter as tk
import csv
import time
import math
from tkinter import *
from datetime import date


#Blue marks on vial colour range as BGR values
low_blue = np.array([0,0,0],dtype='uint8')
high_blue = np.array([255,85,85],dtype='uint8')

#Colour values for YW flies
YW_low_fly = np.array([10,65,10],dtype='uint8')
YW_high_fly = np.array([105,200,200],dtype='uint8')

#Colour values for W1118 flies
W1118_low_fly = np.array([10,10,10],dtype='uint8')
W1118_high_fly = np.array([105,80,80],dtype='uint8')

#Defining variables/lists
fly_height = []
limits = []
limitsx = []
height_avg = 0
Elapsed_Time = 0
ratio_SE = 0
vialx = 0
time_points = [3]
radii = []
csv_Data = []
v_f_ratio = []
noise = []
Video_Feed = False
Assay_Ongoing = False
Calibrating = True
Counting_Down = False

#Filters images by colour to find flies and blue dots on vials
def Mask_Create():

    mask_fly = cv.inRange(img, low_fly, high_fly)
    mask_limits = cv.inRange(img, low_blue, high_blue)

    #Filtering out Initial Noise
    kernel = np.ones((3,3),np.float32)/9
    mask_limits = cv.morphologyEx(mask_limits, cv.MORPH_OPEN, kernel)
    mask_limits = cv.morphologyEx(mask_limits, cv.MORPH_CLOSE, kernel)
    #Smoothing out areas in fly mask for more accurate identification
    mask_fly = cv.morphologyEx(mask_fly, cv.MORPH_CLOSE, kernel)

    return mask_limits,mask_fly


#Finding confines of vial in frame
def Vial_Bound(limits,vialx):
    limits_temp = []
    limitsx_temp = []

    #Identifies areas in colour mask
    contours_limit, hierarchy_limit = cv.findContours(mask_limits, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    #Finding top and bottom of vial
    for item in contours_limit:
        (x1,y1),radius1 = cv.minEnclosingCircle(item)
        if int(y1) in range(5,60) or int(y1) in range(540,595):
            limits_temp.append(int(y1))
            limitsx_temp.append(int(x1))

    #Updating limits values if limits detection was successful
    if len(limits_temp) >= 2:
        limits = [max(limits_temp),min(limits_temp)]
        vialx = int((min(limitsx_temp)+max(limitsx_temp))/2)
    
    return limits,vialx


#Identification of flies in frame
def Fly_Search(mask_fly,vialx):
    global radii
    global noise

    radii = []

    #Identifies areas in colour mask
    contours, hierarchy = cv.findContours(mask_fly, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    #Only updates flies if confines of vial are identified
    if len(limits) == 2:
        fly_height = []
        for item in contours:
            value = True
            (x,y),radius = cv.minEnclosingCircle(item)
            position = []
            position.append(x)
            position.append(y)
            if time_points[0] <= 4.5 and Assay_Ongoing == True:
                if int(y) in range(min(limits),int(min(limits)+(0.15*(max(limits)-min(limits))))):
                    if position not in noise:
                        noise.append(position)
                    del[item]
                    value = False
            #Determining if object not pixel of noise and is inside vial
            if value == True:
                if cv.contourArea(item) != 0:
                    #Checks if object is inside the vial
                    if int(y) in range ((min(limits)+5),(max(limits)-5)):
                        if int(x) in range ((vialx-50),(vialx+50)):
                            radii.append(radius)
                            center = (int(x),int(y))
                            #Checking for multiple flies
                            if (max(limits)-min(limits))/radius >= 0.5*np.mean(v_f_ratio):
                                if position not in noise:
                                    cv.circle(img,center,(int(radius)+5),(0,0,255),1)
                                    fly_height.append(int(y))
                            else:
                                if position not in noise:
                                    cv.circle(img,center,(int(radius)+5),(255,0,0),1)
                                    fly_no = int(math.ceil(radius/(1.1*np.mean(radii))))
                                    while fly_no > 0:
                                        fly_height.append(int(y))
                                        fly_no -= 1
    else:
        fly_height=[]
    
    return fly_height


#Creates list of flies sizes for multiple fly detection
def Calibration(limits,radii):

    if len(limits) == 2 and len(radii) != 0:
        vial_fly_ratio = (max(limits)-min(limits))/np.mean(radii)
        v_f_ratio.append(vial_fly_ratio)

    return v_f_ratio


#Formatting overlay during countdown period
def Countdown():
    global Start_Time
    global Countdown_Time
    global Counting_Down
    global Assay_Ongoing

    Countdown_Time = round((5-(time.perf_counter()-Start_Time)),2)
    if Countdown_Time <= 0:
        Counting_Down = False
        Assay_Ongoing = True
        Start_Time = time.perf_counter()
    cv.putText(img,"Countdown: "+str(Countdown_Time),(20,80),cv.FONT_HERSHEY_PLAIN,1.0,(0,0,255),1)


#Calculates average height of flies in the vial
def Height_Calc(limits):

    perc_fly_height = []
    #Checks if there are enough values to not return error in calculation
    if len(limits) > 1 and len(fly_height) > 0:
        minimum = min(limits)
        maximum = max(limits)
        for item in fly_height:
            height_avg = round(100 - (((item - minimum)/(maximum-minimum))*100),2)
            perc_fly_height.append(height_avg)
    
    return perc_fly_height


#Timer and data collection at specific time points
def Time_Function(perc_fly_height,time_points,Start_Time,csv_Data):
    global Assay_Ongoing
    global Elapsed_Time
    global img

    #Updating video timer
    Elapsed_Time = time.perf_counter()-Start_Time
    cv.putText(img,(f"Time: {Elapsed_Time:0.2f}"),(20,80),cv.FONT_HERSHEY_PLAIN,1.0,(0,0,0),1)

    #Data Collection every time point
    if len(time_points)!=0:
        interim_Data = []
        if Elapsed_Time >= time_points[0]:
            interim_Data.append(time_points[0])
            for item in perc_fly_height:
                interim_Data.append(item)
            csv_Data.append(interim_Data)
            del time_points[0]

    #Stops collecting data once all time points have been collected
    if len(time_points) == 0:
        Assay_Ongoing = False

    return csv_Data


#Function to exit tkinter and start video feed
def Open_Camera():
    global Video_Feed
    global gene_name
    global sex
    global repeat
    global fly_age
    global time_step
    global gene_bg
    Video_Feed = True

    #Assigning inputs to fields in tkinter window
    gene_name = input1.get()
    sex = input2.get()
    repeat = input3.get()
    fly_age = input4.get()
    time_step = float(input5.get())
    gene_bg = input6.get()

    #Generating list of time points for data collection
    while time_points[-1] < 30:
        time_points.append(round((time_points[-1]+time_step),2))
    time_points[-1] = 30

    app.quit()


#Creating window for field inputs
app = Tk()

app.bind('<Escape>', lambda e: app.quit())

label_widget = Label(app) 
label_widget.pack() 

#Creating input fields in window
label1 = tk.Label(text="Gene Name:", width=20, height=1)
label1.pack()
input1 = tk.Entry(fg="black", bg="white", width=8)
input1.pack()

label2 = tk.Label(text="Sex:", width=20, height=1)
label2.pack()
input2 = tk.Entry(fg="black", bg="white", width=8)
input2.pack()

label3 = tk.Label(text="Repeat:", width=20, height=1)
label3.pack()
input3 = tk.Entry(fg="black", bg="white", width=8)
input3.pack()

label4 = tk.Label(text="Fly Age (Days):", width=20, height=1)
label4.pack()
input4 = tk.Entry(fg="black", bg="white", width=8)
input4.pack()

label5 = tk.Label(text="Time Step:*", width=20, height=1)
label5.pack()
input5 = tk.Entry(fg="black", bg="white", width=8)
input5.pack()

label6 = tk.Label(text="Genetic Background(YW or W1118):*", width=30, height=1)
label6.pack()
input6 = tk.Entry(fg="black", bg="white", width=8)
input6.pack()

button1 = Button(app, text="Open Camera", command=Open_Camera) 
button1.pack()

app.mainloop()


#Initial Opening/Resizing of video
cap = cv.VideoCapture(1)
success, img = cap.read()
img = cv.resize(img, (800,600))

#Fly Colour Ranges as BGR values
if gene_bg == 'YW':
    low_fly = YW_low_fly
    high_fly = YW_high_fly
    Genetic_Background = True
elif gene_bg == 'W1118':
    low_fly = W1118_low_fly
    high_fly = W1118_high_fly
    Genetic_Background = True
else:
    Genetic_Background = False


#While loop to display video feed
while Video_Feed == True:

    if Genetic_Background == False:
        print("Invalid Genetic Background Input")
        break

    #Reading Video Frame and Resizing
    success, img = cap.read()
    if img is None:
        break
    img = cv.resize(img, (800,600))

    #Takes key input to start assay
    if cv.waitKey(25)==ord('s'):
        Counting_Down = True
        Calibrating = False
        Assay_Ongoing = False

        #Collecting Start Time
        Start_Time = time.perf_counter()

    #Calls above functions in correct order of operations
    mask_limits,mask_fly = Mask_Create()
    if Counting_Down == False:
        limits,vialx = Vial_Bound(limits,vialx)
        fly_height = Fly_Search(mask_fly,vialx)
    if Calibrating == True:
        v_f_ratio = Calibration(limits,radii)
    perc_fly_height = Height_Calc(limits)
    if Counting_Down == True:
        Countdown()
    #Only collects data if the assay timer is active
    if Assay_Ongoing == True:
        csv_Data = Time_Function(perc_fly_height,time_points,Start_Time,csv_Data)

    #Text overlay on video feed with fly details
    if Assay_Ongoing == False and Counting_Down == False:
        cv.putText(img,"Press s to start data collection",(20,80),cv.FONT_HERSHEY_PLAIN,1.0,(0,0,255),1)
    cv.putText(img,gene_name,(20,100),cv.FONT_HERSHEY_PLAIN,1.0,(0,0,0),1)
    cv.putText(img,sex,(20,120),cv.FONT_HERSHEY_PLAIN,1.0,(0,0,0),1)
    cv.putText(img,"Repeat:"+repeat,(20,140),cv.FONT_HERSHEY_PLAIN,1.0,(0,0,0),1)
    cv.putText(img,"Fly Age:"+fly_age+" days",(20,160),cv.FONT_HERSHEY_PLAIN,1.0,(0,0,0),1)
    cv.line(img,(1,60),(800,60),[0,255,0],1)
    cv.line(img,(1,540),(800,540),[0,255,0],1)

    #Displays video feed in window
    cv.imshow("img", img)
    
    #Checks if assay is completed before exiting window
    if Elapsed_Time >= 20 and Assay_Ongoing == False:
        break


# Collect all the x and y values into lists for graph drawing
x= []
y=[]

for item in csv_Data:
    x.append(item[0])
    if len(item[1:]) > 0:
        y.append(sum(item[1:])/len(item[1:]))
    elif len(y)>0:
        y.append(y[-1])
    else:
        y.append([0])

# Draw a line plot
plt.plot(x, y)

# Add labels and title
plt.xlabel('Time')
plt.ylabel('Average Height')
plt.title('Fly Vial Progression Against Time')

plt.show()

#Exporting Data to csv file

#Creates filename with input fields
filename = str(gene_name)+'_'+str(fly_age)+'days_'+sex+'_'+str(date.today())+'_rpt'+str(repeat)+'.csv'

#Opens csv file with created filename
with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    field = ["Time", "Avg Height"]

    #Creates headings in csv file
    writer.writerow(field)
    #Writes each data point into the csv file
    for item in csv_Data:
        writer.writerow(item)
