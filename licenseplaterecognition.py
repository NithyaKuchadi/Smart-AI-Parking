import numpy as np
import cv2
import os
from openalpr import Alpr
import pandas
import mysql.connector;
from mysql.connector import Error
from mysql.connector import errorcode
from datetime import datetime


alpr = Alpr("us", "/etc/openalpr/openalpr.conf", "/usr/local/share/openalpr/runtime_data")

connection = mysql.connector.connect(host='localhost',
                             database='project220',
                             user='root',
                             password='nithY@123', auth_plugin='mysql_native_password')
alpr.set_top_n(1)
alpr.set_default_region("ca")

cap = cv2.VideoCapture("/Users/nithyakuchadi/sandbox/licenseplate/ka.mov")
dict_plt={}
my_dict = {}

path = "/Users/nithyakuchadi/sandbox/licenseplate/outputFile.txt"

if os.path.exists(path):
    os.remove(path)

outputFile = open(path, "a+", 0)
count = 0
success = True
result={}
def code():
    curs.execute(sql_select_query8,insert_tuple0)
    connection.commit()
    records1 = curs.fetchone()
    if records1[0]>1 :
        sql_update_query="UPDATE user SET ExitTime = (%s) WHERE LicenseNo=(%s)"
        y=""+str(datetime.now())
        insert_tuple3 = (y,x)
        result  = curs.execute(sql_update_query,insert_tuple3)
        connection.commit()     
        sql_select_query1="SELECT TIMESTAMPDIFF(MINUTE,EntryTime,ExitTime) from user WHERE LicenseNo=(%s)"
        curs.execute(sql_select_query1,insert_tuple0)
        connection.commit()
        records11 = curs.fetchone()
        sql_update_query4="UPDATE user SET ParkingPrice = (%s) WHERE LicenseNo=(%s)"
        insert_tuple41 = (records1[0]*1,x)
        result  = curs.execute(sql_update_query4,insert_tuple41)
        connection.commit()
        outputFile.write("%12s%12f\n" % (candidate['plate'], candidate['confidence']))
        dict_plt[candidate['plate']] = candidate['confidence']  
        


while success:    
    success,frame = cap.read()
    cv2.imwrite("frame%d.jpg" % count, frame)     # save frame as JPEG file
    image = cv2.imread('frame{}.jpg'.format(count), -1)
    if(True):      
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        cv2.imwrite("img.jpg", frame)
        results = alpr.recognize_file("img.jpg")
        i = 0
        
        for plate in results['results']:
            i += 1
            for candidate in plate['candidates']:
                prefix = "-"
                if candidate['matches_template']:
                    prefix = "*"
                    
                if candidate['confidence']>87.3 and len(candidate['plate'])==7:
                    prev=candidate['plate']
                    t=""+str(datetime.now())
                    x=""+str(candidate['plate'])
                    curs = connection.cursor(buffered=True)
                    sql_select_query0="select slotID from parkingSlot WHERE LicenseNo=(%s)"
                    insert_tuple0 = (x,)
                    curs.execute(sql_select_query0,insert_tuple0)
                    records = curs.fetchone()
                    connection.commit()
                    if records != None:
                        try:
                                sql_insert_date_query9 = "INSERT INTO user(LicenseNo,EntryTime,slotID) VALUES (%s,%s,%s)"
                                slotid=""+str(records[0])
                                insert_tuple9 = (x,t,slotid)
                                result  = curs.execute(sql_insert_date_query9,insert_tuple9)
                                connection.commit()
                        except Error as e:
                                sql_select_query8="SELECT TIMESTAMPDIFF(MINUTE,EntryTime,NOW()) from user WHERE LicenseNo=(%s)"
                                code()
                    else:
                        try:
                                sql_insert_date_query = "INSERT INTO user(LicenseNo,EntryTime) VALUES (%s,%s)"
                                my_dict[x]=t
                                insert_tuple = (x,t)
                                result  = curs.execute(sql_insert_date_query,insert_tuple)
                                print(x)
                                connection.commit()
                        except Error as e:
                                sql_select_query8="SELECT TIMESTAMPDIFF(MINUTE,EntryTime,NOW()) from user WHERE LicenseNo=(%s)"
                                code()
                    if x in my_dict.keys():
                            sql_select_query8="SELECT TIMESTAMPDIFF(MINUTE,EntryTime,ExitTime) from user WHERE LicenseNo=(%s)"
                            code()
                    my_dict[x]=t
                       
        os.remove('frame{}.jpg'.format(count))
        count+=1
    
outputFile.close()
predict_val = max(dict_plt.values())
license_plate = [k for k, v in dict_plt.items() if v == predict_val]
cap.release()
alpr.unload()
cv2.destroyAllWindows()

