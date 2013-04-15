import procgame
import pinproc
import logging
from procgame import *
from functools import partial
from dmmode import DMMode
from random import choice

class FortressMultiball(DMMode):
    def __init__(self, game):
        super(FortressMultiball, self).__init__(game, 14)
        self.logger = logging.getLogger("FortressMB")
        
        self.jackpots = ['center','left_ramp','left_loop','right_freeway','right_ramp','right_subway','side_ramp']
        self.current_jackpot = 0
        self.jackpot_score = 750000
        
    def mode_started(self):
        self.logger.info("Starting Fortress Multiball...")
        
        self.game.current_player().multiball_lit = False
        self.game.current_player().fortress_multiball = True
        self.game.current_player().fortress_multiball_lit = False
        self.game.current_player().freeze1 = True
        self.game.current_player().freeze2 = False
        self.game.current_player().freeze3 = False
        self.game.current_player().freeze4 = False
        self.game.lamps.startMultiball.disable()
        
        self.cancel_all_delayed()
        
        self.current_jackpot = 0
        self.jackpot_score = 750000
        
        self.game.sound.play_music("fortressmb",-1)
        self.delay('play_maniac', event_type=None, delay=1, handler=self.play_maniac)
        
        self.game.trough.launch_balls(1,stealth=False)
        self.game.ball_save.add(20.0, allow_multiple_saves=True)
        self.game.ball_save.num_balls_to_save = 2
        self.game.ball_save.allow_multiple_saves = True
        
        if self.game.switches.topPopper.is_active():
            self.delay('top_pulse', event_type=None, delay=3, handler=self.game.coils.topPopper.pulse)
        
        self.update_lamps()
        
        self.game.close_divertor()
        
    def increment_jackpot(self):
        self.jackpot_score += 500000
        self.current_jackpot += 1
        if self.current_jackpot > len(self.jackpots) - 1:
            self.current_jackpot = 0
        
    def update_jackpot(self):
        self.game.lamps.centerRampJackpot.disable()
        self.game.lamps.rightRampJackpot.disable()
        self.game.lamps.rightLoopJackpot.disable()
        self.game.lamps.leftRampJackpot.disable()
        self.game.lamps.leftLoopJackpot.disable()
        self.game.lamps.undergroundJackpot.disable()
        self.game.lamps.sideRampJackpot.disable()
        
        self.game.lamps.undergroundArrow.disable()
        self.game.lamps.leftRampArrow.disable()
        self.game.lamps.sideRampArrow.disable()
        self.game.lamps.leftLoopArrow.disable()
        self.game.lamps.centerRampArrow.disable()
        self.game.lamps.rightLoopArrow.disable()
        self.game.lamps.rightRampArrow.disable()
        
        if self.jackpots[self.current_jackpot] == 'center':
            self.game.lamps.centerRampJackpot.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            self.game.lamps.centerRampArrow.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
        
        if self.jackpots[self.current_jackpot] == 'left_ramp':
            self.game.lamps.leftRampJackpot.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            self.game.lamps.leftRampArrow.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            
        if self.jackpots[self.current_jackpot] == 'left_loop':
            self.game.lamps.leftLoopJackpot.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            self.game.lamps.leftLoopArrow.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            
        if self.jackpots[self.current_jackpot] == 'right_freeway':
            self.game.lamps.rightLoopJackpot.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            self.game.lamps.rightLoopArrow.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
        
        if self.jackpots[self.current_jackpot] == 'right_ramp':
            self.game.lamps.rightRampJackpot.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            self.game.lamps.rightRampArrow.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
        
        if self.jackpots[self.current_jackpot] == 'right_subway':
            self.game.lamps.undergroundJackpot.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            self.game.lamps.undergroundArrow.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
        
        if self.jackpots[self.current_jackpot] == 'side_ramp':
            self.game.lamps.sideRampJackpot.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            self.game.lamps.sideRampArrow.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
        
    def sw_centerRamp_active(self, sw):
        if self.jackpots[self.current_jackpot] == 'center':
            self.delay('play_jackpot', event_type=None, delay=1.2, handler=self.play_jackpot)
            self.game.sound.play("explode",fade_music=True)
            self.game.base_game_mode.random_lamp_effect()
            self.game.score(self.jackpot_score)
            base.screenManager.showModalMessage(
                                            message="JACKPOT AWARDED\n" + str(self.jackpot_score), 
                                            modal_name="jackpot", 
                                            fg=(1,0,0,1),
                                            frame_color=(1,0,0,1),
                                            blink_speed=0.030,
                                            blink_color=(0,0,0,0),
                                            bg=(0,0,0,1), 
                                            time = 2)
            self.increment_jackpot()
            self.update_jackpot()
            
    def sw_upperLeftFlipperGate_active(self, sw):
        if self.jackpots[self.current_jackpot] == 'left_loop':
            self.delay('play_jackpot', event_type=None, delay=1.2, handler=self.play_jackpot)
            self.game.sound.play("explode",fade_music=True)
            self.game.base_game_mode.random_lamp_effect()
            self.game.score(self.jackpot_score)
            base.screenManager.showModalMessage(
                                            message="JACKPOT AWARDED\n" + str(self.jackpot_score), 
                                            modal_name="jackpot", 
                                            fg=(1,0,0,1),
                                            frame_color=(1,0,0,1),
                                            blink_speed=0.030,
                                            blink_color=(0,0,0,0),
                                            bg=(0,0,0,1), 
                                            time = 2)
            self.increment_jackpot()
            self.update_jackpot()
            
    def sw_leftRampExit_active(self, sw):
        if self.jackpots[self.current_jackpot] == 'left_ramp':
            self.delay('play_jackpot', event_type=None, delay=1.2, handler=self.play_jackpot)
            self.game.sound.play("explode",fade_music=True)
            self.game.base_game_mode.random_lamp_effect()
            self.game.score(self.jackpot_score)
            base.screenManager.showModalMessage(
                                            message="JACKPOT AWARDED\n" + str(self.jackpot_score), 
                                            modal_name="jackpot", 
                                            fg=(1,0,0,1),
                                            frame_color=(1,0,0,1),
                                            blink_speed=0.030,
                                            blink_color=(0,0,0,0),
                                            bg=(0,0,0,1), 
                                            time = 2)
            self.increment_jackpot()
            self.update_jackpot()
            
    def sw_rightFreeway_active(self, sw):
        if self.jackpots[self.current_jackpot] == 'right_freeway':
            self.delay('play_jackpot', event_type=None, delay=1.2, handler=self.play_jackpot)
            self.game.sound.play("explode",fade_music=True)
            self.game.base_game_mode.random_lamp_effect()
            self.game.score(self.jackpot_score)
            base.screenManager.showModalMessage(
                                            message="JACKPOT AWARDED\n" + str(self.jackpot_score), 
                                            modal_name="jackpot", 
                                            fg=(1,0,0,1),
                                            frame_color=(1,0,0,1),
                                            blink_speed=0.030,
                                            blink_color=(0,0,0,0),
                                            bg=(0,0,0,1), 
                                            time = 2)
            self.increment_jackpot()
            self.update_jackpot()
            
    def sw_rightRampExit_active(self, sw):
        if self.jackpots[self.current_jackpot] == 'right_ramp':
            self.delay('play_jackpot', event_type=None, delay=1.2, handler=self.play_jackpot)
            self.game.sound.play("explode",fade_music=True)
            self.game.base_game_mode.random_lamp_effect()
            self.game.score(self.jackpot_score)
            base.screenManager.showModalMessage(
                                            message="JACKPOT AWARDED\n" + str(self.jackpot_score), 
                                            modal_name="jackpot", 
                                            fg=(1,0,0,1),
                                            frame_color=(1,0,0,1),
                                            blink_speed=0.030,
                                            blink_color=(0,0,0,0),
                                            bg=(0,0,0,1), 
                                            time = 2)
            self.increment_jackpot()
            self.update_jackpot()
            
    def sw_bottomPopper_active_for_500ms(self, sw):
        if self.jackpots[self.current_jackpot] == 'right_subway':
            self.delay('play_jackpot', event_type=None, delay=1.2, handler=self.play_jackpot)
            self.game.sound.play("explode",fade_music=True)
            self.game.base_game_mode.random_lamp_effect()
            self.game.score(self.jackpot_score)
            base.screenManager.showModalMessage(
                                            message="JACKPOT AWARDED\n" + str(self.jackpot_score), 
                                            modal_name="jackpot", 
                                            fg=(1,0,0,1),
                                            frame_color=(1,0,0,1),
                                            blink_speed=0.030,
                                            blink_color=(0,0,0,0),
                                            bg=(0,0,0,1), 
                                            time = 2)
            self.increment_jackpot()
            self.update_jackpot()
            
    def sw_sideRampExit_active(self, sw):
        if self.jackpots[self.current_jackpot] == 'side_ramp':
            self.delay('play_jackpot', event_type=None, delay=1.2, handler=self.play_jackpot)
            self.game.sound.play("explode",fade_music=True)
            self.game.base_game_mode.random_lamp_effect()
            self.game.score(self.jackpot_score)
            
            base.screenManager.showModalMessage(
                                            message="JACKPOT AWARDED\n" + str(self.jackpot_score), 
                                            modal_name="jackpot", 
                                            fg=(1,0,0,1),
                                            frame_color=(1,0,0,1),
                                            blink_speed=0.030,
                                            blink_color=(0,0,0,0),
                                            bg=(0,0,0,1), 
                                            time = 2)
            
            self.increment_jackpot()
            self.update_jackpot()
            
    def play_jackpot(self):
        self.game.sound.play("jackpot", fade_music=True)
          
    def play_maniac(self):
        self.game.sound.play("maniac", fade_music=True)
    
    def explode_lamps(self):
        self.game.lampController.play_show("gameend", repeat=True)
    
    def update_lamps(self):
        self.game.gi_off()
        self.game.coils.leftRampLwrFlasher.schedule(schedule=0b00110011001100110011001100110011, cycle_seconds=0, now=True)
        self.game.coils.rightRampFlasher.schedule(  schedule=0b11001100110011001100110011001100, cycle_seconds=0, now=True)
        self.update_jackpot()
    
    def mode_stopped(self):
        self.logger.info("Multiball mode stopped")
        self.game.gi_on()
        self.game.coils.leftRampLwrFlasher.disable()
        self.game.coils.rightRampFlasher.disable()
        
        p = self.game.current_player()
        p.freeze1 = True
        p.freeze2 = True
        p.freeze3 = False
        p.freeze4 = False
        
        self.game.lamps.centerRampJackpot.disable()
        self.game.lamps.rightRampJackpot.disable()
        self.game.lamps.rightLoopJackpot.disable()
        self.game.lamps.leftRampJackpot.disable()
        self.game.lamps.leftLoopJackpot.disable()
        self.game.lamps.undergroundJackpot.disable()
        self.game.lamps.sideRampJackpot.disable()
        
        self.game.lamps.undergroundArrow.disable()
        self.game.lamps.leftRampArrow.disable()
        self.game.lamps.sideRampArrow.disable()
        self.game.lamps.leftLoopArrow.disable()
        self.game.lamps.centerRampArrow.disable()
        self.game.lamps.rightLoopArrow.disable()
        self.game.lamps.rightRampArrow.disable()
        
        if self.game.trough.num_balls_in_play > 0:
            self.game.play_music()
            self.game.update_lamps()
            
            if self.game.current_player().claw_lit:
                self.game.open_divertor()
        
    def ball_drained(self):
        if self.game.trough.num_balls_in_play <= 1:
            self.game.modes.remove(self)