import cv2
import numpy as np

#Herkennen van kleuren in HSV values, geeft een grens aan waar het tussen moet zitten.
onder_groen = np.array([0, 80, 180])
boven_groen = np.array([20, 255, 255])

# ROI: linkerbovenhoek (x, y) en breedte/hoogte
ROI_X = 753
ROI_Y = 31
ROI_B = 75
ROI_H = 922

PIXELS_VOLLE_BALK = 9000                     # gemeten met alle 22 leds aan
AANTAL_LEDS = 22
PIXELS_PER_LED = PIXELS_VOLLE_BALK / AANTAL_LEDS

# totaal aantal leds dat brandt als segment 1, 2, ... 10 aan is
SEGMENT_GRENZEN = [3, 5, 7, 9, 11, 13, 15, 17, 19, 22]

# zorgt
def herken_groen(frame):
    # knip alleen het ROI-gedeelte uit het beeld
    roi = frame[ROI_Y:ROI_Y + ROI_H, ROI_X:ROI_X + ROI_B]

    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    masker = cv2.inRange(hsv, onder_groen, boven_groen)
    groene_pixels = cv2.countNonZero(masker)

    # teken de ROI als groene rechthoek, zodat je ziet waar gezocht wordt
    cv2.rectangle(frame, (ROI_X, ROI_Y), (ROI_X + ROI_B, ROI_Y + ROI_H), (0, 255, 0), 2)
    return masker, groene_pixels


def bereken_segmenten(groene_pixels):
    leds_aan = round(groene_pixels / PIXELS_PER_LED)
    segmenten = 0
    for grens in SEGMENT_GRENZEN:
        if leds_aan >= grens:
            segmenten += 1
    return segmenten
