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

class BonusScreen(GameScreen):

    bonus_items = []
    anim_sequence = None
    def __init__(self, screen_manager):
        super(BonusScreen, self).__init__(screen_manager, "bonus_screen")
        
        self.anim_sequence = Sequence()
        #(-0.9812,0.70500)
        self.imageObject = OnscreenImage(image = 'assets/images/bonus_bg.png', pos = (0, 0, -0.1), parent = self.node2d, scale=(1.3,1,0.8))
        
    def clear_bonus_items(self):
        for bonus_item in self.bonus_items:
            bonus_item['name_text'].destroy()
            bonus_item['score_text'].destroy()
        self.bonus_items = []
        self.anim_sequence = Sequence()
        
    def add_bonus_item(self, name, score, count = False):
        
        ypos = 0.35 - (len(self.bonus_items) * 0.16)
        
        name_text=OnscreenText(name,
                                       1,
                                       font=base.fontLoader.load('motorwerk.ttf'),
                                       pos=(-1.2,ypos),
                                       fg=(1,0,0,0),
                                       align=TextNode.ALeft,
                                       scale=.15,
                                       mayChange=True,
                                       parent=self.node2d)
        score_text=OnscreenText(str(locale.format("%d", score, grouping=True)),
                                       1,
                                       font=base.fontLoader.load('motorwerk.ttf'),
                                       pos=(1.2,ypos),
                                       fg=(1,1,1,0),
                                       align=TextNode.ARight,
                                       scale=.15,
                                       mayChange=True,
                                       parent=self.node2d)
        
        self.bonus_items.append({'name': name, 'score': score, 'count': count, 'name_text': name_text, 'score_text': score_text})
        
        self.anim_sequence.append(LerpFunc(self.fade_text_in, fromData=0, toData=1.0, duration=0.4, blendType='easeIn', extraArgs=[name_text, score_text,(1,0,0,1),(1,1,1,1)]))
        

    def fade_text_in(self, t, name_text, score_text, name_text_color, score_text_color):
        try:
            name_text.setFg((name_text_color[0],name_text_color[1],name_text_color[2],t))
            score_text.setFg((score_text_color[0],score_text_color[1],score_text_color[2],t))
        except:
            pass
        
    def start_animation(self):
        self.anim_sequence.start()

    def show(self):        
        
        # Call our base class show method now so it can render anything it wants
        super(BonusScreen, self).show()
        

    def hide(self):
        """
        Called when the screen manager wants to remove this screen from the display.
        
        We have no choice but to obey when this method is called. So hide our background.
        
        Our models will be hidden automatically as the 3d nodes are removed from the render tree
        """
        super(BonusScreen, self).hide()
        
        