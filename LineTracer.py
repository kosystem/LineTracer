#! /usr/bin/python

import sys
sys.path.append("../PythonGlutWrapper")
from GlutViewController import GlutViewController

from OpenGL.GL import *
from OpenGL.GLUT import *
import Image
import math


class Wheel(object):
    """docstring for Wheel"""
    __accelerator = 0.0
    __velocity = 0.0
    __mass = 100.0
    __damper = 0.1

    def __init__(self):
        super(Wheel, self).__init__()

    def motion(self):
        self.__velocity +=\
            self.__accelerator / self.__mass\
            - self.__velocity * self.__damper

    def setAccelerator(self, acc):
        if acc > 100.0:
            self.__accelerator = 100.0
        elif acc < -100.0:
            self.__accelerator = -100.0
        else:
            self.__accelerator = acc

    def getVelocity(self):
        return self.__velocity


class TraceCar(object):
    """docstring for Car"""
    __x = 0.0
    __y = 0.0
    __rotate = math.pi/2
    __wheelBase = 5.0
    __sensorPos1X = 0.0
    __sensorPos1Y = 0.0
    __sensorPos2X = 0.0
    __sensorPos2Y = 0.0
    __sensorPos3X = 0.0
    __sensorPos3Y = 0.0

    def __init__(self, x, y):
        super(TraceCar, self).__init__()
        self.__x = x
        self.__y = y
        self.wheelR = Wheel()
        self.wheelL = Wheel()
        self.sensor1Color = (0, 0, 0)
        self.sensor2Color = (0, 0, 0)
        self.sensor3Color = (0, 0, 0)

    def x(self):
        return self.__x

    def y(self):
        return self.__y

    def setAccelerator(self, accL, accR):
        self.wheelL.setAccelerator(accL)
        self.wheelR.setAccelerator(accR)

    def getRotate(self):
        return self.__rotate

    def getSensor1Pos(self):
        return (self.__sensorPos1X, self.__sensorPos1Y)

    def getSensor2Pos(self):
        return (self.__sensorPos2X, self.__sensorPos2Y)

    def getSensor3Pos(self):
        return (self.__sensorPos3X, self.__sensorPos3Y)

    def motion(self):
        self.wheelR.motion()
        self.wheelL.motion()
        w = (self.wheelR.getVelocity() - self.wheelL.getVelocity())\
            / (2.0 * self.__wheelBase)
        self.__rotate += w
        v = (self.wheelR.getVelocity() + self.wheelL.getVelocity()) / 2.0
        self.__x += v * math.cos(self.__rotate)
        self.__y += v * math.sin(self.__rotate)
        self.__sensorPos1X = self.__x + 5.5 * math.cos(self.__rotate)
        self.__sensorPos1Y = self.__y + 5.5 * math.sin(self.__rotate)
        self.__sensorPos2X = self.__sensorPos1X + 3.0 * math.cos(self.__rotate + math.pi/2.0)
        self.__sensorPos2Y = self.__sensorPos1Y + 3.0 * math.sin(self.__rotate + math.pi/2.0)
        self.__sensorPos3X = self.__sensorPos1X + 3.0 * math.cos(self.__rotate - math.pi/2.0)
        self.__sensorPos3Y = self.__sensorPos1Y + 3.0 * math.sin(self.__rotate - math.pi/2.0)


