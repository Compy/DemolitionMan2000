'''
Created on Dec 18, 2012

@author: compy
'''
from direct.task import Task
from direct.gui.DirectGui import *
from pandac.PandaModules import *
from direct.gui.OnscreenText import OnscreenText,TextNode
from gamescreen import GameScreen
from video.uielements import Menu, Sprite
from direct.interval.IntervalGlobal import *
from direct.interval.LerpInterval import LerpFunc
from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
import os, sys, locale
from functools import partial

class SimonSaysScreen(GameScreen):

    bonus_items = []
    anim_sequence = None
    def __init__(self, screen_manager):
        super(SimonSaysScreen, self).__init__(screen_manager, "simon_says_screen")
        self.ss_off = OnscreenImage(image = 'assets/images/ss_all_off.png', 
                                         pos = (0, 0, -0.1), 
                                         parent = self.node2d, 
                                         scale=(1.3,1,0.8))
        self.ss_blue = OnscreenImage(image = 'assets/images/ss_blue.png', 
                                         pos = (0, 0, -0.1), 
                                         parent = self.node2d, 
                                         scale=(1.3,1,0.8))
        self.ss_green = OnscreenImage(image = 'assets/images/ss_green.png', 
                                         pos = (0, 0, -0.1), 
                                         parent = self.node2d, 
                                         scale=(1.3,1,0.8))
        self.ss_red = OnscreenImage(image = 'assets/images/ss_red.png', 
                                         pos = (0, 0, -0.1), 
                                         parent = self.node2d, 
                                         scale=(1.3,1,0.8))
        self.ss_yellow = OnscreenImage(image = 'assets/images/ss_yellow.png', 
                                         pos = (0, 0, -0.1), 
                                         parent = self.node2d, 
                                         scale=(1.3,1,0.8))
        
        self.ss_inst = OnscreenImage(image = 'assets/images/simon_says_inst.png', 
                                         pos = (0, 0, -0.1), 
                                         parent = self.node2d, 
                                         scale=(1.3,1,0.8))
        
        self.ss_inst2 = OnscreenImage(image = 'assets/images/ss_r2.png', 
                                         pos = (0, 0, -0.1), 
                                         parent = self.node2d, 
                                         scale=(1.3,1,0.8))
        
        self.ss_off.hide()
        self.ss_blue.hide()
        self.ss_green.hide()
        self.ss_red.hide()
        self.ss_yellow.hide()
        self.ss_inst.hide()
        self.ss_inst2.hide()
        
        self.ss_award = OnscreenText("10,000,000",
                                       1,
                                       font=base.fontLoader.load('BigDots.ttf'),
                                       fg=((206.0/255.0),(0.0/255.0),(224.0/255.0),1),
                                       pos=(0,0.5),
                                       align=TextNode.ACenter,
                                       scale=.2,
                                       mayChange=True,
                                       parent=self.node2d)


    def show(self):        
        
        # Call our base class show method now so it can render anything it wants
        super(SimonSaysScreen, self).show()
        
        self.ss_off.hide()
        self.ss_blue.hide()
        self.ss_green.hide()
        self.ss_red.hide()
        self.ss_yellow.hide()
        self.ss_inst.hide()
        self.ss_award.hide()

    def hide(self):
        """
        Called when the screen manager wants to remove this screen from the display.
        
        We have no choice but to obey when this method is called. So hide our background.
        
        Our models will be hidden automatically as the 3d nodes are removed from the render tree
        """
        super(SimonSaysScreen, self).hide()
        
    def show_color(self, color):
        base.display_queue.put_nowait(partial(self._ts_show_color, color=color))
        
    def hide_color(self):
        base.display_queue.put_nowait(partial(self._ts_hide_color))
        
    def show_award(self, award):
        base.display_queue.put_nowait(partial(self._ts_show_award, award=award))
        
    def hide_award(self):
        base.display_queue.put_nowait(partial(self._ts_hide_award))
        
    def _ts_hide_award(self):
        self.ss_award.hide()
        
    def _ts_show_award(self, award):
        self.ss_award.setText(str(base.format_score(award)))
        self.ss_award.show()
        
    def show_instructions(self):
        base.display_queue.put_nowait(partial(self._ts_show_inst))
        
    def hide_instructions(self):
        base.display_queue.put_nowait(partial(self._ts_hide_inst))
        
    def _ts_hide_inst(self):
        self.ss_inst.hide()
        
    def _ts_show_inst(self):
        self.ss_inst.show()
        
    def show_instructions2(self):
        base.display_queue.put_nowait(partial(self._ts_show_inst2))
        
    def hide_instructions2(self):
        base.display_queue.put_nowait(partial(self._ts_hide_inst2))
        
    def _ts_hide_inst2(self):
        self.ss_inst2.hide()
        
    def _ts_show_inst2(self):
        self.ss_inst2.show()
        
        
    def _ts_show_color(self, color):
        self.ss_off.hide()
        self.ss_blue.hide()
        self.ss_green.hide()
        self.ss_red.hide()
        self.ss_yellow.hide()
        
        if color == "blue": self.ss_blue.show()
        elif color == "green": self.ss_green.show()
        elif color == "red": self.ss_red.show()
        elif color == "yellow": self.ss_yellow.show()
        else: self.ss_off.show()
        
    def _ts_hide_color(self):
        self.ss_off.show()
        self.ss_blue.hide()
        self.ss_green.hide()
        self.ss_red.hide()
        self.ss_yellow.hide()
        