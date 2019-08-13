import cv2 as open_cv
import numpy as np
import logging
from drawing_utils import draw_contours
from colors import COLOR_GREEN, COLOR_WHITE, COLOR_BLUE , COLOR_BLACK
from datetime import datetime

class MotionDetector:
    LAPLACIAN = 1.4
    DETECT_DELAY = 1
    
    ''' {
	1: {
			is_vacant: True
			in_time: None
			out_time: None
			lic_plate: None
			history: [
						{
							in_time: <Time when the car was parked as epoch>
							out_time: <Time when the car left - as epoch>
							duration: <calculate the time diff and save it>
							car_license_plate: <Get the license plate if, you can>
						}
					]
	               }
        }'''
    
    
    
    def __init__(self, video, coordinates, start_frame):
        self.video = video
        self.coordinates_data = coordinates
        self.start_frame = start_frame
        self.contours = []
        self.bounds = []
        self.mask = []
        
        self.my_parking_lot = { 
        '1': {'is_vacant': True, 'in_time': None, 'out_time': None,'lic_plate': None},
        '2': {'is_vacant': True, 'in_time': None, 'out_time': None,'lic_plate': None},
        '3': {'is_vacant': True, 'in_time': None, 'out_time': None,'lic_plate': None}
                      }
   
    def detect_motion(self):
        capture = open_cv.VideoCapture(self.video)
        capture.set(open_cv.CAP_PROP_POS_FRAMES, self.start_frame)

        coordinates_data = self.coordinates_data
        logging.debug("coordinates data: %s", coordinates_data)
        #print("coordinates data: %s", coordinates_data)

        for p in coordinates_data:
            coordinates = self._coordinates(p)
            logging.debug("coordinates: %s", coordinates)
            #print("coordinates: %s", coordinates)

            rect = open_cv.boundingRect(coordinates)
            #print("rect: %s", rect)

            new_coordinates = coordinates.copy()
            new_coordinates[:, 0] = coordinates[:, 0] - rect[0]
            new_coordinates[:, 1] = coordinates[:, 1] - rect[1]
            logging.debug("new_coordinates: %s", new_coordinates)
            #print("new_coordinates: %s", new_coordinates)

            self.contours.append(coordinates)
            self.bounds.append(rect)

            mask = open_cv.drawContours(
                np.zeros((rect[3], rect[2]), dtype=np.uint8),
                [new_coordinates],
                contourIdx=-1,
                color=255,
                thickness=-1,
                lineType=open_cv.LINE_8)

            mask = mask == 255
            self.mask.append(mask)
            logging.debug("mask: %s", self.mask)
            #print("mask: %s", self.mask)

        statuses = [False] * len(coordinates_data)
        times = [None] * len(coordinates_data)
       

        while capture.isOpened():
            result, frame = capture.read()
            if frame is None:
                break

            if not result:
                raise CaptureReadError("Error reading video capture on frame %s" % str(frame))

            blurred = open_cv.GaussianBlur(frame.copy(), (5, 5), 3)
            grayed = open_cv.cvtColor(blurred, open_cv.COLOR_BGR2GRAY)
            new_frame = frame.copy()
            logging.debug("new_frame: %s", new_frame)
            #print("new_frame: %s", new_frame)

            position_in_seconds = capture.get(open_cv.CAP_PROP_POS_MSEC) / 1000.0
            #print(capture.get(open_cv.CAP_PROP_POS_MSEC))

            for index, c in enumerate(coordinates_data):
                #print(index,c)
                status = self.__apply(grayed, index, c)
                #print(status)

                if times[index] is not None and self.same_status(statuses, index, status):
                    #print("wen is it coming here")
                    times[index] = None
                    continue

                if times[index] is not None and self.status_changed(statuses, index, status):
                    #print('====> idx: '+str(index)+' I am vacant now, at -- '+ str(datetime.now()))
                    for ind,slot_info in self.my_parking_lot.items():
                        if self.my_parking_lot[ind]['is_vacant']== True:
                            self.my_parking_lot[ind]['in_time']=str(datetime.now())
                            print(self.my_parking_lot[ind]['in_time'])
                            self.my_parking_lot[ind]['is_vacant']=False
                    if position_in_seconds - times[index] >= MotionDetector.DETECT_DELAY:
                        statuses[index] = status
                        times[index] = None
                    continue

                if times[index] is None and self.status_changed(statuses, index, status):
                    times[index] = position_in_seconds
                    for ind,slot_info in self.my_parking_lot.items():
                        if self.my_parking_lot[ind]['is_vacant']== False:
                            self.my_parking_lot[ind]['out_time']=str(datetime.now())
                            self.my_parking_lot[ind]['is_vacant']=True
                    #print('====> idx: '+str(index)+' I have a car here now, at -- '+ str(datetime.now(

            for index, p in enumerate(coordinates_data):
                coordinates = self._coordinates(p)

                color = COLOR_GREEN if statuses[index] else COLOR_BLUE
                #if statuses[index]:
                #print(datetime.now())
                draw_contours(new_frame, coordinates, str(p["id"] + 1), COLOR_WHITE, color)

            open_cv.imshow(str(self.video), new_frame)
            k = open_cv.waitKey(1)
            #print(self.my_parking_lot)
            if k == ord("q"):
                break
        capture.release()
        open_cv.destroyAllWindows()
    
    def __apply(self, grayed, index, p):
        coordinates = self._coordinates(p)
        logging.debug("points: %s", coordinates)
        #print("points: %s", coordinates)

        rect = self.bounds[index]
        logging.debug("rect: %s", rect)
        #print("rect: %s", rect)

        roi_gray = grayed[rect[1]:(rect[1] + rect[3]), rect[0]:(rect[0] + rect[2])]
        laplacian = open_cv.Laplacian(roi_gray, open_cv.CV_64F)
        logging.debug("laplacian: %s", laplacian)

        coordinates[:, 0] = coordinates[:, 0] - rect[0]
        coordinates[:, 1] = coordinates[:, 1] - rect[1]

        status = np.mean(np.abs(laplacian * self.mask[index])) < MotionDetector.LAPLACIAN
        logging.debug("status: %s", status)
        #print("rect: %s", rect)
        return status

    @staticmethod
    def _coordinates(p):
        return np.array(p["coordinates"])

    @staticmethod
    def same_status(coordinates_status, index, status):
        return status == coordinates_status[index]

    @staticmethod
    def status_changed(coordinates_status, index, status):
        return status != coordinates_status[index]


class CaptureReadError(Exception):
    pass
