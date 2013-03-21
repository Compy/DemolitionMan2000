import procgame
import pinproc
import logging
from procgame import *
from functools import partial
from dmmode import DMMode

class BaseMode(DMMode):
    def __init__(self, game):
        super(BaseMode, self).__init__(game, 10)
        self.logger = logging.getLogger("BaseMode")
        self.ignore_switches = {}
        self.ignore_switches['right_ramp'] = False
        self.ignore_switches['left_ramp'] = False
        
        
    def mode_started(self):
        self.logger.info("Starting base mode...")
        #Disable any previously active lamp
        for lamp in self.game.lamps:
            lamp.disable()
                        
        #Update lamp status's for all modes
        self.game.update_lamps()
        
        self.game.lamps.gi01.pulse(0)
        self.game.lamps.gi02.pulse(0)
        self.game.lamps.gi03.pulse(0)
        self.game.lamps.gi04.pulse(0)
        self.game.lamps.gi05.pulse(0)
        
        # Enable the flippers
        self.game.enable_flippers(True)

        # Each time this mode is added to game Q, set this flag true.
        self.ball_starting = True
        self.ball_saved = False
        # Put the ball into play and start tracking it.
        self.game.trough.launch_balls(1, self.ball_launch_callback)

        # Enable ball search in case a ball gets stuck during gameplay.
        self.game.ball_search.enable()

        # Reset tilt warnings and status
        self.times_warned = 0;
        self.tilt_status = 0

        # In case a higher priority mode doesn't install it's own ball_drained
        # handler.
        self.game.trough.drain_callback = self.ball_drained_callback

        #ball save callback - exp
        self.game.ball_save.callback = self.ball_save_callback
        
        self.screen = base.screenManager.getScreen("score")
        
        base.screenManager.showScreen("score")
    
    def ball_drained_callback(self):
        logging.info("Drain callback")
        if self.game.trough.num_balls_in_play == 0:
            # We lost the last ball we had in play, start the bonus
            self.game.enable_flippers(False)
            self.finish_ball()
            self.stop_timer()
            
        for mode in self.game.modes:
            mode.ball_drained()
            
    def ball_save_callback(self):
        #anim = dmd.Animation().load(game_path+"dmd/eternal_life.dmd")
        #self.layer = dmd.AnimatedLayer(frames=anim.frames,hold=False)
        #self.game.sound.play_voice('dont_touch_anything')
        #self.game.sound.play('electricity')
        base.screenManager.showModalMessage(
                                            message="Ball Saved!", 
                                            modal_name="ball_save", 
                                            fg=(1,0,0,1),
                                            frame_color=(1,0,0,1),
                                            blink_speed=0.030,
                                            blink_color=(0,0,0,0),
                                            bg=(0,0,0,1), 
                                            start_location=(1.5,0,0),
                                            end_location=(0,0,0),
                                            animation='slide',
                                            time = 4)
        self.ball_saved = True
        self.game.sound.play('dontmove')
        
            
    def ball_launch_callback(self):
        #print("Debug - Ball Starting var is:"+str(self.ball_starting))
        if self.ball_starting:
            #print("Debug - Starting Ball Save Lamp")
            self.game.ball_save.start_lamp()
            #start background music
            #print("Debug - Starting General Play Music")
            self.game.sound.play_music('ball_wait_start', -1)
    
    def mode_stopped(self):

        # Ensure flippers are disabled
        self.game.enable_flippers(enable=False)

        # Deactivate the ball search logic so it won't search due to no
        # switches being hit.
        self.game.ball_search.disable()

    def finish_ball(self):
        #self.game.sound.fadeout_music()
        self.game.modes.add(self.game.bonus)
        self.stop_timer()
        base.display_queue.put_nowait(partial(self.screen.update_timer_text, text="--"))
        

        # Only compute bonus if it wasn't tilted away. 23/02/2011
        #if not self.tilt_status:
        #            self.bonus.calculate(self.end_ball)
        #else:
        #            self.end_ball()


        # Turn off tilt display (if it was on) now that the ball has drained.
        #if self.tilt_status and self.layer == self.tilt_layer:
        #            self.layer = None

    def end_ball(self):
        #remove bonus mode
        #self.game.modes.remove(self.bonus)
                
        # Tell the game object it can process the end of ball
        # (to end player's turn or shoot again)
        self.game.end_ball()
        
    def ignore_switch(self, switch, time = 1.5):
        self.ignore_switches[switch] = True
        self.delay('unignore_' + switch, event_type=None, delay=time, handler=self.unignore_switch, param=switch)
        
    def unignore_switch(self, switch):
        self.ignore_switches[switch] = False
    
    def sw_phantomSwitch_active(self,sw):
        if not self.game.SIMULATE: return
        # on a first press, end multiball if we're above 1 ball in play
        if self.game.trough.num_balls_in_play > 1:
            self.game.trough.num_balls_in_play = 1
        # if only one ball is in play, end ball
        else:
            self.game.trough.num_balls_in_play = 0
        self.ball_drained_callback()
    
    
    def sw_leftSlingshot_active(self, sw):
        self.game.score(230)
        self.game.sound.play("slingshot")
        self.game.coils.ejectFlasher.pulse(60)
        
    def sw_rightSlingshot_active(self, sw):
        self.game.score(230)
        self.game.sound.play("slingshot")
        self.game.coils.lowerReboundFlasher.pulse(60)
        
    def sw_flipperLwR_closed_for_3s(self, sw):
        if not self.game.status_display_mode.is_started():
            self.game.modes.add(self.game.status_display_mode)
            self.game.status_held_flipper = 'R'
            
    def sw_flipperLwL_closed_for_3s(self, sw):
        if not self.game.status_display_mode.is_started():
            self.game.modes.add(self.game.status_display_mode)
            self.game.status_held_flipper = 'L'
            
    def sw_leftJet_active(self, sw):
        self.add_acmag_percentage()
        self.game.sound.play("jet")
        self.game.score(510)
        self.pause_timer(3)
        
    def sw_rightJet_active(self, sw):
        self.add_acmag_percentage()
        self.game.sound.play("jet")
        self.game.score(510)
        self.pause_timer(3)
        
    def sw_bottomJet_active(self, sw):
        self.add_acmag_percentage()
        self.game.sound.play("jet")
        self.game.score(510)
        self.pause_timer(3)
    
    def add_acmag_percentage(self):
        # If the player has already completed acmag, ignore it
        if self.game.current_player().acmag: return
        
        if self.game.current_player().acmag_percentage < 100:
            self.game.current_player().acmag_percentage += 5
            self.cancel_delayed('hide_acmag_text')
            self.delay(name='hide_acmag_text', event_type=None, delay=2.5, handler=self.screen.hide_acmag_text)
            base.display_queue.put_nowait(partial(self.screen.update_acmag_text, text=str(self.game.current_player().acmag_percentage) + "%"))
        
        if self.game.current_player().acmag_percentage == 100:
            # Start acmag
            self.game.current_player().acmag = True
            self.game.modes.add(self.game.acmag)
    
    def sw_startButton_active(self, sw):
        if self.game.ball == 1:
            p = self.game.add_player()
            if p != False:
                base.screenManager.showModalMessage(message=p.name + " added", modal_name="player_add", bg=(0,0,1,1), time = 2)
            
    def sw_eject_closed_for_500ms(self, sw):
        self.game.coils.eject.pulse()
        
    def sw_bottomPopper_active_for_250ms(self, sw):
        if self.game.current_player().arrow_subway:
            self.do_laser_millions()
            self.game.current_player().arrow_subway = False
            self.game.lamps.undergroundArrow.disable()
            
            
        # If computer is lit, don't do anything because the computer mode will handle it
        if self.game.current_player().computer_lit:
            self.game.computer.start_award()
            return
        self.release_bottomPopper()
        self.logger.info("Ejecting bottom popper")
        
    def release_bottomPopper(self):
        self.game.sound.play("vuk")
        self.game.lampController.play_show("vuk", repeat=False)
        self.delay('vuk', event_type=None, delay=1, handler=self.game.coils.bottomPopper.pulse, param=50)
        
    def sw_topPopper_active_for_700ms(self, sw):
        if self.game.current_player().extraball_lit:
            self.game.gi_off()
            self.game.sound.play("extraball")
            self.game.current_player().extra_balls += 1
            self.delay('top_vuk',event_type=None,delay=3,handler=self.post_extraball_release)
            self.game.lamps.extraBall.disable()
            self.game.current_player().extraball_lit = False
        else:
            self.game.coils.topPopper.pulse()
            
    def post_extraball_release(self):
        self.game.gi_on()
        self.game.sound.play("explode")
        self.game.coils.topPopper.pulse()
        self.game.lampController.save_state('base')
        self.game.lampController.play_show("top_to_bottom",
                                           repeat=False,
                                           callback=self.game.update_lamps
                                           )
            
    def sw_ballLaunch_active(self, sw):
        if self.game.switches.shooterLane.is_active():
            self.game.coils.ballLaunch.pulse(50)
            self.game.lamps.gi01.schedule(schedule=0x55555555, cycle_seconds=0, now=True)
            self.game.lamps.gi02.schedule(schedule=0x55555555, cycle_seconds=0, now=True)
            self.game.lamps.gi03.schedule(schedule=0x55555555, cycle_seconds=0, now=True)
            self.game.lamps.gi04.schedule(schedule=0x55555555, cycle_seconds=0, now=True)
            self.game.lamps.gi05.schedule(schedule=0x55555555, cycle_seconds=0, now=True)
            self.delay(name='gi_reactivate', event_type=None, delay=0.3, handler=self.game.gi_on)
            self.game.sound.play("explode")
            self.game.sound.play_music('main',-1)
            self.game.lampController.save_state('base')
            self.game.lampController.play_show("ball_launch", 
                                               repeat=False,
                                               callback=self.game.update_lamps
                                               )

            
    def sw_shooterLane_active_for_500ms(self, sw):
        if self.ball_saved:
            self.game.coils.ballLaunch.pulse(50)
            self.game.sound.play("gunshots")
            self.ball_saved = False
            
    def sw_shooterLane_open_for_1s(self, sw):
        if self.ball_starting:
            self.ball_starting = False
            self.game.ball_save.start(num_balls_to_save=1, time=10, now=True, allow_multiple_saves=False)
            
    def sw_leftInlane_active(self, sw):
        self.game.sound.play("inlane")
        
    def sw_rightInlane_active(self, sw):
        self.game.sound.play("inlane")
    
    def sw_leftOutlane_active(self, sw):
        if not self.ball_saved:
            self.stop_timer()
            self.game.sound.play_music("drain")
            self.game.bonus_preemptive = True
            self.game.lampController.play_show("top_to_bottom", repeat=False, callback=self.game.dim_lower_pf)
        else:
            self.game.bonus_preemptive = False
        
    def sw_rightOutlane_active(self, sw):
        if not self.ball_saved:
            self.stop_timer()
            self.game.sound.play_music("drain")
            self.game.bonus_preemptive = True
            self.game.lampController.play_show("top_to_bottom", repeat=False, callback=self.game.dim_lower_pf)
        else:
            self.game.bonus_preemptive = False
        
    def set_timer(self, time = 30):
        self.game.current_player().timer = time;
        
    def start_timer(self):
        self.delay(name='global_mode_timer', event_type=None, delay=1, handler=self._dec_global_timer)
        
    def stop_timer(self):
        self.cancel_delayed('global_mode_timer')
        self.cancel_delayed('timer_pause')
        
        if self.game.current_player().timer <= 0:
            base.display_queue.put_nowait(partial(self.screen.update_timer_text, text="--"))
        
    def pause_timer(self, pause_secs):
        self.stop_timer()
        self.cancel_delayed('timer_pause')
        self.delay('timer_pause', event_type=None, delay=pause_secs, handler=self.start_timer)
        
    def add_time(self, time_to_add, max_time = 30):
        self.game.current_player().timer += time_to_add
        if self.game.current_player().timer > max_time:
            self.game.current_player().timer = max_time
        
    def sw_centerRamp_active(self, sw):
        self.game.score(2010)
        if self.game.current_player().arrow_acmag:
            self.do_laser_millions()
            self.game.current_player().arrow_acmag = False
            self.game.lamps.centerRampArrow.disable()
        else:
            self.game.sound.play("acmag_hit")
        self.game.lampController.save_state('base')
        self.game.lampController.play_show("acmag",
                                           repeat=False,
                                           callback=self.game.update_lamps
                                           )
    def sw_leftLoop_active(self, sw):
        self.game.score(600)
        if self.game.current_player().arrow_left_loop:
            self.do_laser_millions()
            self.game.current_player().arrow_left_loop = False
            self.game.lamps.leftLoopArrow.disable()
            
    def sw_leftRampExit_active(self, sw):
        if self.game.current_player().arrow_left_ramp:
            self.do_laser_millions()
            self.game.current_player().arrow_left_ramp = False
            self.game.lamps.leftRampArrow.disable()
        
    def sw_upperLeftFlipperGate_active(self, sw):
        self.screen.spin_spinner()
        self.game.sound.play_delayed(key = "spinner", loops = 20, delay = 0.05, callback = partial(self.game.score, 1000))
        self.delay('spinner_sound', event_type=None, delay=1.3, handler=self.play_spinner_sound, param=2)
        
    def play_spinner_sound(self, level):
        if level == 2:
            self.game.sound.play_delayed(key = "spinner", loops = 5, delay = 0.25, callback = partial(self.game.score, 1000))
        
    def sw_sideRampExit_active(self, sw):
        if self.game.current_player().arrow_side_ramp:
            self.do_laser_millions()
            self.game.current_player().arrow_side_ramp = False
            self.game.lamps.sideRampArrow.disable()
            
    def sw_rightRampExit_active(self, sw):
        if self.game.current_player().arrow_right_ramp:
            self.do_laser_millions()
            self.game.current_player().arrow_right_ramp = False
            self.game.lamps.rightRampArrow.disable()
        
    def sw_rightFreeway_active(self, sw):
        if self.game.current_player().arrow_right_loop:
            self.do_laser_millions()
            self.game.current_player().arrow_right_loop = False
            self.game.lamps.rightLoopArrow.disable()
            return
            
        self.game.sound.play("loop")
        
    def sw_rightRampEnter_active(self, sw):
        if self.ignore_switches["right_ramp"]: return
        self.ignore_switch("right_ramp")
        self.game.sound.play("ramp_up")
        self.game.coils.rightRampFlasher.schedule(schedule=0x0000dddd, cycle_seconds=1, now=True)
        self.game.lampController.save_state('base')
        self.game.lampController.play_show("bottom_to_top",
                                           repeat=False,
                                           callback=self.game.update_lamps
                                           )
        
    def sw_leftRampEnter_active(self, sw):
        if self.ignore_switches["left_ramp"]: return
        self.ignore_switch("left_ramp")
        self.game.sound.play("ramp_up")
        self.game.coils.leftRampLwrFlasher.schedule(schedule=0x0000dddd, cycle_seconds=1, now=True)
        self.game.lampController.save_state('base')
        self.game.lampController.play_show("bottom_to_top",
                                           repeat=False,
                                           callback=self.game.update_lamps
                                           )
        
    def do_laser_millions(self):
        self.game.sound.play("zap")
        self.game.score(2000000)
        self.screen.show_laser_millions()
        
    def _dec_global_timer(self):
        self.game.current_player().timer -= 1
        if self.game.current_player().timer <= 0:
            # Timeout
            for mode in self.game.modes:
                if isinstance(mode, DMMode):
                    mode.timeout()
                    
            base.display_queue.put_nowait(partial(self.screen.update_timer_text, text="--"))
        else:
            self.logger.info("Global timer " + str(self.game.current_player().timer))
            self.delay(name='global_mode_timer', event_type=None, delay=1, handler=self._dec_global_timer)
            
            base.display_queue.put_nowait(partial(self.screen.update_timer_text, text=str(self.game.current_player().timer)))