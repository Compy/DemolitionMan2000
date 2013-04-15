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
import sys, imp, os, locale, random


class ClawScreen(GameScreen):
    tex = None
    def __init__(self, screen_manager):
        super(ClawScreen, self).__init__(screen_manager, "claw")
        
        self.positions = []
        #self.positions.append((-0.78320,0,0.29866))
        #elf.positions.append((-0.64843,0,0.27343))
        #self.positions.append((-0.5,0,0.28385))
        #self.positions.append((-0.32031,0,0.38802))
        #self.positions.append((-0.13867,0,0.58333))
        
        self.positions.append((-1.08320,0,0.29866))
        self.positions.append((-0.84843,0,0.27343))
        self.positions.append((-0.6,0,0.28385))
        self.positions.append((-0.39,0,0.38802))
        self.positions.append((-0.23867,0,0.58333))

        self.claw_5combos = OnscreenImage(image = 'assets/images/claw_5combos.png', pos = self.positions[0],
                                   parent=self.node2d,
                                   scale=.1)
        self.claw_eb = OnscreenImage(image = 'assets/images/claw_eb.png', pos = self.positions[1],
                                   parent=self.node2d,
                                   scale=.1)
        self.claw_10m = OnscreenImage(image = 'assets/images/claw_10m.png', pos = self.positions[0],
                                   parent=self.node2d,
                                   scale=.1)
        self.claw_addexplode = OnscreenImage(image = 'assets/images/claw_addexplode.png', pos = self.positions[3],
                                   parent=self.node2d,
                                   scale=.1)
        self.claw_bonusx = OnscreenImage(image = 'assets/images/claw_bonusx.png', pos = self.positions[2],
                                   parent=self.node2d,
                                   scale=.1)
        self.claw_carchase = OnscreenImage(image = 'assets/images/claw_carchase.png', pos = self.positions[2],
                                   parent=self.node2d,
                                   scale=.1)
        self.claw_cfb = OnscreenImage(image = 'assets/images/claw_cfb.png', pos = self.positions[4],
                                   parent=self.node2d,
                                   scale=.1)
        self.claw_lock = OnscreenImage(image = 'assets/images/claw_lock.png', pos = self.positions[1],
                                   parent=self.node2d,
                                   scale=.1)
        self.claw_superjets = OnscreenImage(image = 'assets/images/claw_superjets.png', pos = self.positions[3],
                                   parent=self.node2d,
                                   scale=.1)
        self.claw_tz = OnscreenImage(image = 'assets/images/claw_tz.png', pos = self.positions[4],
                                   parent=self.node2d,
                                   scale=.1)
        
        self.claw_5combos.hide()
        self.claw_eb.hide()
        self.claw_10m.hide()
        self.claw_addexplode.hide()
        self.claw_bonusx.hide()
        self.claw_carchase.hide()
        self.claw_cfb.hide()
        self.claw_lock.hide()
        self.claw_superjets.hide()
        self.claw_tz.hide()
        
        self.awards = []
        
    def show(self):
        super(ClawScreen, self).show()
        self.fill_slots()
        
    def hide(self):
        super(ClawScreen, self).hide()
        
    def get_slots(self):
        return self.awards
        
    def fill_slots(self):
        self.awards = []
        self.claw_5combos.hide()
        self.claw_eb.hide()
        self.claw_10m.hide()
        self.claw_addexplode.hide()
        self.claw_bonusx.hide()
        self.claw_carchase.hide()
        self.claw_cfb.hide()
        self.claw_lock.hide()
        self.claw_superjets.hide()
        self.claw_tz.hide()
        
        # Pos 1: 5 COMBOS | 10M
        # POS 2: EB | LOCK
        # POS 3: CAR CHASE | BONUS X
        # POS 4: SUPERJETS | ADD EXPLODE
        # POS 5: CFB | TZ
        
        for i in range(5):
            r = random.randint(1,2)
            if i == 0:
                if r == 1:
                    self.claw_5combos.show()
                    self.awards.append("5 combos")
                else: 
                    self.claw_10m.show()
                    self.awards.append("10 million")
            if i == 1:
                if r == 1: 
                    self.claw_eb.show()
                    self.awards.append("extra ball")
                else: 
                    self.claw_lock.show()
                    self.awards.append("lock")
            if i == 2:
                if r == 1:
                    self.claw_carchase.show()
                    self.awards.append("car chase")
                else:
                    self.claw_bonusx.show()
                    self.awards.append("bonus x")
            if i == 3:
                if r == 1:
                    self.claw_superjets.show()
                    self.awards.append("superjets")
                else:
                    self.claw_addexplode.show()
                    self.awards.append("add explode")
            if i == 4:
                if r == 1:
                    self.claw_cfb.show()
                    self.awards.append("cfb")
                else:
                    self.claw_tz.show()
                    self.awards.append("tz")
        