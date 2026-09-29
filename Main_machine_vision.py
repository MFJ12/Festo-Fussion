# machine vision - live camerabeeld van een Allied Vision camera (Vimba X)
import cv2
from vmbpy import VmbSystem, FrameStatus, PixelFormat
from kleur_herkenning import herken_groen

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
            cam.ExposureTimeAbs.set(10000)   # belichtingstijd in microseconden: 10000 = 10 ms
            cam.BalanceWhiteAuto.set('Off')

            while True:
                frame = cam.get_frame()

                if frame.get_status() == FrameStatus.Complete:

                        img = frame.convert_pixel_format(PixelFormat.Bgr8).as_opencv_image()

                        img, masker = herken_groen(img)

                        cv2.imshow('Mako Camera Live Feed', img)
                        cv2.imshow('Masker',masker)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
           
    
    cv2.destroyAllWindows()

if __name__=='__main__':
    main()