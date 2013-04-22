import procgame
import pinproc
import logging
from procgame import *
from functools import partial
from dmmode import DMMode
from random import choice

class CarChaseMode(DMMode):
    def __init__(self, game):
        super(CarChaseMode, self).__init__(game, 14)
        self.logger = logging.getLogger("CarChase")
        self.ignore_bottom = False
        self.ignore_top = False
        self.is_left_ramp = True
        self.mode_completing = False
        self.shots_made = 0
        self.shot_value = 500000
        
        self.current_sound = 0
        
        self.screen = base.screenManager.getScreen("carchase")
        
        self.sounds = ['spartan_catchup', 'huxley_scream', 'huxley_scream' 'huxley_gotit', 'huxley_scream', 'spartan_catchup', 'spartan_push_pedal']
        
    def mode_started(self):
        self.logger.info("Starting car chase mode...")
        self.cancel_all_delayed()
        self.game.close_divertor()
        
        if self.game.current_player().claw_lit:
            self.game.current_player().claw_lit = False
            self.game.current_player().access_claw_lit = True
        
        if not self.game.acmag.is_started():
            base.screenManager.getScreen("stack").clear_stacks()
        
        # carCrashTop, carCrashCenter, carCrashBottom
        self.game.sound.play_music("chase",-1)
        self.delay('play_start', event_type=None, delay=1, handler=self.play_start_sound)
        self.is_left_ramp = True
        self.shots_made = 0
        self.shot_value = 500000
        self.mode_completing = False
        
        self.current_sound = 0
        
        self.game.base_game_mode.set_timer(20)
        self.game.base_game_mode.start_timer()
        self.update_lamps()
        
    def play_start_sound(self):
        self.game.sound.play("spartan_push")
    
    def play_random_sound(self):
        self.game.sound.play(self.sounds[self.current_sound])
        self.current_sound += 1
        if self.current_sound > len(self.sounds) - 1:
            self.current_sound = 0
        
    def sw_rightRampExit_active(self, sw):
        if self.is_left_ramp: return
        
        self.game.sound.play("engine")
        self.delay('play_random_sound', event_type=None, delay=1, handler=self.play_random_sound)
        self.game.score(self.shot_value)
        self.is_left_ramp = True
        self.update_lamps()
        self.shots_made += 1
        
    def sw_elevatorHold_active_for_250ms(self, sw):
        if not self.mode_completing:
            self.game.sound.stop_music()
            self.game.dim_lower_pf()
            self.mode_completing = True
            self.game.base_game_mode.pause_timer()
            self.delay('explode_lamps', event_type=None, delay=6.5, handler=self.explode_lamps)
            self.delay('show_award', event_type=None, delay=7.6, handler=self.show_award)
            self.game.current_player().car_chase = True
            base.screenManager.showScreen("carchase")
    
    def explode_lamps(self):
        self.game.lampController.play_show("gameend", repeat=True)
        
        
    def show_award(self):
        base.screenManager.showModalMessage(
                                    message = "10,251,999\nAWARDED!",
                                    time = 5,
                                    font = "motorwerk.ttf",
                                    scale = 0.17,
                                    bg=(0,0,0,1),
                                    fg=(1,1,1,1),
                                    frame_color = (1,0,0,1),
                                    blink_speed = 0.015,
                                    blink_color = (0,0,0,1),
                                    #l r t b
                                    frame_margin = (0.1,0.25,0,0)
                                    )
        self.delay('total', event_type=None, delay=3, handler=self.game.sound.play, param="bonus_total")
        self.delay('end_mode', event_type=None, delay=5, handler=self.end_mode)
        self.game.score(10251990)
        
    def end_mode(self):
        self.game.lampController.stop_show()
        self.game.update_lamps()
        
        self.game.claw.orient()
        self.game.gi_on()
        self.game.modes.remove(self)
        base.screenManager.hideScreen("carchase")
        
    def sw_leftRampExit_active(self, sw):
        if not self.is_left_ramp: return
        
        self.game.sound.play("engine")
        self.delay('play_random_sound', event_type=None, delay=1, handler=self.play_random_sound)
        self.game.score(self.shot_value)
        self.is_left_ramp = False
        self.update_lamps()
        self.shots_made += 1
        
        if self.shots_made >= 3:
            self.game.open_divertor()
    
    def update_lamps(self):
        if self.is_left_ramp:
            self.game.lamps.leftRampCarChase.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            self.game.coils.leftRampLwrFlasher.schedule(schedule=0x30003000, cycle_seconds=0, now=True)
            self.game.lamps.rightRampCarChase.disable()
            self.game.coils.rightRampFlasher.disable()
        else:
            self.game.lamps.rightRampCarChase.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            self.game.coils.rightRampFlasher.schedule(schedule=0x30003000, cycle_seconds=0, now=True)
            self.game.lamps.leftRampCarChase.disable()
            self.game.coils.leftRampLwrFlasher.disable()
    
    def sw_chaseCar1_active(self, sw):
        if self.ignore_bottom: return
        
        self.game.ball_save.add(3.0, allow_multiple_saves=False)
        
        self.ignore_bottom = True
        self.delay('unignore_bottom_car', event_type=None, delay=3, handler=self.unignore_bottom)
        
        base.screenManager.showModalMessage(
                                    message = "Chase value increased!",
                                    time = 1.2,
                                    font = "motorwerk.ttf",
                                    scale = 0.17,
                                    bg=(0,0,0,1),
                                    fg=(1,1,1,1),
                                    frame_color = (1,0,0,1),
                                    blink_speed = 0.015,
                                    blink_color = (0,0,0,1),
                                    #l r t b
                                    frame_margin = (0.1,0.25,0,0)
                                    )
        
        self.shot_value += 100000
        
    def sw_chaseCar2_active(self, sw):
        if self.ignore_top: return
        self.ignore_top = True
        self.delay('unignore_top_car', event_type=None, delay=3, handler=self.unignore_top)
    
        
    def sw_flipperLwL_closed_for_1s(self, sw):
        if not self.game.wtsa.is_started():
            self.game.coils.flipperLwLHold.disable()
            
    def sw_flipperLwR_closed_for_1s(self, sw):
        if not self.game.wtsa.is_started():
            self.game.coils.flipperLwRHold.disable()
            
        
    def unignore_bottom(self):
        self.ignore_bottom = False
        
    def unignore_top(self):
        self.ignore_top = False
    
    def mode_stopped(self):
        self.logger.info("Car Chase mode complete")
        if not self.game.current_player().claw_lit:
            self.game.close_divertor()
        
        self.game.coils.leftRampLwrFlasher.disable()
        self.game.coils.rightRampFlasher.disable()
        self.game.lamps.rightRampCarChase.disable()
        self.game.lamps.leftRampCarChase.disable()
        if self.game.acmag.is_started() and self.game.current_player().timer > 0:
            self.game.base_game_mode.start_timer()
        else:
            self.game.current_player().timer = 0
            self.game.base_game_mode.start_timer()
        
        if self.game.trough.num_balls_in_play > 0:
            self.game.play_music()
        
    def timeout(self):
        self.logger.info("Car Chase timeout")
        self.game.current_player().car_chase = True
        self.game.modes.remove(self)
        
    def ball_drained(self):
        if self.game.trough.num_balls_in_play > 0: return
        self.game.modes.remove(self)