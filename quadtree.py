    # -*- coding:utf8 -*-
import pygame
from pygame.locals import *
from math import ceil, floor, atan2, degrees, radians, sqrt, cos, sin

#States
UNKNOWN = 0
MISTO = 1
CHEIO = 2
VAZIO = 3

#Mode
EDGES = 0
NO_EDGES = 1

class Node(object):
    NE = NO = SE = SO = None

    def __init__(self, top=-100000, left=-100000, w=200000, h=200000, tipo = UNKNOWN):
        self.top = top
        self.left = left
        self.width = w
        self.height = h
        self.__tipo__ = tipo
        self.himm = 0

    
    @property
    def tipo(self):
        return self.__tipo__


    @tipo.setter
    def tipo(self,value):
        if not value in [UNKNOWN,VAZIO, CHEIO,MISTO]:
            raise Exception("NODE: Type not valid")
        
        if self.__tipo__ == CHEIO:
            self.addHIMM()
        elif self.__tipo__ == VAZIO:
            self.subHIMM()
        else:
            self.__tipo__ = value


    def addHIMM(self):
        self.himm += 3
        if self.himm > 15:
            self.himm = 15
        
        if self.himm >= 6:
            self.__tipo__ = CHEIO


    def subHIMM(self):
        self.himm -= 1
        if self.himm < 0:
            self.himm = 0

        if self.himm < 6:
            self.__tipo__ = VAZIO


    def putObstaculo(self, p, value = CHEIO, minSize = 100):
        if self.tipo == value:
            return
        w,h = self.width/2., self.height/2.
        if self.tipo in [UNKNOWN, VAZIO, CHEIO]:
            self.NO, self.NE, self.SO, self.SE = (Node(self.top,self.left, w,h,self.tipo),
                                                    Node(self.top,self.left+w, w,h,self.tipo),
                                                    Node(self.top+h,self.left, w,h,self.tipo),
                                                    Node(self.top+h,self.left+w, w,h,self.tipo))
            self.tipo = MISTO

        if self.tipo == MISTO:
            if w + self.left > p[0]:
                if h + self.top > p[1]:
                    if w > minSize and h > minSize:
                        self.NO.putObstaculo(p,value)
                    else:
                        self.NO.tipo = value
                else:
                    if w > minSize and h > minSize:
                        self.SO.putObstaculo(p,value)
                    else:
                        self.SO.tipo = value
            else:
                if h + self.top > p[1]:
                    if w > minSize and h > minSize:
                        self.NE.putObstaculo(p,value)
                    else:
                        self.NE.tipo = value
                else:
                    if w > minSize and h > minSize:
                        self.SE.putObstaculo(p,value)
                    else: 
                        self.SE.tipo = value

        if (self.tipo == MISTO) and (self.NO.tipo == self.NE.tipo == self.SE.tipo == self.SO.tipo != MISTO):
            maxi = max(self.NE.himm,self.NO.himm,self.SO.himm,self.SE.himm)
            mini = min(self.NE.himm,self.NO.himm,self.SO.himm,self.SE.himm)
            
            if (maxi-mini) < 10:
                self.tipo = self.NE.tipo
                self.himm = maxi
                self.NE = self.NO = self.SE = self.SO = None


    def isInside(self,p):
        if (self.top <= p[1] < self.height+self.top) and (self.left <= p[0] < self.width+self.left):
            return True
        return False


    def drawNode(self,screen,minRect, celSize, mode = EDGES):

        s = screen.get_size()

        (minx,miny),(maxx,maxy) = minRect
        sx, sy = celSize
        #Arrumar para desenhar somente o que for visivel
        #if self.isInside((minx,miny)) or self.isInside((minx,maxy)) or self.isInside((maxx,maxy)) or self.isInside((maxx,miny)):

        p = floor(self.left - minx)*sx, s[1] - floor(self.top - miny)*sy
        size = ceil(self.width*sx),-ceil(self.height*sy)
        if self.tipo == CHEIO:
            pygame.draw.rect(screen,(0,0,0),pygame.Rect(p, size),0)
            if mode == EDGES:
                pygame.draw.rect(screen,(0,0,0),pygame.Rect(p, size),1)
        elif self.tipo == VAZIO:
            pygame.draw.rect(screen,(255,255,255),pygame.Rect(p, size),0)
            if mode == EDGES:
                pygame.draw.rect(screen,(0,0,0),pygame.Rect(p, size),1)
        elif self.tipo == UNKNOWN and mode == EDGES:
            pygame.draw.rect(screen,(0,0,0),pygame.Rect(p, size),1)
        elif self.tipo == MISTO:
            self.NO.drawNode(screen,minRect,celSize,mode)
            self.SO.drawNode(screen,minRect,celSize,mode)
            self.NE.drawNode(screen,minRect,celSize,mode)
            self.SE.drawNode(screen,minRect,celSize,mode)

    def __len__(self):
        if self.tipo in [UNKNOWN,VAZIO,CHEIO]:
            return 1
        if self.tipo == MISTO:
            return 1 + len(self.NO) + len(self.NE) + len(self.SO) + len(self.SE)




