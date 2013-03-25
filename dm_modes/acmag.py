import procgame
import pinproc
import logging
import random
from procgame import *
from dmmode import DMMode

class AcmagMode(DMMode):
    score_color_switch = False
    mode_accomplished = False
    def __init__(self, game):
        super(AcmagMode, self).__init__(game, 12)
        self.logger = logging.getLogger("ACMAG")
        self.switch_ignores = {}
        self.switch_ignores['right_enter'] = False
        self.switch_ignores['left_enter'] = False
        
        
    def mode_started(self):
        self.logger.info("Starting ACMAG mode...")
        self.screen = base.screenManager.getScreen("acmag")
        
        base.screenManager.getScreen("score").set_score_color((1,0,0,1))
        if not self.game.car_chase.is_started():
            self.game.sound.play_music("acmag",-1)
            base.screenManager.getScreen("stack").clear_stacks()
        
        self.screen.mode_started()
            
        self.game.sound.play("computer_acmag", fade_music=True)
        self.game.base_game_mode.set_timer(30)
        self.game.base_game_mode.start_timer()
        self.delay(name='acmag_blink_score', event_type=None, delay=0.42, handler=self.toggle_score_color)
        self.mode_accomplished = False
        base.screenManager.showScreen("acmag", False)
    
    def mode_stopped(self):
        self.logger.info("ACMAG mode complete")
        base.screenManager.hideScreen("acmag")
        self.cancel_delayed('acmag_blink_score')
        base.screenManager.getScreen("score").set_score_color((0,1,1,1))
        
        # If this mode wasn't accomplished, undo all acmag settings so the player
        # can re-run the mode
        if not self.mode_accomplished:
            self.game.current_player().acmag = False
            # Cut them some slack at 25%
            self.game.current_player().acmag_percentage = 60
            
    def ball_drained(self):
        self.cancel_delayed('acmag_blink_score')
        base.screenManager.hideScreen("acmag")
        
    def timeout(self):
        self.logger.info("ACMAG timeout")
        self.mode_accomplished = True
        self.game.modes.remove(self)
        
        if self.game.trough.num_balls_in_play > 0:
            self.game.sound.play_music("main",-1)
        
        
    def toggle_score_color(self):
        self.score_color_switch = not self.score_color_switch
        
        if self.score_color_switch:
            base.screenManager.getScreen("score").set_score_color((1,1,1,1))
        else:
            base.screenManager.getScreen("score").set_score_color((1,0,0,1))
            
        self.delay(name='acmag_blink_score', event_type=None, delay=0.45, handler=self.toggle_score_color)
        
    def sw_rightRampEnter_active(self, sw):
        if self.switch_ignores['right_enter'] or not self.screen.explode_right():
            return
        
        self.game.sound.play("explode")
        
        if random.randint(1,3) == 2:
            self.cancel_delayed('acmag_praise')
            self.delay(name='acmag_praise', event_type=None, delay=0.5, handler=self.play_praise)
            
        self.ignore_switch('right_enter')
        
    
    def sw_leftRampEnter_active(self, sw):
        if self.switch_ignores['left_enter'] or not self.screen.explode_left():
            return
        
        self.game.sound.play("explode")
        
        if random.randint(1,3) == 2:
            self.cancel_delayed('acmag_praise')
            self.delay(name='acmag_praise', event_type=None, delay=0.5, handler=self.play_praise)
            
        self.ignore_switch('left_enter')
    
    def sw_sideRampExit_active(self, sw):
        pass
    
    def sw_centerRamp_active(self, sw):
        self.screen.generate_new_barrel()
        self.screen.explode_center()
        self.game.sound.play("explode")
        
        if random.randint(1,2) == 2:
            self.cancel_delayed('acmag_praise')
            self.delay(name='acmag_praise', event_type=None, delay=0.5, handler=self.play_praise)
            
    def play_praise(self):
        self.game.sound.play("praise")
        
    def expire_switch_ignore(self, switch):
        self.switch_ignores[switch] = False
        
    def ignore_switch(self, switch, length = 1.5):
        self.switch_ignores[switch] = True
        self.delay('acmag_unignore_'+switch, event_type=None, delay=length, handler=self.expire_switch_ignore, param=switch)