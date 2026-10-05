import cv2
import numpy as np

#Herkennen van kleuren
onder_groen = np.array([36, 80, 180])
boven_groen = np.array([85, 255, 255])

PIXELS_VOLLE_BALK = 14000                     # gemeten met alle 22 leds aan
AANTAL_LEDS = 22
PIXELS_PER_LED = PIXELS_VOLLE_BALK / AANTAL_LEDS

# totaal aantal leds dat brandt als segment 1, 2, ... 10 aan is
SEGMENT_GRENZEN = [3, 5, 7, 9, 11, 13, 15, 17, 19, 22]


def herken_groen(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    masker = cv2.inRange(hsv, onder_groen, boven_groen)
    groene_pixels = cv2.countNonZero(masker)
    return masker, groene_pixels

def bereken_segmenten(groene_pixels):
    leds_aan = round(groene_pixels / PIXELS_PER_LED)
    segmenten = 0
    for grens in SEGMENT_GRENZEN:
        if leds_aan >= grens:
            segmenten += 1
    return segmenten
