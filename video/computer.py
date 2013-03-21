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

class ComputerScreen(GameScreen):

    computer_items = []
    computer_positions = []
    computer_cells = []
    anim_sequence = None
    active_cell = None
    active_cell_blinking = False
    def __init__(self, screen_manager):
        super(ComputerScreen, self).__init__(screen_manager, "computer_screen")
        #(-0.9904,0.97804)
        x = -0.9604
        y = 0.6804
        self.computer_positions.append((-0.9604, 0, 0.6804))
        self.computer_positions.append((0, 0, 0.6804))
        self.computer_positions.append((0.9630, 0, 0.6804))
        
        self.computer_positions.append((-0.9604, 0, 0))
        self.computer_positions.append((0, 0, 0))
        self.computer_positions.append((0.9630, 0, 0))
        
        self.computer_positions.append((-0.9604, 0, -0.6804))
        self.computer_positions.append((0, 0, -0.6804))
        self.computer_positions.append((0.9630, 0, -0.6804))
        
        self.anim_sequence = Sequence()
        #(-0.9812,0.70500)
        for i in range(9):
            self.computer_cells.append(OnscreenImage(image = 'assets/images/cell.png', 
                                                     pos = self.computer_positions[i],
                                                     parent = self.node2d,
                                                     scale = (0.35,1,0.35)))
            self.computer_cells[len(self.computer_cells) - 1].setTransparency(TransparencyAttrib.MAlpha)
        
        self.active_cell = OnscreenImage(image = 'assets/images/cell_active.png',
                                         pos = (-2, 0, 0),
                                         parent = self.node2d,
                                         scale = (0.35, 1, 0.35))
        self.active_cell.setTransparency(TransparencyAttrib.MAlpha)
        
        
    def random_cell(self, task = None):
        cell_number = random.randint(0,8)
        self.active_cell.setPos(self.computer_positions[cell_number])
        return Task.again
    
    def blink_active_cell(self):
        base.taskMgr.doMethodLater(0.08, self._do_blink_active_cell, 'computer_blink_task')
        
        base.screenManager.showModalMessage(
                                                message = base.hwgame.computer.award[0],
                                                time = 3.0,
                                                font = "eurostile.ttf",
                                                scale = 0.2,
                                                bg=(0,0,0,1),
                                                fg=(0,1,0,1),
                                                blink_speed = 0.5,
                                                blink_color = (0,0,0,1),
                                                #l r t b
                                                frame_margin = (0.1,0.25,0,0),
                                                frame_color = (0,1,0,1)
                                                )
        
    def _do_blink_active_cell(self, task = None):
        self.active_cell_blinking = not self.active_cell_blinking
        
        if self.active_cell_blinking:
            self.active_cell.show()
        else:
            self.active_cell.hide()
        return Task.again
        
    
    def stop_random(self, task = None):
        base.taskMgr.remove('computer_task')
        
    def computer_choice_timeout(self, task = None):
        self.stop_random(task)
        self.blink_active_cell()

    def show(self):        
        
        # Call our base class show method now so it can render anything it wants
        super(ComputerScreen, self).show()
        base.taskMgr.doMethodLater(0.08, self.random_cell, 'computer_task')
        base.taskMgr.doMethodLater(1.2, self.computer_choice_timeout, 'end_computer_task')

    def hide(self):
        """
        Called when the screen manager wants to remove this screen from the display.
        
        We have no choice but to obey when this method is called. So hide our background.
        
        Our models will be hidden automatically as the 3d nodes are removed from the render tree
        """
        super(ComputerScreen, self).hide()
        if base.hwgame != None:
            self.stop_random()
            base.taskMgr.remove('computer_blink_task')
        
        