class LineTracer(GlutViewController):
    """docstring for LineTracer"""
    def __init__(self):
        super(LineTracer, self).__init__()
        self.texture = 0
        self.courseImage = 0
        self.car = TraceCar(-125.0, 0.0)

    def display(self, deltaTime):
        # self.drawAxis(10)
        glRotate(-90, 1.0, 0.0, 0.0)
        glPushMatrix()
        self.drawCourse()

        glPushMatrix()
        self.car.sensor1Color = self.getSensor(self.car.getSensor1Pos())
        self.car.sensor2Color = self.getSensor(self.car.getSensor2Pos())
        self.car.sensor3Color = self.getSensor(self.car.getSensor3Pos())

        self.controlProcess()

        self.car.motion()
        self.camera.lock_x = self.car.x()
        self.camera.lock_z = -self.car.y()

        glTranslate(self.car.x(), self.car.y(), 0.0)
        glPushMatrix()
        glRotate(self.car.getRotate()*180.0/math.pi, 0.0, 0.0, 1.0)
        self.drawCar(self.car.sensor1Color,
                     self.car.sensor2Color,
                     self.car.sensor3Color)
        glPopMatrix()
        glPopMatrix()
        # for x in xrange(-100,100,5):
        #     for y in xrange(-100,100,5):
        #         glPushMatrix()
        #         glTranslate(x, y, 0)
        #         color = self.getSensor((x, y))
        #         self.setColor(color)
        #         glutSolidCube(1)
        #         glPopMatrix()
        glPopMatrix()

        sensorStirng = 'L: %.1f, C:%.1f, R: %.1f' % (
            self.car.sensor2Color[0],
            self.car.sensor1Color[0],
            self.car.sensor3Color[0])
        self.overlayString(sensorStirng, 2.0, 10.0)
        self.overlayString('Press ESC key to Exit', 2.0, -8.0)

    def load(self):
        print "load...."
        self.camera.tilt = math.pi/180.0*45.0
        glEnable(GL_TEXTURE_2D)

        self.courseImage = Image.open('../GrayLine.png')

        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        # Comment 2
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            4,
            self.courseImage.size[0],
            self.courseImage.size[1],
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            self.courseImage.convert('RGBA').tostring())
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)

    def motion(self, x, y):
        # print "MouseMove: x: %d, y: %d" % (x, y)
        movedX = x - self.mouseState.x
        movedY = y - self.mouseState.y
        if self.mouseState.button == 0 & self.mouseState.pressed:
            self.camera.pan += float(-movedX)/100.0
            self.camera.tilt += float(movedY)/100.0
        if self.camera.tilt > math.pi/2.0:
            self.camera.tilt = math.pi/2.0
        if self.camera.tilt < math.pi/180.0*5.0:
            self.camera.tilt = math.pi/180.0*5.0
        self.mouseState.x = x
        self.mouseState.y = y

    def drawCourse(self):
        vx, vy = 256.0, 256.0
        tx, ty = 1, 1
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glBegin(GL_POLYGON)
        glColor3f(0, 0, 0)
        glTexCoord2d(0.0, 1.0)
        glVertex3f(-vx, -vy, 0.0)

        glTexCoord2d(1.0, 1.0)
        glVertex3f(vx, -vy, 0.0)

        glTexCoord2d(1.0, 0.0)
        glColor3f(1, 1, 1)
        glVertex3f(vx, vy, 0.0)

        glTexCoord2d(0.0, 0.0)
        glVertex3f(-vx, vy, 0.0)
        glEnd()
        glBindTexture(GL_TEXTURE_2D, 0)

    def getSensor(self, pos):
        imageX = float(pos[0] + 256) / 512.0 * self.courseImage.size[0]
        imageY = -float(pos[1] - 256) / 512.0 * self.courseImage.size[1]
        # print imageX, ppimageY
        if 0 < imageX < self.courseImage.size[1] and 0 < imageY < self.courseImage.size[1]:
            rgb = [0.0, 0.0, 0.0]
            for x in (-1, 0, 1):
                for y in (-1, 0, 1):
                    temp = self.courseImage.getpixel((imageX+x, imageY+y))
                    rgb = [rgb[i] + temp[i]for i in range(len(rgb))]
            pixel = (float(rgb[0])/9.0/255.0,
                     float(rgb[1])/9.0/255.0,
                     float(rgb[2])/9.0/255.0)
            return pixel
        else:
            return (0, 0, 0)

    def drawCar(self, sensor1, sensor2, sensor3):
        # self.drawAxis(10)
        # draw car body
        glPushMatrix()
        self.setColor((0.8, 0.0, 0.0))
        glTranslate(0.0, 0.0, 4.5)
        glutSolidCube(8)
        glPopMatrix()
        # draw sensor base
        glPushMatrix()
        self.setColor(sensor1)
        glTranslate(5.0, 0.0, 0.5)
        self.setColor((0.4, 0.4, 0.4))
        glutSolidCube(3)
        glTranslate(0.0, 3.0, 0.0)
        glutSolidCube(3)
        glTranslate(0.0, -6.0, 0.0)
        glutSolidCube(3)
        glPopMatrix()
        # draw sensors
        glPushMatrix()
        glTranslate(5.5, 0.0, 2.2)
        self.setColor(sensor1)
        glutSolidCube(1)
        glTranslate(0.0, 3.0, 0.0)
        self.setColor(sensor2)
        glutSolidCube(1)
        glTranslate(0.0, -6.0, 0.0)
        self.setColor(sensor3)
        glutSolidCube(1)
        glPopMatrix()
        # draw car wheels
        glPushMatrix()
        glTranslate(0.0, 0.0, 3.0)
        glRotate(90, 0.0, 1.0, 0.0)
        glRotate(90, 1.0, 0.0, 0.0)
        glTranslate(0.0, 0.0, 5.0)
        self.setColor((0.2, 0.2, 0.2))
        glutSolidTorus(0.7, 2.5, 16, 20)
        glTranslate(0.0, 0.0, -10.0)
        glutSolidTorus(0.7, 2.5, 16, 20)
        glPopMatrix()

    def controlProcess(self):
        # if not hasattr(self, 'acc'):
        #     self.acc = 0
        blightness = \
            0.299 * self.car.sensor1Color[0]\
            + 0.587 * self.car.sensor1Color[1]\
            + 0.114 * self.car.sensor1Color[2]
        # ref = 0.4
        # diff = ref - blightness
        # self.acc += diff * 0.02
        # out = diff * 0.2 + self.acc + 0.5
        # print out, self.acc, diff
        # self.car.setAccelerator(20.0*(1.0-out), 20.0*out)

        # if blightness > 0.9:
        #     self.car.setAccelerator(20.0, 0.0)
        # else:
        #     self.car.setAccelerator(0.0, 20.0)


if __name__ == '__main__':
    vi = LineTracer()
    vi.startFramework()
