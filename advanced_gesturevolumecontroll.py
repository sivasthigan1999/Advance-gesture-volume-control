import cv2

import time
import numpy as np
import handtrackingmodule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
wCam, hCam = 640, 480
cap=cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector=htm.handDetector(detectionCon=0.7,maxHands=1)
pTime = 0
volBar=0
vol=0
volPer=0

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange=volume.GetVolumeRange()

minVol=volRange[0]
maxVol=volRange[1]

while True:
    success,img=cap.read()
    #find hand
    img=detector.findHands(img)
    lmList,bbox = detector.findPosition(img, draw=True)
    if len(lmList) != 0:
        #print(lmList[4],lmList[8])
        #print(bbox)
        area=(bbox[2]-bbox[0])*(bbox[3]-bbox[1])//100
        #print(area)
        if area>200 and area<700:
            print('yes')

            #find distance between index and thump
            length, img, lineInfo = detector.findDistance(4, 8, img)
            print(length)



            #convert volume
            volPer=np.interp(length,[30,180],[0,100])
            volBar = np.interp(length, [30, 180], [400, 150])


            # Reduce Resolution to make it smoother
            smoothness = 1
            volPer = smoothness * round(volPer / smoothness)

            fingers=detector.fingersUp()
            print(fingers)

            #check fingers up
            if fingers[4]==0:
            #set volume if pinky finger is down
                volume.SetMasterVolumeLevelScalar(volPer / 100, None)
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 10, (0, 255, 0), cv2.FILLED)

        cv2.rectangle(img,(50,150),(85,400),(0,255,0),3)
        cv2.rectangle(img,(50,int(volBar)),(85,400),(0,255,0),cv2.FILLED)
        cv2.putText(img, f' {int(volPer)}%', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                    1, (0, 255, 0), 3)
        #print(vol)

    # frame rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 0), 3)
    cVol = int(volume.GetMasterVolumeLevelScalar() * 100)
    cv2.putText(img, f'SET vol: {int(cVol)}', (400, 50), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 0), 3)
    cv2.imshow('image',img)
    if cv2.waitKey(1) and 0xFF == ord('q'):

        break