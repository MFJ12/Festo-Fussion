# machine vision - live camerabeeld van een Allied Vision camera (Vimba X)
import cv2
from vmbpy import VmbSystem, FrameStatus, PixelFormat
from kleur_herkenning import herken_kleur
from asyncua.sync import Client
from asyncua import ua
from geheim import PLC_USER, PLC_PASSWORD
from Pixel_grootte import herken_groen, bereken_segmenten

PLC_GEBRUIKEN = False
PLC_URL = "opc.tcp://192.168.1.10:4840"
NODE_SEGMENT = "ns=6;s=Arp.Plc.Eclr/Main1.iAantalSegmenten"
NODE_ORANJE = "ns=6;s=Arp.Plc.Eclr/Main1.iAantalOranje"
APP_URI = "urn:festo-fussion:python"

def klik(event, x, y, flags, meting):
    # print de gemiddelde HSV-waarde van een 5x5 gebiedje rond de muisklik
    if event == cv2.EVENT_LBUTTONDOWN and meting["hsv"] is not None:
        stukje = meting["hsv"][max(y - 2, 0):y + 3, max(x - 2, 0):x + 3]
        h, s, v = stukje.reshape(-1, 3).mean(axis=0).astype(int)
        print(f"x={x} y={y}   H={h} S={s} V={v}")

def main():

    with VmbSystem.get_instance() as vmb:
        cams = vmb.get_all_cameras()
        if not cams:
            print("Geen Mako camera gevonden.")
            return

        cam = cams[0]

        with cam:
            print(f"Verbonden met: {cam.get_name()}({cam.get_id()})")

            cam.set_pixel_format(PixelFormat.BayerRG8)
            cam.ExposureAuto.set('Off')
            cam.ExposureTimeAbs.set(10000)   # belichtingstijd in microseconden:1500
            cam.BalanceWhiteAuto.set('Off')

            if PLC_GEBRUIKEN:
                plc = Client(PLC_URL)
                plc.application_uri = APP_URI
                plc.set_security_string("Basic256Sha256,SignAndEncrypt,certificaat.der,sleutel.pem")
                plc.set_user(PLC_USER)
                plc.set_password(PLC_PASSWORD)
                plc.connect()
                node_segment = plc.get_node(NODE_SEGMENT)
                node_oranje = plc.get_node(NODE_ORANJE)
            vorige_oranje = -1
            vorige_aantal = -1

            meting = {"hsv": None}
            cv2.namedWindow('Mako Camera Live Feed')
            cv2.setMouseCallback('Mako Camera Live Feed', klik, meting)

            while True:
                frame = cam.get_frame()

                if frame.get_status() == FrameStatus.Complete:

                        img = frame.convert_pixel_format(PixelFormat.Bgr8).as_opencv_image()
                        meting["hsv"] = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

                        img, masker_oranje, aantal_oranje = herken_kleur(img)
                        if aantal_oranje != vorige_oranje:
                            if PLC_GEBRUIKEN:
                                node_oranje.write_value(ua.DataValue(ua.Variant(aantal_oranje, ua.VariantType.Int16)))
                            vorige_oranje = aantal_oranje

                         
                        masker_groen, groene_pixels = herken_groen(img)
                        segmenten = bereken_segmenten(groene_pixels)

                        # telt het aantal segmenten zorgt ervoor dat de value word aangepast wanneer het niet gelijk is
                        if segmenten != vorige_aantal:
                            if PLC_GEBRUIKEN:    
                                node_segment.write_value(ua.DataValue(ua.Variant(segmenten, ua.VariantType.Int16)))
                            vorige_aantal = segmenten

                        # geeft text linksboven in het beeld
                        cv2.putText(img, f"Groen: {groene_pixels}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                        cv2.putText(img, f"Segmenten: {segmenten}", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

                        # geeft het camerabeeld weer op de laptop
                        cv2.imshow('Mako Camera Live Feed', img)
                        cv2.imshow('Masker groen', masker_groen)
                        cv2.imshow('Masker oranje', masker_oranje)
                        
                        # cv2.imshow('Masker',masker)
                # zorgt ervoor dat het programma wordt afgesloten
                if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
            if PLC_GEBRUIKEN:                
            # zet node_segment op nul zodat de plc geen integer vasthoud.
                node_segment.write_value(ua.DataValue(ua.Variant(0, ua.VariantType.Int16)))
            # zorgt ervoor dat de verbinding word verbroken met de plc.
                plc.disconnect()
                
    cv2.destroyAllWindows()

if __name__=='__main__':
    main()