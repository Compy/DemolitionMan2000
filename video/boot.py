'''
Created on Dec 18, 2012

@author: compy
'''
from direct.task import Task
from direct.gui.DirectGui import *
from pandac.PandaModules import *
from direct.gui.OnscreenText import OnscreenText,TextNode
from gamescreen import GameScreen
from video.uielements import Menu
from panda3d.core import Vec3, DirectionalLight
from uielements import Sprite, DMDSpriteFont
import os, sys

from direct.showbase.PythonUtil import *

class BootScreen(GameScreen):
    '''
    classdocs
    '''


    def __init__(self, screen_manager):
        '''
        Constructor
        '''
        super(BootScreen, self).__init__(screen_manager, "boot_screen")
        self.loading_text=OnscreenText("LOADING",
                                       1,
                                       fg=((51/255.0),(102/255.0),1,1),
                                       pos=(0,-0.4),
                                       align=TextNode.ACenter,
                                       scale=.3,
                                       mayChange=1,
                                       font=base.fontLoader.load("dotmatrix.ttf"),
                                       parent=self.node2d)
        self.loading_bar = DirectWaitBar(text = "", 
                                         value = 0, 
                                         pos = (0,.8,-0.8), 
                                         scale = (1, 1, 0.1), 
                                         barColor=(0,0,255,255), 
                                         frameColor=(0,0,0,0),
                                         parent=self.node2d)
        
        
        # Scale the X value to match our screen width
        self.loading_bar.setSx(1.35)

        cube = base.loader.loadModel("assets/models/cube.egg")
        cube.setPos(-0.4,40,0)
        #cube.setScale(0.09,0.09,0.09)
        myInterval4 = cube.hprInterval( 7, Vec3(360,-10,0) ).loop()
        
        cube.setP(-10)
        
        if base.displayFlipped:
            cube.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullCounterClockwise))
        
        cube.reparentTo(self.node)
        
        dlight = DirectionalLight('my dlight')
        dlnp = render.attachNewNode(dlight)
        cube.setLight(dlnp)
        
        """
        self.explosion = Sprite(
                                parent=self.node, 
                                file_name="assets/sprites/lightning/lightning_", 
                                file_type="png", 
                                num_frames=16, 
                                int_padding=2,
                                scale=(1,1,1))
        self.explosion.setPos(0,5,0)
        self.explosion.fps = 18
        """
        
        #self.explosion.setLight(dlnp)

    
    def incLoadingProgress(self, by_value = 1):
        if (self.loading_bar['value'] >= 100):
            return
        
        
        self.loading_bar['value'] += by_value
        self._updateDisplay()
        
    def setLoadingProgress(self, value):
        self.loading_bar['value'] = value
        self._updateDisplay()
        
    def getLoadingProgress(self):
        return self.loading_bar['value']
        
    def _updateDisplay(self):
        self.loading_text.setText("LOADING (" + str(self.loading_bar['value']) + "%)")
        
    def show(self):
        super(BootScreen, self).show()
        
    def hide(self):
        super(BootScreen, self).hide()