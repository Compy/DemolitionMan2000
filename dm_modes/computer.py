import procgame
import pinproc
import logging
import random
from procgame import *
from dmmode import DMMode

class ComputerMode(DMMode):
    computer_awards = [
                       #('Extra Ball Lit', 'computer_light_eb'),
                       #('Light Explode', 'computer_explode_activated'),
                       #('Light Explode', 'computer_explode_activated'),
                       #('Light Explode', 'computer_explode_activated'),
                       #('Light Explode', 'computer_explode_activated'),
                       #('Light Explode', 'computer_explode_activated'),
                       #('3X Car Crash', 'computer_triple_car_crash'),
                       #('3X Car Crash', 'computer_triple_car_crash'),
                       #('3X Car Crash', 'computer_triple_car_crash'),
                       #('2X Retina Scan', 'computer_double_retina_scan'),
                       #('2X Retina Scan', 'computer_double_retina_scan'),
                       #('2X Retina Scan', 'computer_double_retina_scan'),
                       #('Light Arrows', 'computer_light_arrows'),
                       #('Light Arrows', 'computer_light_arrows'),
                       #('Light Arrows', 'computer_light_arrows'),
                       ('Mystery Mode', None),
                       ('Mystery Mode', None),
                       ('Mystery Mode', None),
                       #('Maximize Freezes', 'computer_max_freezes'),
                       #('Collect Bonus', 'computer_max_freezes'), #FIXME
                       #('Collect Standups', 'computer_max_freezes'),
                       #('Collect Standups', 'computer_max_freezes'),
                       #('Collect Standups', 'computer_max_freezes'),
                       #('Collect Standups', 'computer_max_freezes')
                       ]
    def __init__(self, game):
        super(ComputerMode, self).__init__(game, 11)
        self.logger = logging.getLogger("Computer")
        self.award = ""
        
        
    def mode_started(self):
        self.logger.info("Starting computer mode...")
        self.game.lamps.computer.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
        self.computer_screen = base.screenManager.getScreen("computer")
        self.award_in_progress = False
    
    def mode_stopped(self):
        self.game.lamps.computer.disable()
        self.logger.info("Computer mode complete")
        base.screenManager.hideScreen("computer")
        self.award_in_progress = False
        
    def sw_bottomPopper_active_for_200ms(self, sw):
        # Computer award
        self.start_award()
        return True
    
    def start_award(self):
        if self.award_in_progress: return
        base.screenManager.showScreen("computer", False)
        #self.game.sound.set_music_volume(0.2)
        self.game.sound.play("computer_award", fade_music=True)
        self.award = self.computer_awards[random.randrange(0,len(self.computer_awards) - 1)]
        
        self.logger.info("Computer awards " + self.award[0])
        
        self.delay(name='say_computer_award', event_type=None, delay=2.1, handler=self.announce_award)
        
        self.delay(name='end_computer', event_type=None, delay=4, handler=self.end_computer)
        self.award_in_progress = True
    
    def announce_award(self):
        if self.award[1] != None:
            self.game.sound.play(self.award[1], fade_music=True)
        
        if self.award[0] == "Light Arrows":
            self.game.current_player().arrow_loop = True
            self.game.current_player().arrow_left_ramp = True
            self.game.current_player().arrow_acmag = True
            self.game.current_player().arrow_subway = True
            self.game.current_player().arrow_side_ramp = True
            self.game.current_player().arrow_right_ramp = True
            self.game.current_player().arrow_right_loop = True

            self.game.lamps.leftLoopArrow.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)   
            self.game.lamps.rightRampArrow.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            self.game.lamps.undergroundArrow.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            self.game.lamps.leftRampArrow.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            self.game.lamps.sideRampArrow.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            self.game.lamps.centerRampArrow.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            self.game.lamps.rightLoopArrow.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            
        if self.award[0] == "Mystery Mode":
            self.game.current_player().computer_lit = False
            self.game.modes.add(self.game.wtsa)
            self.game.modes.remove(self)

    
    def update_lamps(self):
        if self.game.current_player().computer_lit:
            self.game.lamps.computer.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
        else:
            self.game.lamps.computer.disable()
    
    def end_computer(self):
        #self.game.sound.set_music_volume(0.6)
        self.game.current_player().computer_lit = False
        self.game.base_game_mode.release_bottomPopper()
        self.game.modes.remove(self)