import procgame
import pinproc
import logging
from procgame import *
from functools import partial
from dmmode import DMMode

class SanAngelesMode(DMMode):
    def __init__(self, game):
        super(SanAngelesMode, self).__init__(game, 10)
        self.logger = logging.getLogger("WTSA")
        self.shell = False
        self.burger = False
        self.scanner = False
        
        self.switch_ignores = {}
        self.switch_ignores['right_enter'] = False
        self.switch_ignores['left_enter'] = False
        
    def mode_started(self):
        self.logger.info("Starting Welcome to San Angeles mode...")
        self.cancel_all_delayed()
        self.screen = base.screenManager.getScreen("wtsa")
        
        self.game.enable_flippers(False)
        self.game.invert_flippers(True)
        self.game.current_player().sanangeles_in_progress = True
        base.screenManager.showScreen("wtsa", False)
        self.screen.show_instructions()
        self.delay('wtsa_start', event_type=None, delay=5, handler=self.start)
        self.game.sound.play_music("wtsa", -1)
        self.shell = False
        self.burger = False
        self.scanner = False
        self.switch_ignores['right_enter'] = False
        self.switch_ignores['left_enter'] = False
        #self.game.lampController.play_show("wtsa",
        #                                   repeat=True)
        
        if self.game.current_player().claw_lit:
            self.game.close_divertor()
            self.game.current_player().access_claw_lit = True
            self.game.current_player().claw_lit = False
            self.game.update_lamps()
        
    def start(self):
        self.screen.hide_instructions()
        self.game.base_game_mode.release_bottomPopper()
        self.game.base_game_mode.set_timer(20)
        self.game.base_game_mode.start_timer()
        self.screen.mode_started()
        self.game.trough.launch_balls(2,stealth=False)
        self.game.ball_save.add(20.0, allow_multiple_saves=True)
        self.game.ball_save.num_balls_to_save = 3
        self.game.ball_save.allow_multiple_saves = True
    
    def mode_stopped(self):
        self.logger.info("WTSA mode complete")
        self.game.invert_flippers(False)
        self.game.enable_flippers(True)
        self.game.current_player().sanangeles_in_progress = False
        base.screenManager.hideScreen("wtsa")
        
    def timeout(self):
        self.game.sound.play_music("main",-1)
        self.game.modes.remove(self)
        
    def ball_drained(self):
        if self.game.trough.num_balls_in_play > 0: return
        base.screenManager.hideScreen("wtsa")
        
    def expire_switch_ignore(self, switch):
        self.switch_ignores[switch] = False
        
    def ignore_switch(self, switch, length = 1.5):
        self.switch_ignores[switch] = True
        self.delay('wtsa_unignore_'+switch, event_type=None, delay=length, handler=self.expire_switch_ignore, param=switch)
        
    def sw_rightRampEnter_active(self, sw):
        if self.switch_ignores['right_enter'] or not self.screen.explode_right():
            self.screen.clear_last_removed_model('right_ramp')
            return
        
        self.game.sound.play("explode")
            
        self.ignore_switch('right_enter')
        
        self.play_sound(self.screen.get_last_removed_model('right_ramp'))
        self.game.base_game_mode.pause_timer(3)
        self.process_award(self.screen.get_last_removed_model('right_ramp'))
        
        print "sanangeles right ramp enter "  + self.screen.get_last_removed_model('right_ramp')
        
        #self.game.lampController.play_show("wtsa",
        #                                   repeat=True)
        
    
    def sw_leftRampEnter_active(self, sw):
        if self.switch_ignores['left_enter'] or not self.screen.explode_left():
            self.screen.clear_last_removed_model('left_ramp')
            return
        
        self.game.sound.play("explode")
        self.ignore_switch('left_enter')
        self.play_sound(self.screen.get_last_removed_model('left_ramp'))
        
        self.game.base_game_mode.pause_timer(3)
        
        print "sanangeles left ramp enter "  + self.screen.get_last_removed_model('left_ramp')
        
        self.process_award(self.screen.last_removed_model['left_ramp'])
        #self.game.lampController.play_show("wtsa",
        #                                   repeat=True)
    
    def sw_sideRampExit_active(self, sw):
        pass
    
    def sw_centerRamp_active(self, sw):
        if not self.screen.explode_center():
            self.screen.clear_last_removed_model('center_ramp')
            return
        self.game.sound.play("explode")
        self.play_sound(self.screen.get_last_removed_model('center_ramp'))
        
        self.game.base_game_mode.pause_timer(3)
        self.process_award(self.screen.get_last_removed_model('center_ramp'))
        
        print "sanangeles center ramp enter " + self.screen.get_last_removed_model('center_ramp')
        
        #self.game.lampController.play_show("wtsa",
        #                                   repeat=True)
        
    def process_award(self, award):
        
        message = ""
        if award == "scanner":
            message = "100,000"
            self.game.score(100000)
        if award == "shell":
            message = "200,000"
            self.game.score(200000)
        if award == "burger":
            message = "300,000"
            self.game.score(300000)
        if award == "bonus_x":
            self.game.current_player().bonus_x += 1
            message = "Multiplier Increased!"
            base.display_queue.put_nowait(partial(base.screenManager.getScreen("score").update_hud))
            
        base.screenManager.showModalMessage(
                                    message = message,
                                    time = 2.0,
                                    font = "motorwerk.ttf",
                                    scale = 0.2,
                                    bg=(0,0,0,1),
                                    fg=(1,1,1,1),
                                    frame_color = (1,0,0,1),
                                    blink_speed = 0.015,
                                    blink_color = (0,0,0,1),
                                    #l r t b
                                    frame_margin = (0.1,0.25,0,0)
                                    )
        
    def play_sound(self, obj):
        if obj == "burger" and not self.burger:
            self.game.sound.play("cows",fade_music=True)
            self.burger = True
        if obj == "shell" and not self.shell:
            self.game.sound.play("seashells",fade_music=True)
            self.shell = True
        if obj == "scanner" and not self.scanner:
            self.game.sound.play("verbal_fine",fade_music=True)
            self.scanner = True
        