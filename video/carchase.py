'''
Created on Dec 10, 2012

@author: compy
'''

from direct.gui.OnscreenText import OnscreenText, TextNode
from direct.gui.OnscreenImage import OnscreenImage
from gamescreen import GameScreen
from direct.gui.DirectGui import *
from direct.task.Task import Task
from direct.stdpy.file import *
from uielements import Sprite
from panda3d.core import *
import platform
import sys, imp, os, locale


class CarChaseScreen(GameScreen):
    tex = None
    def __init__(self, screen_manager):
        super(CarChaseScreen, self).__init__(screen_manager, "carchase")
        
        #self._testText=OnscreenText("Attract Screen 2",
        #                               1,
        #                               fg=(1,1,1,1),
        #                               pos=(0,0),
        #                               align=TextNode.ACenter,
        #                               scale=.1,
        #                               mayChange=False,
        #                               parent=self.node2d)
        
        
        self.tex = MovieTexture("carchase")
        assert self.tex.read("assets/video/dm_carchase_end.mp4"), "Failed to load video!"
        
        self.clipSound=base.loader.loadSfx("assets/video/dm_carchase_end.wav")
        #self.tex.synchronizeTo(mySound)
        
        # Set up a fullscreen card to set the video texture on.
        cm = CardMaker("carchase");
        #cm.setFrame(-1,1,-1,1)
        cm.setFrameFullscreenQuad()
        cm.setUvRange(self.tex)
        card = NodePath(cm.generate())
        card.reparentTo(self.node2d)
        card.setTexture(self.tex)
        card.setBin("fixed",-20)
        #card.setTexScale(TextureStage.getDefault(), self.tex.getTexScale())
        #card.setPos(-0.4,0,0)
        
    def show(self):
        super(CarChaseScreen, self).show()
        # Load the texture. We could use loader.loadTexture for this,
        # but we want to make sure we get a MovieTexture, since it
        # implements synchronizeTo.
        
        self.tex.setLoop(False)
        self.tex.stop()
        self.tex.play()
        self.clipSound.stop()
        self.clipSound.play()
        
        
    def hide(self):
        super(CarChaseScreen, self).hide()
        if self.tex != None:
            self.tex.setTime(0)