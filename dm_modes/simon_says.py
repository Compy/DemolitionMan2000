import procgame
import pinproc
import logging
from procgame import *
from functools import partial
from dmmode import DMMode
import random

LEFT_RAMP = 0
RIGHT_RAMP = 1
SIDE_SCOOP = 2

class SimonSays(DMMode):
    def __init__(self, game):
        super(SimonSays, self).__init__(game, 10)
        self.logger = logging.getLogger("SimonSays")
        self.current_award = 15000000
        self.current_shot = LEFT_RAMP
        self.num_hits = 3
        self.instructions_showing = False
        self.screen = base.screenManager.getScreen("simon_says")
        self.timer_paused = False
        self.current_move_delay = 0.5
        self.currently_taking_input = False
        self.current_moves = []
        self.current_player_moves = []
        self.current_round = 1
        self.good_hits = 1
        
        
    def mode_started(self):
        self.logger.info("Starting Simon Says mode...")
        self.current_award = 15000000
        self.current_shot = LEFT_RAMP
        self.num_hits = 3
        self.timer_paused = False
        base.screenManager.showScreen("simon_says")
        self.screen.show_instructions()
        self.instructions_showing = True
        self.currently_taking_input = False
        self.update_lamps()
        self.current_move_delay = 0.5
        self.delay('show_instructions', event_type=None, delay=3, handler=self.start)
        self.current_moves = []
        self.current_player_moves = []
        self.current_round = 1
        self.good_hits = 1
        self.game.close_divertor()
        
        
    def start(self):
        self.instructions_showing = False
        self.screen.hide_instructions()
        self.game.base_game_mode.release_bottomPopper()
        self.screen.show_award(self.current_award)
        self.pause_timer(4)
        self.dec_award()
        self.game.sound.play("simon_says",fade_music=True)
        self.show_message("Shoot left ramp!", 2)
        
    def mode_stopped(self):
        self.logger.info("Stopping Simon Says mode...")
        base.screenManager.hideScreen("simon_says")
        self.game.play_music()
        self.game.update_lamps()
        if self.game.trough.num_balls_in_play >= 1:
            if self.current_round < 4:
                self.game.sound.play("simon_pathetic",fade_music=True)
            
            if self.game.current_player().claw_lit:
                self.game.open_divertor()
            
            self.game.gi_on()
    
    def update_lamps(self):
        if self.current_shot == LEFT_RAMP:
            self.game.lamps.quickFreeze.schedule(     schedule=0b00000000000000000000000000111111,cycle_seconds=1,now=True)
            self.game.lamps.leftRampCarChase.schedule(schedule=0b00000000000000000000111111000000,cycle_seconds=1,now=True)
            self.game.lamps.leftRampExplode.schedule( schedule=0b00000000000000111111000000000000,cycle_seconds=1,now=True)
            self.game.lamps.leftRampJackpot.schedule( schedule=0b00000000111111000000000000000000,cycle_seconds=1,now=True)
            self.game.lamps.leftRampArrow.schedule(   schedule=0b11111111000000000000000000000000,cycle_seconds=1,now=True)
            self.delay('update_lamps', event_type=None, delay=1, handler=self.update_lamps)
        elif self.current_shot == RIGHT_RAMP:
            self.game.lamps.clawReady.schedule(        schedule=0b00000000000000000000000000111111,cycle_seconds=1,now=True)
            self.game.lamps.rightRampCarChase.schedule(schedule=0b00000000000000000000111111000000,cycle_seconds=1,now=True)
            self.game.lamps.rightRampExplode.schedule( schedule=0b00000000000000111111000000000000,cycle_seconds=1,now=True)
            self.game.lamps.rightRampJackpot.schedule( schedule=0b00000000111111000000000000000000,cycle_seconds=1,now=True)
            self.game.lamps.rightRampArrow.schedule(   schedule=0b11111111000000000000000000000000,cycle_seconds=1,now=True)
            self.delay('update_lamps', event_type=None, delay=1, handler=self.update_lamps)
        elif self.current_shot == SIDE_SCOOP:
            self.game.lamps.undergroundArrow.schedule(0xFF00FF00,cycle_seconds=0,now=True)
        
    def sw_leftRampExit_active(self, sw):
        if self.current_shot == LEFT_RAMP:
            self.current_shot = RIGHT_RAMP
            self.game.score(self.current_award)
            self.show_award("right")
            self.current_award += 15000000
            self.game.sound.play('ss_ramp1',fade_music=True)
            self.game.sound.play("simon_says",fade_music=True)
        
    def sw_rightRampExit_active(self, sw):
        if self.current_shot == RIGHT_RAMP:
            self.current_shot = SIDE_SCOOP
            self.game.score(self.current_award)
            self.show_award("side")
            self.current_award += 15000000
            self.game.sound.play('ss_ramp2',fade_music=True)
            self.game.sound.play("simon_says",fade_music=True)
    
    def sw_bottomPopper_active_for_250ms(self, sw):
        if self.instructions_showing == True:
            return
        if not self.current_shot == SIDE_SCOOP:
            self.game.base_game_mode.release_bottomPopper()
            self.pause_timer(5)
        else:
            # Move on to round 2
            self.cancel_delayed('simon_laugh')
            self.game.enable_flippers(False)
            self.game.score(self.current_award)
            self.show_award()
            self.cancel_delayed('dec_award')
            self.screen.hide_award()
            self.delay('start_r2', event_type=None, delay=2, handler=self.show_r2_instructions)
            
    def show_r2_instructions(self):
        self.screen.show_instructions2()
        self.delay('start_r2', event_type=None, delay=5, handler=self.start_r2)
        self.game.sound.play('ss_r2',fade_music=True)
        self.delay('play_music', event_type=None, delay=2.5, handler=self.play_r2_music)
        
    def play_r2_music(self):
        self.game.sound.play_music("simon_r2",-1)
        
    def start_r2(self):
        self.screen.hide_award()
        self.screen.hide_instructions2()
        self.cancel_delayed('dec_award')
        self.screen.show_color("off")
        self.generate_move_list(self.num_hits)
        self.game.sound.play("simon_says", fade_music=True)
        self.delay('play_moves',event_type=None, delay=1, handler=self.play_move_list)
        self.game.gi_off()
    
    def release_popper(self):
        if self.game.current_player().computer_lit:
            self.game.computer.start_award()
            return
        
        self.game.base_game_mode.release_bottomPopper()
        
    def dec_award(self):
        if self.timer_paused or self.instructions_showing:
            self.delay('dec_award',event_type=None,delay=0.25,handler=self.dec_award)
            return
        if self.current_award <= 0:
            self.game.modes.remove(self)
            return
        
        self.current_award -= 250000
        self.screen.show_award(self.current_award)
        self.delay('dec_award',event_type=None,delay=0.25,handler=self.dec_award)
        
    def show_award(self,side = ""):
        msg = "SIMON SAYS AWARD:\n"+str(base.format_score(self.current_award))
        if side == "right":
            msg += "\nShoot right ramp!"
        if side == "side":
            msg += "\nShoot side scoop!"
        base.screenManager.showModalMessage(
                                                message = msg,
                                                time = 2.0,
                                                scale = 0.2,
                                                font = "eurostile.ttf",
                                                bg=(0,0,0,1),
                                                fg=(1,1,1,1),
                                                frame_color=((206.0/255.0),0,(224.0/255.0),1),
                                                blink_speed = 0.015,
                                                blink_color = (0,0,0,1)
                                                )
        
    def pause_timer(self, for_secs):
        self.timer_paused = True
        self.delay('timer_resume', event_type=None, delay=for_secs, handler=self.resume_timer)
        
    def resume_timer(self):
        self.timer_paused = False
        
    def generate_move_list(self, number_moves):
        choices = ["red","blue","yellow","green"]
        result = []
        for i in range(number_moves):
            next_move = random.choice(choices)
            result.append(random.choice(choices))
            
        self.current_moves = result
        self.current_player_moves = list(result)
    
    def play_move_list(self):
        if len(self.current_moves) <= 0:
            self.currently_taking_input = True
            
            self.show_message("Your Turn!", 2)
            
            return
        self.currently_taking_input = False
        current_move = self.current_moves.pop(0)
        self.screen.show_color(current_move)
        self.game.sound.play("ss_"+current_move, fade_music=True)
        self.delay('play_move',event_type=None,delay=self.current_move_delay, handler=self.play_move_list)
        self.delay('turn_current_color_off',event_type=None,delay=0.25,handler=self.screen.show_color,param="off")
        
    def sw_flipperLwR_active(self, sw):
        if not self.currently_taking_input: return
        self.validate_move("blue")
        self.screen.show_color("blue")
        self.game.sound.play("ss_blue", fade_music=True)
        self.delay('turn_current_color_off',event_type=None,delay=0.25,handler=self.screen.show_color,param="off")
        
    def sw_flipperLwL_active(self, sw):
        if not self.currently_taking_input: return
        self.validate_move("yellow")
        self.screen.show_color("yellow")
        self.game.sound.play("ss_yellow", fade_music=True)
        self.delay('turn_current_color_off',event_type=None,delay=0.25,handler=self.screen.show_color,param="off")
        
    def sw_leftHandle_active(self, sw):
        if not self.currently_taking_input: return
        self.validate_move("green")
        self.screen.show_color("green")
        self.game.sound.play("ss_green", fade_music=True)
        self.delay('turn_current_color_off',event_type=None,delay=0.25,handler=self.screen.show_color,param="off")
        
    def sw_rightHandle_active(self, sw):
        if not self.currently_taking_input: return
        self.validate_move("red")
        self.screen.show_color("red")
        self.game.sound.play("ss_red", fade_music=True)
        self.delay('turn_current_color_off',event_type=None,delay=0.25,handler=self.screen.show_color,param="off")
        
    def validate_move(self, color):
        if len(self.current_player_moves) <= 0: return
        current_move = self.current_player_moves.pop(0)
        if current_move == color:
            # The player got the right color
            self.good_hits += 1
            if len(self.current_player_moves) <= 0:
                # This was the last color in the stack, so the current round is completed
                self.currently_taking_input = False
                
                if self.current_round < 6:
                    self.current_round += 1
                    self.current_move_delay -= 0.05
                    self.num_hits += 1
                
                    self.show_message("Round " + str(self.current_round), 1.5)
                    self.delay('advance_round', event_type=None, delay=2, handler=self.advance_round)
                else:
                    self.game.enable_flippers(True)
                    self.game.score(2500000 * self.good_hits)
                    self.show_message("Mode Complete!\nTotal Award:\n" + str(base.format_score(2500000 * self.good_hits)))
                    self.delay('mode_over', event_type=None, delay=3, handler=self.game.modes.remove, param=self)
                    self.delay('release_ball', event_type=None, delay=2, handler=self.game.base_game_mode.release_bottomPopper)
                    self.game.sound.play("simon_niceshooting", fade_music=True)
                    
        else:
            # The player got the wrong color
            self.currently_taking_input = False
            self.game.sound.play("alarm", fade_music=True)
            self.game.score(2000000 * self.good_hits)
            self.show_message("Whoops, wrong move!\nTotal Award:\n" + str(base.format_score(2000000 * self.good_hits)))
            self.delay('mode_over', event_type=None, delay=3, handler=self.game.modes.remove, param=self)
            self.delay('release_ball', event_type=None, delay=2, handler=self.game.base_game_mode.release_bottomPopper)
            self.game.enable_flippers(True)
        
    def advance_round(self):
        self.game.sound.play("simon_says", fade_music=True)
        self.generate_move_list(self.num_hits)
        self.delay('play_hits', event_type=None, delay=1, handler=self.play_move_list)
        
    #
    #
    # PAUSE TIMER SWITCH HANDLERS
    #
    def sw_centerRamp_active(self, sw):
        self.pause_timer(3)
        
    def sw_leftRampEnter_active(self, sw):
        self.pause_timer(3)
    
    def sw_rightRampEnter_active(self, sw):
        self.pause_timer(3)
        
    def sw_leftJet_active(self, sw):
        self.pause_timer(3)
        
    def sw_rightJet_active(self, sw):
        self.pause_timer(3)
        
    def sw_bottomJet_active(self, sw):
        self.pause_timer(3)
        
    def sw_leftSlingshot_active(self, sw):
        self.pause_timer(3)
        
    def sw_rightSlingshot_active(self, sw):
        self.pause_timer(3)
        
    def show_message(self, message, time = 3):
        base.screenManager.showModalMessage(
                                                message = message,
                                                time = time,
                                                scale = 0.2,
                                                font = "eurostile.ttf",
                                                bg=(0,0,0,1),
                                                fg=(1,1,1,1),
                                                frame_color=((206.0/255.0),0,(224.0/255.0),1),
                                                blink_speed = 0.015,
                                                blink_color = (0,0,0,1)
                                                )