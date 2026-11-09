import cv2
import numpy as np

# HSV-bereik voor de oranje schijf (gemeten op de schijf: H 4-8, S 130-200, V 50-92)
# S-ondergrens 140 houdt de zwakke weerspiegeling onder de schijf buiten het masker
onder_kleur = np.array([0, 140, 45])
boven_kleur = np.array([12, 255, 255])
# ROI: linkerbovenhoek (x, y) en breedte/hoogte
ROI_X = 339
ROI_Y = 13
ROI_B = 292
ROI_H = 593

# vormeisen: de schijf zie je van opzij, dus breed en plat
MIN_BREEDTE = 100        # pixels
MIN_VERHOUDING = 5       # breedte / hoogte

def herken_kleur(frame):
    # knip alleen het ROI-gedeelte uit het beeld
    roi = frame[ROI_Y:ROI_Y + ROI_H, ROI_X:ROI_X + ROI_B]

    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    masker = cv2.inRange(hsv, onder_kleur, boven_kleur)
    # ruis weghalen en gaatjes in de schijf dichten
    masker = cv2.morphologyEx(masker, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    masker = cv2.morphologyEx(masker, cv2.MORPH_CLOSE, np.ones((5, 15), np.uint8))

    contouren, _ = cv2.findContours(masker, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # zoek de grootste vlek die breed en plat is: dat is de schijf
    schijf = None
    for c in contouren:
        x, y, b, h = cv2.boundingRect(c)
        if b >= MIN_BREEDTE and b / max(h, 1) >= MIN_VERHOUDING:
            if schijf is None or cv2.contourArea(c) > cv2.contourArea(schijf):
                schijf = c

    aantal = 0
    if schijf is not None:
        x, y, b, h = cv2.boundingRect(schijf)
        # coördinaten zijn binnen de ROI, dus ROI_X/ROI_Y erbij optellen voor het hele beeld
        x += ROI_X
        y += ROI_Y
        midden_y = y + h // 2
        cv2.rectangle(frame, (x, y), (x + b, y + h), (0, 165, 255), 2)
        cv2.putText(frame, f"schijf y={midden_y}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
        aantal = 1

    # teken de ROI zelf als blauwe rechthoek, zodat je ziet waar gezocht wordt
    cv2.rectangle(frame, (ROI_X, ROI_Y), (ROI_X + ROI_B, ROI_Y + ROI_H), (255, 0, 0), 2)
    cv2.putText(frame, f"Aantal: {aantal}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
    return frame, masker, aantal

# def herken_kleur(frame):
#     hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
#     masker = cv2.inRange(hsv, onder_kleur, boven_kleur)

#     contouren, _ = cv2.findContours(masker, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     aantal = 0
#     for c in contouren:
#         if cv2.contourArea(c) > 400:
#             x, y, b, h = cv2.boundingRect(c)
#             cv2.rectangle(frame, (x, y), (x + b, y + h), (0, 165, 255), 2)
#             cv2.putText(frame, "oranje", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
#             aantal += 1
#     cv2.putText(frame, f"Aantal: {aantal}", (20, 40), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1.2, (255, 255, 255), 2)
#     return frame, masker, aantal