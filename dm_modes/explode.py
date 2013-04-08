import procgame
import pinproc
import logging
from procgame import *
from functools import partial
from dmmode import DMMode
import random

class ExplodeMode(DMMode):
    def __init__(self, game):
        super(ExplodeMode, self).__init__(game, 10)
        self.logger = logging.getLogger("Explode")
        self.explode_hurryup = False
        
        
    def mode_started(self):
        self.logger.info("Starting explode mode...")
        #base.screenManager.showScreen("skillshot", False)
        #self.skillshot_screen = base.screenManager.getScreen("skillshot")
        self.explode_hurryup = False
        self.update_lamps()
        self.current_sound = 0
        
    def mode_stopped(self):
        self.game.current_player().explode_leftloop = False
        self.game.current_player().explode_leftramp = False
        self.game.current_player().explode_rightramp = False
        self.game.current_player().explode_rightloop = False
    
    def add_explode_lamp(self):
        if not self.game.current_player().explode_leftloop:
            self.game.current_player().explode_leftloop = True
            self.game.lamps.leftLoopExplode.pulse(0)
        elif not self.game.current_player().explode_leftramp:
            self.game.lamps.leftRampExplode.pulse(0)
            self.game.current_player().explode_leftramp = True
        elif not self.game.current_player().explode_rightramp:
            self.game.lamps.rightRampExplode.pulse(0)
            self.game.current_player().explode_rightramp = True
        elif not self.game.current_player().explode_rightloop:
            self.game.lamps.rightLoopExplode.pulse(0)
            self.game.current_player().explode_rightloop = True
    
    def update_lamps(self):
        #leftLoopExplode
        #leftRampExplode
        #rightRampExplode
        #rightLoopExplode
        if not self.explode_hurryup:
            if self.game.current_player().explode_leftloop:
                self.game.lamps.leftLoopExplode.pulse(0)
            if self.game.current_player().explode_leftramp:
                self.game.lamps.leftRampExplode.pulse(0)
            if self.game.current_player().explode_rightramp:
                self.game.lamps.rightRampExplode.pulse(0)
            if self.game.current_player().explode_rightloop:
                self.game.lamps.rightLoopExplode.pulse(0)
        else:
            self.game.lamps.leftLoopExplode.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            self.game.lamps.leftRampExplode.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            self.game.lamps.rightRampExplode.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            self.game.lamps.rightLoopExplode.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
        
    def sw_upperLeftFlipperGate_active(self, sw):
        if self.game.current_player().explode_leftloop:

            self.game.sound.play("explode",fade_music=True)
            self.game.base_game_mode.random_lamp_effect()
            self.delay('explode_yeah', event_type=None, delay=1, handler=self.play_explode_praise)
            self.game.score(2000000)
            self.game.current_player().explosions += 1
        
    def sw_leftRampExit_active(self, sw):
        if self.game.current_player().explode_leftramp or self.explode_hurryup:
            
            self.game.sound.play("explode",fade_music=True)
            self.game.base_game_mode.random_lamp_effect()
            self.delay('explode_yeah', event_type=None, delay=1, handler=self.play_explode_praise)
            self.game.score(2000000)
            self.game.current_player().explosions += 1
        
    def sw_rightRampExit_active(self, sw):
        if self.game.current_player().explode_rightramp or self.explode_hurryup:
            
            self.game.sound.play("explode",fade_music=True)
            self.game.base_game_mode.random_lamp_effect()
            self.delay('explode_yeah', event_type=None, delay=1, handler=self.play_explode_praise)
            self.game.score(2000000)
            self.game.current_player().explosions += 1
        
    def sw_rightFreeway_active(self, sw):
        if self.game.current_player().explode_rightloop or self.explode_hurryup:
            
            self.game.sound.play("explode",fade_music=True)
            self.game.base_game_mode.random_lamp_effect()
            self.delay('explode_yeah', event_type=None, delay=1, handler=self.play_explode_praise)
            self.game.score(2000000)
            self.game.current_player().explosions += 1
            
    def play_explode_praise(self):
        explode_list = ['praise','simon_lovely','simon_right','spartan_yeah']
        self.game.sound.play(explode_list[self.current_sound],fade_music=True)
        
        self.current_sound += 1
        if self.current_sound > len(explode_list) - 1:
            self.current_sound = 0