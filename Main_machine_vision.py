# machine vision - live camerabeeld van een Allied Vision camera (Vimba X)
import cv2
from vmbpy import VmbSystem, FrameStatus, PixelFormat
from kleur_herkenning import herken_kleur
from asyncua.sync import Client
from asyncua import ua
from geheim import PLC_USER, PLC_PASSWORD
PLC_URL = "opc.tcp://192.168.1.10:4840"
NODE_AANTAL = "ns=6;s=Arp.Plc.Eclr/Main1.iAantalBoxen"
APP_URI = "urn:festo-fussion:python"

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
            cam.ExposureTimeAbs.set(1500)   # belichtingstijd in microseconden:
            cam.BalanceWhiteAuto.set('Off')
            plc = Client(PLC_URL)
            plc.application_uri = APP_URI
            plc.set_security_string("Basic256Sha256,SignAndEncrypt,certificaat.der,sleutel.pem")
            plc.set_user(PLC_USER)
            plc.set_password(PLC_PASSWORD)
            plc.connect()
            node_aantal = plc.get_node(NODE_AANTAL)
            vorige_aantal = -1

            while True:
                frame = cam.get_frame()

                if frame.get_status() == FrameStatus.Complete:

                        img = frame.convert_pixel_format(PixelFormat.Bgr8).as_opencv_image()

                        img, masker, aantal = herken_kleur(img)
                        if aantal != vorige_aantal:
                            node_aantal.write_value(ua.DataValue(ua.Variant(aantal, ua.VariantType.Int16)))
                            vorige_aantal = aantal

                        cv2.imshow('Mako Camera Live Feed', img)
                        cv2.imshow('Masker',masker)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
            node_aantal.write_value(ua.DataValue(ua.Variant(0, ua.VariantType.Int16)))    
            plc.disconnect()
    
    cv2.destroyAllWindows()

if __name__=='__main__':
    main()