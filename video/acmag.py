'''
Created on Mar 3, 2013

@author: compy
'''

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

class AcmagScreen(GameScreen):
    '''
    classdocs
    '''


    def __init__(self, screen_manager):
        '''
        Constructor
        '''
        super(AcmagScreen, self).__init__(screen_manager, "acmag_screen")
        
        #self.place_model(model_name = "warehouse.egg",
        #                 scale = (0.015, 0.015, 0.015),
        #                 pos = (0.0, 120, -20),
        #                 rotate = False,
        #                 h = 150)
        
    def mode_started(self):
        self.stack_screen = self.screen_manager.getScreen("stack")
        
        self.stack_screen.place_model(model_name = "police_car.bam",
                         scale = (0.05, 0.05, 0.05),
                         pos = "right_ramp",
                         rotate = True,
                         rotspeed = 4,
                         mode = "acmag")
        
        self.stack_screen.place_model(model_name = "scanner.egg",
                         scale = (0.6, 0.6, 0.6),
                         pos = "left_ramp",
                         rotate = True,
                         rotspeed = 4,
                         mode = "acmag")
        
        self.stack_screen.place_model(model_name = "first_aid.bam",
                         scale = (0.02, 0.02, 0.02),
                         pos = "left_ramp",
                         rotate = True,
                         rotspeed = 3,
                         mode = "acmag")
        
        self.stack_screen.place_model(model_name = "bonus_x.bam",
                         scale = (0.7, 0.7, 0.7),
                         pos = "right_ramp",
                         rotate = True,
                         rotspeed = 3,
                         mode = "acmag")
        
        self.stack_screen.place_model(model_name = "barrel.bam",
                         scale = (0.2, 0.2, 0.2),
                         pos = "center_ramp",
                         rotate = True,
                         rotspeed = 2,
                         p = 10,
                         mode = "acmag")
        
        self.stack_screen.place_model(model_name = "barrel.bam",
                         scale = (0.2, 0.2, 0.2),
                         pos = "center_ramp",
                         rotate = True,
                         rotspeed = 2,
                         p = 10,
                         mode = "acmag")
        
        self.screen_manager.showScreen("stack")
        
    def explode(self, position):
        self.explosion = Sprite(self.node, "assets/sprites/explosion/explosion_", "png", 29, 2, scale = (1,1,1), fps = 50)
        self.explosion.setPos(position[0], position[1] - 112, position[2] + 28)
        self.explosion.play()
        
    def explode_right(self):
        if not self.stack_screen.location_has_object("right_ramp", mode="acmag"):
            return False
        
        self.explosion = Sprite(self.node, "assets/sprites/explosion/explosion_", "png", 29, 2, scale = (1,1,1), fps = 50)
        self.explosion.setPos(2.8,10,8.2)
        self.explosion.play()
        self.stack_screen.remove_bottom_model("right_ramp")
        return True
    
    def explode_left(self):
        if not self.stack_screen.location_has_object("left_ramp", mode="acmag"):
            return False
        
        self.explosion = Sprite(self.node, "assets/sprites/explosion/explosion_", "png", 29, 2, scale = (1,1,1), fps = 50)
        self.explosion.setPos(-1.3,10,6.9)
        self.explosion.play()
        self.stack_screen.remove_bottom_model("left_ramp")
        return True
        
    def explode_center(self):
        if not self.stack_screen.location_has_object("center_ramp", mode="acmag"):
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
                         mode = "acmag")
        

        