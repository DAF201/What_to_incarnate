import winsound
from multiprocessing import Process
import cv2
import pyautogui
import time
import pathlib
import scan


PATH = str(pathlib.Path(__file__).parent.resolve())
START_TIME = time.time()
WINDOW_NAME = 'man in mirror'


def window_capture() -> None:
    myScreenshot = pyautogui.screenshot()
    myScreenshot.save(PATH+'\\'+r'%s.png' % str(time.time()-START_TIME))


def video_cap() -> None:
    switch_counter = 0
    cap = cv2.VideoCapture(0)
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(
        WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while True:
        ret, img = cap.read()
        img = cv2.flip(img, 1)
        cv2.imshow(WINDOW_NAME, img)
        pyautogui.click(100, 100)
        k = cv2.waitKey(1)
        if k == 27:
            exit()
        elif k == 26:
            window_capture()
        elif k == 24:
            switch(switch_counter)
            switch_counter += 1


def bgm() -> None:
    winsound.PlaySound(PATH+'\source\RHH.wav',
                       winsound.SND_ASYNC | winsound.SND_ALIAS)


def stop_bgm() -> None:
    winsound.PlaySound(None, winsound.SND_ASYNC)


def switch(switch_counter):
    if switch_counter % 2 == 0:
        bgm()
    else:
        stop_bgm()


def main() -> None:
    result = scan.covered()
    p1 = Process(target=video_cap, args=())
    p2 = Process(target=scan.scan, args=(result,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()


if __name__ == '__main__':
    main()
