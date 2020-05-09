import cv2
import argparse
import numpy as np
import sys
import glob
from PIL import Image

#####################################################################

keep_processing = True

# parse command line arguments for camera ID or video file

parser = argparse.ArgumentParser(description='Perform ' + sys.argv[0] + ' example operation on incoming camera/video image')
parser.add_argument("-c", "--camera_to_use", type=int, help="specify camera to use", default=0)
parser.add_argument("-r", "--rescale", type=float, help="rescale image by this factor", default=1.0)
parser.add_argument('video_file', metavar='video_file', type=str, nargs='?', help='specify optional video file')
args = parser.parse_args()


#####################################################################

# basic grayscale histogram drawing in raw OpenCV using lines

# adapted from:
# https://raw.githubusercontent.com/Itseez/opencv/master/samples/python2/hist.py

def hist_lines(hist):
    h = np.ones((300,256,3)) * 255 # white background
    cv2.normalize(hist,hist,0,255,cv2.NORM_MINMAX)
    hist=np.int32(np.around(hist))
    for x,y in enumerate(hist):
        cv2.line(h,(x,0),(x,y),(0,0,0)) # black bars
    y = np.flipud(h)
    return y

#####################################################################

# define video capture object

cap = cv2.VideoCapture(0)

# define display window name

windowName1 = "Live Camera Input" # window name
windowName2 = "Input Histogram" # window name
windowName3 = "Processed Output" # window name
windowName4 = "Output Histogram" # window name
windowName5 = "Hasil Stack"

# if command line arguments are provided try to read video_file
# otherwise default to capture from attached H/W camera

if (((args.video_file) and (cap.open(str(args.video_file))))
    or (cap.open(args.camera_to_use))):

    # create window by name (as resizable)

    cv2.namedWindow(windowName1, cv2.WINDOW_NORMAL)
    cv2.namedWindow(windowName2, cv2.WINDOW_NORMAL)
    cv2.namedWindow(windowName3, cv2.WINDOW_NORMAL)
    cv2.namedWindow(windowName4, cv2.WINDOW_NORMAL)
    cv2.namedWindow(windowName5, cv2.WINDOW_NORMAL)

    while (keep_processing):

        # if video file or camera successfully open then read frame from video

        if (cap.isOpened):
            ret, frame = cap.read()
            # when we reach the end of the video (file) exit cleanly

            if (ret == 0):
                keep_processing = False
                continue
            
            # rescale if specified

            if (args.rescale != 1.0):
                frame = cv2.resize(frame, (0, 0), fx=args.rescale, fy=args.rescale)

        # convert to grayscale

        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # perform histogram equalization

        output = cv2.equalizeHist(gray_img)

        count = 0
        while (keep_processing):
            ret,frame = output.read()
            #cv2.imshow('window-name',frame)
            cv2.imwrite("results/frame%d.jpg" % count, frame)
            count = count + 1
            if count == 30:
                break

        
        gorengan = cv2.add(("results/frame%d.jpg" % count),("results/frame%d.jpg" % count+1))

        # Langkah 1 mengakses dan mengambil frame dri source yang sudah di EequalHist, lalu menyimpannya, jika bisa menyimpan dalam variabel saja
        # def getFrame(sec):
        #     output.set(cv2.CAP_PROP_POS_MSEC, sec*15)
        #     hasFrames, bakwan = output.read()
        #     if hasFrames:
        #         cv2.imwrite("dasar"+str(count)+".jpg", bakwan)

        #     return hasFrames
        # sec = 0
        # frameRate = 0.5
        # count = 1
        # succes = getFrame(sec)
        # while succes:
        #     count = count + 1
        #     sec = sec + frameRate
        #     sec = round(sec, 2)
        #     succes = getFrame(sec)

        # Langkah 2 menggabungkan frame-frame yang dibaca pada Langkah 1 menjadi 1 gambar
        #gabung = cv2.add(output,0)

        # display image

        cv2.imshow(windowName1,gray_img)
        cv2.imshow(windowName2,hist_lines(cv2.calcHist([gray_img],[0],None,[256],[0,256])))
        cv2.imshow(windowName3,output)
        cv2.imshow(windowName4,hist_lines(cv2.calcHist([output],[0],None,[256],[0,256])))
        cv2.imshow(windowName5,gorengan)

        
        # start the event loop - essential

        # cv2.waitKey() is a keyboard binding function (argument is the time in milliseconds).
        # It waits for specified milliseconds for any keyboard event.
        # If you press any key in that time, the program continues.
        # If 0 is passed, it waits indefinitely for a key stroke.
        # (bitwise and with 0xFF to extract least significant byte of multi-byte response)

                
        key = cv2.waitKey(40) & 0xFF # wait 40ms (i.e. 1000ms / 25 fps = 40 ms)

        # It can also be set to detect specific key strokes by recording which key is pressed

        # e.g. if user presses "x" then exit

        if (key == ord('x')):
            keep_processing = False
        

    # close all windows

    cv2.destroyAllWindows()

else:
    print("No video file specified or camera connected.")

#####################################################################
