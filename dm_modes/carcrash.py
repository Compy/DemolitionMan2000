import procgame
import pinproc
import logging
from procgame import *
from functools import partial
from dmmode import DMMode

class CarCrashMode(DMMode):
    def __init__(self, game):
        super(CarCrashMode, self).__init__(game, 10)
        self.logger = logging.getLogger("CarCrash")
        self.ignore_bottom = False
        self.ignore_top = False
        
    def mode_started(self):
        self.logger.info("Starting carcrash mode...")
        self.cancel_all_delayed()
        # carCrashTop, carCrashCenter, carCrashBottom
        self.update_lamps()
    
    def update_lamps(self):
        
        if self.game.current_player().car_crashes == 0:
            self.game.lamps.carCrashBottom.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
        elif self.game.current_player().car_crashes == 1:
            self.game.lamps.carCrashBottom.pulse(0)
            self.game.lamps.carCrashCenter.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
        elif self.game.current_player().car_crashes >= 2:
            self.game.lamps.carCrashBottom.pulse(0)
            self.game.lamps.carCrashCenter.pulse(0)
            self.game.lamps.carCrashTop.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
    
    def sw_chaseCar1_active(self, sw):
        if self.ignore_bottom: return
        
        self.game.ball_save.add(2.0, allow_multiple_saves=False)
        
        if self.game.current_player().car_crashes == 0:
            self.game.current_player().car_crashes = 1
            self.game.score(3000000)
        elif self.game.current_player().car_crashes == 1:
            self.game.current_player().car_crashes = 2
            self.game.score(6000000)
        elif self.game.current_player().car_crashes >= 2:
            self.game.current_player().car_crashes += 1
            self.game.score(10000000)
            
        self.update_lamps()
        self.ignore_bottom = True
        self.delay('unignore_bottom_car', event_type=None, delay=3, handler=self.unignore_bottom)
        self.game.sound.play("tires")
        
    def sw_chaseCar2_active(self, sw):
        if self.ignore_top: return
        self.game.score(3000000 * self.game.current_player().car_crashes)
        self.ignore_top = True
        self.delay('unignore_top_car', event_type=None, delay=3, handler=self.unignore_top)
        self.game.sound.play("crash")
    
        
    def unignore_bottom(self):
        self.ignore_bottom = False
        
    def unignore_top(self):
        self.ignore_top = False
    
    def mode_stopped(self):
        self.logger.info("Carcrash mode complete")