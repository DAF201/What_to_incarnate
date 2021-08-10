import os
import time
import math
import threading
import glfw
import PyFaceDet
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from kill3d import 窗口
from rimo_utils import 计时, cv0, matrix
import pathlib


线程数 = 3
最低信念 = 65
人脸座标 = []
lock = threading.Lock()
PATH = str(pathlib.Path(__file__).parent.resolve())


def scan(result):
    def 人脸检测(img):
        偷懒 = 3
        w, h = img.shape[:2]
        if h/偷懒 < 64:
            偷懒 = h/64
        if w/偷懒 < 64:
            偷懒 = w/64
        img = cv0.resize(img, dsize=(int(h/偷懒), int(w/偷懒)))
        for det in PyFaceDet.facedetect_cnn(img):  # 横坐标、纵坐标、长度、宽度、置信度、角度
            x, y, w, h = det[:4]
            信念 = det[4]
            if 信念 < 最低信念:
                continue
            yield np.array([y, y+h, x, x+w])*偷懒

    def 循环人脸座标():
        def g():
            global 人脸座标
            while True:
                res = []
                for _, 截图, 位置 in 窗口.全部扫描([窗口.顶层窗口()]):
                    if 截图 is None:
                        continue
                    for det in 人脸检测(截图):
                        实际位置 = det + np.array([位置[1], 位置[1], 位置[0], 位置[0]])
                        res.append(实际位置)
                人脸座标 = res
        for _ in range(线程数):
            threading.Thread(target=g, daemon=True).start()

    此處 = os.path.abspath(os.path.dirname(__file__))
    图 = cv0.read(f'{此處}'+'%s' % result)

    def 生成opengl纹理(npdata):
        w, h, 通道数 = npdata.shape
        d = 2**int(max(math.log2(w), math.log2(h)) + 1)
        纹理 = np.zeros([d, d, 通道数], dtype=npdata.dtype)
        纹理[:w, :h] = npdata
        纹理座标 = (w / d, h / d)

        width, height = 纹理.shape[:2]
        纹理编号 = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, 纹理编号)
        if 通道数 == 3:
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width,
                         height, 0, GL_BGR, GL_UNSIGNED_BYTE, 纹理)
        if 通道数 == 4:
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width,
                         height, 0, GL_BGRA, GL_UNSIGNED_BYTE, 纹理)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

        return 纹理编号, 纹理座标

    def 新建窗口(尺寸, 标题='Your mask'):
        glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, True)
        glfw.window_hint(glfw.RESIZABLE, False)
        glfw.window_hint(glfw.FLOATING, True)
        window = glfw.create_window(*尺寸, 标题, None, None)
        glfw.make_context_current(window)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFuncSeparate(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA,
                            GL_ONE, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0, 0, 0, 0)
        纹理编号, 纹理座标 = 生成opengl纹理(图)
        return window, 纹理编号, 纹理座标

    glfw.init()
    循环人脸座标()

    莉沫大军 = []
    莉沫大军.append(新建窗口([300, 300]))

    def 画图(纹理编号, 纹理座标):
        glClear(GL_COLOR_BUFFER_BIT)
        glBindTexture(GL_TEXTURE_2D, 纹理编号)
        glColor4f(1, 1, 1, 1)
        a = b = -1
        c = d = 1
        q, w = 纹理座标
        [[p1, p2],
         [p4, p3]] = np.array([
             [[a, b, 0, 1, 0, 0], [a, d, 0, 1, w, 0]],
             [[c, b, 0, 1, 0, q], [c, d, 0, 1, w, q]],
         ])
        t = matrix.rotate_ax(-math.pi/2, axis=(0, 1))
        glBegin(GL_QUADS)
        for p in [p1, p2, p3, p4]:
            glTexCoord2f(*p[4:])
            glVertex4f(*(p[:4]@t))
        glEnd()
        glfw.swap_buffers(window)

    def 定位(window, p):
        x = p[3]-p[2]
        y = p[1]-p[0]
        y1, x1 = 图.shape[:2]
        if x1/y1 < x/y:
            xx = int(y/y1*x1)
            glViewport((x-xx)//2, 0, xx, y)
        else:
            yy = int(x/x1*y1)
            glViewport(0, (y-yy)//2, x, yy)
        glfw.set_window_monitor(window, None,
                                xpos=p[2],
                                ypos=p[0],
                                width=p[3]-p[2],
                                height=p[1]-p[0],
                                refresh_rate=glfw.DONT_CARE
                                )

    while True:
        pp = 人脸座标
        glfw.poll_events()
        for i, p in enumerate(pp):
            while len(莉沫大军) <= i:
                莉沫大军.append(新建窗口([200, 200]))
            window, 纹理编号, 纹理座标 = 莉沫大军[i]
            glfw.make_context_current(window)
            glfw.poll_events()
            # glfw.window_hint(glfw.VISIBLE, True)
            glfw.set_window_attrib(window, glfw.DECORATED, False)
            r = 0.3
            y1, y2, x1, x2 = p
            dy = (y2-y1)*r
            dx = (x2-x1)*r
            p = np.array([y1-dy*2, y2+dy, x1-dx, x2+dx]).astype(int)
            定位(window, p)
            画图(纹理编号, 纹理座标)
        for window, _, _ in 莉沫大军[len(pp):]:
            glfw.make_context_current(window)
            glfw.poll_events()
            glfw.destroy_window(window)
        莉沫大军 = 莉沫大军[:len(pp)]
        time.sleep(0.01)


def covered() -> str:
    print('今天化身什么呢？')
    print('1:顶碗人,2:贝极星,3:皇珈骑士, 4:嘉心糖, 5.奶淇淋')
    user = input()

    if user == '1' or user == '顶碗人':
        covered = r".\source\bowl.png"
    elif user == '2' or user == '贝极星':
        covered = r".\source\star.png"
    elif user == '3' or user == '皇珈骑士':
        covered = r".\source\knight.png"
    elif user == '4' or user == '嘉心糖':
        covered = r".\source\candy.png"
    elif user == '5' or user == '奶淇淋':
        covered = r".\source\icecream.png"
    elif user == 'asoul' or user == '一个魂':
        covered = r".\source\A_soul.png"
    elif user == 'mouse' or user == 'mice' or user == 'rat' or '鼠' in user:
        covered = r".\source\mouse.png"
    elif user == '毒唯' or user == 'dw':
        covered = r".\source\joker.png"
    elif user == 'carol' or user == 'Carol' or user == '珈乐':
        covered = r".\source\Carol.png"
    elif user == 'cr':
        covered = r".\source\cr.png"
    elif user == 'alien':
        covered = r".\source\alien.png"
    elif user == 'redheel' or user == '高跟鞋':
        covered = r".\source\high_heel.png"
    elif user == '流汗黄豆' or user == '😅':
        covered = r".\source\sweating_soybean.png"
    elif user == 'hj' or user == '汉奸' or user == 'traitor' or '东' in user or '眠' in user:
        covered = r".\source\traitor.png"
    elif user == 'robot' or user == '机器人':
        covered = r".\source\robot.png"
    elif user == 'demon' or user == '恶魔':
        covered = r".\source\demon.png"
    elif user == 'microphone' or user == 'jb':
        covered = r".\source\microphone.png"
    elif user == 'lama' or user == '羊驼' or user == '阿草':
        if os.path.isfile(PATH+'\source\lama.png'):
            covered = r".\source\lama.png"
        else:
            print('file missing')
            covered = r".\source\ybb.png"
    else:
        covered = r".\source\ybb.png"
    return covered