class Quadtree(Node):

    minSize = 100
    scale = 1.
    center = (0.,0.)


    def __init__(self, top=-100000, left=-100000, w=200000, h=200000, tipo = UNKNOWN):
        super(Quadtree,self).__init__(top, left, w, h, tipo)
        self.mode = EDGES


    def putObstaculoSweep(self,roboPos,leituras):
        x,y = roboPos[0], roboPos[1]
        pad = 5500.

        minx, miny, maxx, maxy = x - pad, y - pad, x + pad, y + pad

        variacao = 100
        for nx in xrange(int(minx),int(maxx),self.minSize):
            for ny in xrange(int(miny),int(maxy),self.minSize):

                center = nx, ny
                angle = degrees(atan2(center[1]-roboPos[1],center[0]-roboPos[0])) - roboPos[2]

                angle %= 360
                if angle> 180:
                    angle -= 360

                if -90. <= angle <= 90.:

                    r = leituras[int(90-angle)]
                    r = min(r,5000)
            
                    d = sqrt(pow(center[1]-roboPos[1],2) + pow(center[0]-roboPos[0],2))

                    if r < 5000 and r-variacao < d < r+variacao:
                        self.putObstaculo(center,CHEIO,self.minSize)
                    elif d <= r-variacao:
                        self.putObstaculo(center,VAZIO,self.minSize)


    def draw(self,screen):

        s = screen.get_size()
        sx = self.scale*float(s[0])/self.width
        sy = self.scale*float(s[1])/self.height


        halfWidthMap = ceil(self.width/(2.*self.scale))
        halfHeightMap = ceil(self.height/(2.*self.scale))

        minx,miny,maxx,maxy =  (self.center[0]-halfWidthMap,
                                self.center[1]-halfHeightMap,
                                self.center[0]+halfWidthMap,
                                self.center[1]+halfHeightMap)
        celSize = sx, sy
        minRect = (minx,miny),(maxx,maxy)

        self.drawNode(screen,minRect,celSize,self.mode)


    def drawRobot(self,screen,x,y,th,leituras):

        s = screen.get_size()
        sx = self.scale*float(s[0])/self.width
        sy = self.scale*float(s[1])/self.height

        halfWidthMap = ceil(self.width/(2.*self.scale))
        halfHeightMap = ceil(self.height/(2.*self.scale))

        minx,miny,maxx,maxy =  (self.center[0]-halfWidthMap,
                                self.center[1]-halfHeightMap,
                                self.center[0]+halfWidthMap,
                                self.center[1]+halfHeightMap)

        robot = int(sx*(x-minx)), s[1] - int(sy*(y-miny))
        pygame.draw.circle(screen,(255,0,0),robot,int(1.*self.scale),0)
        if leituras != []:
            dLaser = [robot]
            angle = 90+th
            for r in leituras:
                if r > 5000:
                    r = 5000
                dLaser.append((
                                sx*(x + r*cos(radians(angle)) - minx) ,
                                s[1] - sy*(y + r*sin(radians(angle)) - miny)))
                angle -= 1
            
            pygame.draw.polygon(screen,(0,0,255),dLaser,0)

