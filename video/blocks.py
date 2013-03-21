'''
Created on Dec 18, 2012

@author: compy
'''
from direct.task import Task
from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText,TextNode
from gamescreen import GameScreen
from video.uielements import Menu
from panda3d.core import Vec3, DirectionalLight
import os, sys

class BlocksScreen(GameScreen):
    '''
    classdocs
    '''

    def __init__(self, screen_manager):
        '''
        Constructor
        '''
        super(BlocksScreen, self).__init__(screen_manager, "blocks_screen")
        
        self.cubes = []
        
        for i in range(3):
        
            cube = base.loader.loadModel("assets/models/powerup.egg")
            zpos = i * (0.8)
            cube.setPos(0,10,zpos)
            cube.setScale(0.02,0.02,0.02)
            #myInterval4 = cube.hprInterval( 1, Vec3(360,-10,0) ).loop()
            
            cube.setP(10)
            cube.setH(5)
            
            cube.reparentTo(self.node)
            
            self.cubes.append(cube)
        
            dlight = DirectionalLight('my dlight')
            dlnp = render.attachNewNode(dlight)
            cube.setLight(dlnp)
