import cv2
import numpy as np

# HSV-bereik voor de kleuren
onder_kleur = np.array([36, 80, 180])
boven_kleur = np.array([85, 255, 255])

def herken_kleur(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    masker = cv2.inRange(hsv, onder_kleur, boven_kleur)

    contouren, _ = cv2.findContours(masker, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    aantal = 0
    for c in contouren:
        if 10 < cv2.contourArea(c) > 400:
            x, y, b, h = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + b, y + h), (0, 165, 255), 2)
            cv2.putText(frame, "groen", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
            aantal += 1
    cv2.putText(frame, f"Aantal: {aantal}", (20, 40), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1.2, (255, 255, 255), 2)
    return frame, masker, aantal