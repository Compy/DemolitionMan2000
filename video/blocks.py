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
from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
import os, sys
import random

class BlocksScreen(GameScreen):
    '''
    ROW COMBINATIONS
    
    
    1 -*-*-*-
       * * *
       * * *
       
    2  * * *
       - - -
       * * *
    
    3  * * *
       * * *
       - - -
       
    4  - * *
       * - *
       * * -
    
    5  * * -
       * - *
       - * *
       
    6  | * *
       | * *
       | * *
       
    7  * | *
       * | *
       * | *
       
    8  * * |
       * * |
       * * |
    
    
    '''

    def __init__(self, screen_manager):
        '''
        Constructor
        '''
        super(BlocksScreen, self).__init__(screen_manager, "blocks_screen")
        
        self.cubes = []
        self.stackpos = (-1.5, 0, 2)
        
        dlight = DirectionalLight('my dlight')
        self.dlnp = render.attachNewNode(dlight)
        
        self.fill_stack(0)
        self.fill_stack(1)
        self.fill_stack(2)
        
        arc = base.loader.loadModel("assets/models/arc.bam")
        arc.setPos(-1.1,6,-1.5)
        arc.setScale(0.1,0.1,0.1)
        arc.setH(120)
        arc.reparentTo(self.node)
        arc.setLight(self.dlnp)
        
        self.wizard = base.loader.loadModel("assets/models/wizard.bam")
        self.wizard.setPos(-1.9,6,0)
        self.wizard.setScale(0.015,0.015,0.015)
        self.wizard.setH(20)
        self.wizard.reparentTo(self.node)
        self.wizard.setLight(self.dlnp)
        
        self.explosion = Sprite(
                                parent=self.node, 
                                file_name="assets/sprites/blue_explosion/blue_explosion_", 
                                file_type="png", 
                                num_frames=13, 
                                int_padding=2,
                                scale=(5,5,5))
        
        self.sparkle = Sprite(
                                parent=self.node, 
                                file_name="assets/sprites/purple_sparkle/purple_sparkle_", 
                                file_type="png", 
                                num_frames=17, 
                                int_padding=2,
                                fps=25,
                                scale=(1.2,1.2,1.2))
        
        self.wizard_w = OnscreenImage(
                         parent=self.node2d,                        # Parented to our 2d node renderer
                         image="assets/images/wizard_w.png",     # File name specified
                         pos=(-0.5,0,0.4),                              # z: -2 is off screen at the bottom
                         scale=(0.4,1,0.25))                         # Scale it down a bit horizontally and vertically to make it look right
        
        self.wizard_wi = OnscreenImage(
                         parent=self.node2d,                        # Parented to our 2d node renderer
                         image="assets/images/wizard_wi.png",     # File name specified
                         pos=(-0.5,0,0.4),                              # z: -2 is off screen at the bottom
                         scale=(0.4,1,0.25))                         # Scale it down a bit horizontally and vertically to make it look right
        
        self.wizard_w.setTransparency(TransparencyAttrib.MAlpha)
        self.wizard_wi.setTransparency(TransparencyAttrib.MAlpha)
        
        self.wizard_wi.hide()
        self.wizard_w.hide()
        
        if base.displayFlipped:
            self.wizard.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullCounterClockwise))
            arc.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullCounterClockwise))
        
    def show(self):
        super(BlocksScreen, self).show()
        self.sparkle.setPos(-3.6,20,-4.1)
        self.sparkle.play(loops=-1)
        
        
    def fill_stack(self, stack = 1):
        colors = ("block_blue.bam", "block_red.bam", "purple.bam", "powerup.egg")
        for i in range(3):
        
            color = random.choice(colors)
            cube = base.loader.loadModel("assets/models/"+color)
            zpos = i * (0.8)
            zpos = zpos - 1
            cube.setPos(self.stackpos[stack],15,zpos)
            cube.setScale(0.02,0.02,0.02)
            #cube.stack = stack
            #cube.slot = i
            
            cubeEntry = {}
            cubeEntry['stack'] = stack
            cubeEntry['slot'] = i + 1
            cubeEntry['model'] = cube
            
            if color == "block_blue.bam":
                cubeEntry['color'] = "blue"
            elif color == "block_red.bam":
                cubeEntry['color'] = "red"
            elif color == "purple.bam":
                cubeEntry['color'] = "purple"
            else:
                cubeEntry['color'] = "bright_blue"
            
            #myInterval4 = cube.hprInterval( 1, Vec3(360,-10,0) ).loop()
            
            cube.setP(10)
            cube.setH(10)
            
            cube.reparentTo(self.node)
            
            self.cubes.append(cubeEntry)
    
            cube.setLight(self.dlnp)
            
            if base.displayFlipped:
                cube.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullCounterClockwise))
                
    def get_cube_color(self, stack, slot):
        for cube in self.cubes:
            if cube['stack'] == stack and cube['slot'] == slot:
                return cube['color']
            
        return None
    
    def get_cube_model(self, stack, slot):
        for cube in self.cubes:
            if cube['stack'] == stack and cube['slot'] == slot:
                return cube['model']
            
        return None
    
    def explode_cube(self, stack):
        explosion = Sprite(
                                parent=self.node, 
                                file_name="assets/sprites/blue_explosion/blue_explosion_", 
                                file_type="png", 
                                num_frames=13, 
                                int_padding=2,
                                scale=(2,2,2),
                                fps=25)
        explosion.setPos(self.stackpos[stack],14,-1)
        explosion.play(loops=1)
    
    def remove_cube(self, stack, slot = 1):
        cubeToRemove = None
        for cube in self.cubes:
            if cube['stack'] == stack and cube['slot'] == slot:
                cubeToRemove = cube
                break
                
        if cubeToRemove != None:
            cubeToRemove['model'].removeNode()
            self.cubes.remove(cubeToRemove)
    
    def add_cube(self, stack):
        colors = ("block_blue.bam", "block_red.bam", "purple.bam", "powerup.egg")
        
        color = random.choice(colors)
        cube = base.loader.loadModel("assets/models/"+color)
        zpos = 2 * (0.8)
        zpos = zpos - 1
        cube.setPos(self.stackpos[stack],15,2)
        cube.setScale(0.02,0.02,0.02)
        #cube.stack = stack
        #cube.slot = i
        
        cubeEntry = {}
        cubeEntry['stack'] = stack
        cubeEntry['slot'] = 3
        cubeEntry['model'] = cube
        
        if color == "block_blue.bam":
            cubeEntry['color'] = "blue"
        elif color == "block_red.bam":
            cubeEntry['color'] = "red"
        elif color == "purple.bam":
            cubeEntry['color'] = "purple"
        else:
            cubeEntry['color'] = "bright_blue"
        
        #myInterval4 = cube.hprInterval( 1, Vec3(360,-10,0) ).loop()
        
        cube.setP(10)
        cube.setH(10)
        
        cube.reparentTo(self.node)
        
        self.cubes.append(cubeEntry)

        cube.setLight(self.dlnp)
        
        if base.displayFlipped:
            cube.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullCounterClockwise))
            
        LerpPosInterval(cube,duration=0.6,pos=(self.stackpos[stack],15,zpos),blendType='easeIn').start()
    
    def move_cubes_down(self, stack):
        for cube in self.cubes:
            if cube['stack'] == stack and cube['slot'] != 1:
                
                cube['slot'] -= 1
                
                zpos = (cube['slot'] - 1) * (0.8)
                zpos = zpos - 1
                #cube['model'].setPos(self.stackpos[stack],15,zpos)
                LerpPosInterval(cube['model'],duration=0.6,pos=(self.stackpos[stack],15,zpos),blendType='easeIn').start()

    def toggle_blink_section(self, section):
        if section == 1:
            for stack in range(3):
                cube3 = self.get_cube_model(3, stack)
                cube2 = self.get_cube_model(2, stack)
                cube1 = self.get_cube_model(1, stack)
                
                if cube3.isHidden():
                    cube1.show()
                    cube2.show()
                    cube3.show()
                else:
                    cube1.hide()
                    cube2.hide()
                    cube3.hide()

    def turn_wizard(self, degree = 20):
        self.wizard.hprInterval(1, Vec3(degree,0,0)).start()
        
    def hide_wizard_text(self):
        self.wizard_w.hide()
        self.wizard_wi.hide()
        
    def toggle_wi(self, toggle):
        self.wizard_w.show()
        if toggle:
            self.wizard_wi.hide()
        else:
            self.wizard_wi.show()