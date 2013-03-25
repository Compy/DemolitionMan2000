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

class SanAngelesScreen(GameScreen):

    def __init__(self, screen_manager):
        super(SanAngelesScreen, self).__init__(screen_manager, "wtsa_screen")
        
        self.stack_screen = self.screen_manager.getScreen("stack")
        
        self.instructions = OnscreenImage(image = 'assets/images/wtsa.png',
                                         pos = (0, 0, 0),
                                         parent = self.node2d,
                                         scale = (0.8, 0.8, 0.8))
        self.instructions.setTransparency(TransparencyAttrib.MAlpha)

    def show_instructions(self):
        self.instructions.show()
    
    def hide_instructions(self):
        self.instructions.hide()

    def show(self):        
        
        # Call our base class show method now so it can render anything it wants
        super(SanAngelesScreen, self).show()

    def hide(self):
        """
        Called when the screen manager wants to remove this screen from the display.
        
        We have no choice but to obey when this method is called. So hide our background.
        
        Our models will be hidden automatically as the 3d nodes are removed from the render tree
        """
        super(SanAngelesScreen, self).hide()
        
    def mode_started(self):
        self.clear_stacks()
        self.stack_screen.place_model(model_name = "burger.bam",
                         scale = (0.4, 0.4, 0.4),
                         pos = "right_ramp",
                         rotate = True,
                         rotspeed = 4,
                         mode = "wtsa")
        
        self.stack_screen.place_model(model_name = "scanner.egg",
                         scale = (0.6, 0.6, 0.6),
                         pos = "left_ramp",
                         rotate = True,
                         rotspeed = 4,
                         mode = "wtsa")
        
        self.stack_screen.place_model(model_name = "shell.bam",
                         scale = (0.4, 0.4, 0.4),
                         pos = "left_ramp",
                         rotate = True,
                         rotspeed = 3,
                         mode = "wtsa")
        
        self.stack_screen.place_model(model_name = "bonus_x.bam",
                         scale = (0.7, 0.7, 0.7),
                         pos = "right_ramp",
                         rotate = True,
                         rotspeed = 3,
                         mode = "wtsa")
        
        self.stack_screen.place_model(model_name = "burger.bam",
                         scale = (0.4, 0.4, 0.4),
                         pos = "center_ramp",
                         rotate = True,
                         rotspeed = 2,
                         p = 10,
                         mode = "wtsa")
        
        self.screen_manager.showScreen("stack")
        
    def explode(self, position):
        self.explosion = Sprite(self.node, "assets/sprites/explosion/explosion_", "png", 29, 2, scale = (1,1,1), fps = 50)
        self.explosion.setPos(position[0], position[1] - 112, position[2] + 28)
        self.explosion.play()
        
    def explode_right(self):
        if not self.stack_screen.location_has_object("right_ramp", mode="wtsa"):
            return False
        
        self.explosion = Sprite(self.node, "assets/sprites/explosion/explosion_", "png", 29, 2, scale = (1,1,1), fps = 50)
        self.explosion.setPos(2.8,10,8.2)
        self.explosion.play()
        self.stack_screen.remove_bottom_model("right_ramp")
        return True
    
    def explode_left(self):
        if not self.stack_screen.location_has_object("left_ramp", mode="wtsa"):
            return False
        
        self.explosion = Sprite(self.node, "assets/sprites/explosion/explosion_", "png", 29, 2, scale = (1,1,1), fps = 50)
        self.explosion.setPos(-1.3,10,6.9)
        self.explosion.play()
        self.stack_screen.remove_bottom_model("left_ramp")
        return True
        
    def explode_center(self):
        if not self.stack_screen.location_has_object("center_ramp", mode="wtsa"):
            return False
        
        self.explosion = Sprite(self.node, "assets/sprites/explosion/explosion_", "png", 29, 2, scale = (1,1,1), fps = 50)
        self.explosion.setPos(0.1,8,8.5)
        self.explosion.play()
        self.stack_screen.remove_bottom_model("center_ramp")
        
    def generate_new_barrel(self):
        self.stack_screen.place_model(model_name = "barrel.bam",
                         scale = (0.2, 0.2, 0.2),
                         pos = "center_ramp",
                         rotate = True,
                         rotspeed = 2,
                         p = 10,
                         mode = "wtsa")
        
    def get_last_removed_model(self, location):
        return self.stack_screen.last_removed_model[location]
    def clear_last_removed_model(self, location):
        self.stack_screen.last_removed_model[location] = ""