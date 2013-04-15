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
import os, sys, locale, random

class MatchScreen(GameScreen):

    bonus_items = []
    anim_sequence = None
    def __init__(self, screen_manager):
        super(MatchScreen, self).__init__(screen_manager, "bonus_screen")
        
        self.anim_sequence = Sequence()
        #(-0.9812,0.70500)
        title=OnscreenText("Match",
                                           1,
                                           font=base.fontLoader.load('motorwerk.ttf'),
                                           pos=(-1.2,0.70),
                                           fg=(1,0,0,1),
                                           align=TextNode.ALeft,
                                           scale=.25,
                                           mayChange=False,
                                           parent=self.node2d)
        self.digits=OnscreenText("",
                                           1,
                                           font=base.fontLoader.load('motorwerk.ttf'),
                                           pos=(-1.2,0.5),
                                           fg=(1,0,0,1),
                                           align=TextNode.ALeft,
                                           scale=.15,
                                           mayChange=True,
                                           parent=self.node2d)
        
        self.match=OnscreenText("",
                                           1,
                                           font=base.fontLoader.load('motorwerk.ttf'),
                                           pos=(0.65,-0.8),
                                           fg=(1,1,1,1),
                                           align=TextNode.ALeft,
                                           scale=.15,
                                           mayChange=True,
                                           parent=self.node2d)
        
        self.drop_idx = 0
        self.imgs = []
        
    def set_digits(self, digits):
        print "SET DIGITS " + str(digits)
        dtext = ""
        for d in digits:
            print "DIGITS " + str(d)
            dtext += str(d) + "\n"
            
        print "DTEXT " + dtext
                    
        self.digits.setText(dtext)
            
        self.digits.show()
            
            
        #self.anim_sequence.append(LerpFunc(self.fade_text_in, fromData=0, toData=1.0, duration=0.4, blendType='easeIn', extraArgs=[name_text,(1,0,0,1)]))
            

    def fade_text_in(self, t, name_text, name_text_color):
        try:
            name_text.setFg((name_text_color[0],name_text_color[1],name_text_color[2],t))
        except:
            pass
        
    def start_animation(self):
        #self.anim_sequence.start()
        pass
        
    def show(self):
        super(MatchScreen, self).show()
        self.start_animation()
        self.drop_idx = 0
        self.match.setText("")
        for img in self.imgs:
            img.destroy()
            
        self.imgs = []
        
    def hide(self):
        super(MatchScreen, self).hide()
        for img in self.imgs:
            img.destroy()
            
        self.imgs = []
        
    def drop(self):
        print "DROP IDX " + str(self.drop_idx) 
        p =  (-0.7 + (self.drop_idx * 0.3), 0, 1.4)
        p_end = (p[0],p[1],-1.5)
        img = OnscreenImage(image = 'assets/images/icecube.png', pos = p, parent = self.node2d, scale=(0.1,1,0.1))
        self.imgs.append(img)
        
        LerpPosInterval(img,
                        0.7,
                        pos=p_end,
                        blendType='easeIn'
                     ).start()
        
        self.drop_idx += 1
        
    def explode(self):
        print "EXPLODE"
        self.explosion = Sprite(
                                parent=self.node, 
                                file_name="assets/sprites/blue_explosion/blue_explosion_", 
                                file_type="png", 
                                num_frames=13, 
                                int_padding=2,
                                scale=(5,5,5))
        self.explosion.fps=24
        self.explosion.setPos(8,40,-2)
        self.explosion.play(loops=1)
        base.taskMgr.doMethodLater(0.5, self.showMatchNumber, 'match_show')
        
    def showMatchNumber(self,task):
        random_match = random.randint(0,9)
        if random_match < 10:
            r = str(random_match) + "0"
        else:
            r = str(random_match)
        self.match.setText(r)
        return Task.done
        
        