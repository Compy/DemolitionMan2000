import procgame
import pinproc
import logging
from procgame import *
from functools import partial
from dmmode import DMMode
import random
import os

class BaseMode(DMMode):
    BLINK_SLOW = 0xf0f0f0f0
    BLINK_FAST = 0xbbbbbbbb
    
    def __init__(self, game):
        super(BaseMode, self).__init__(game, 10)
        self.logger = logging.getLogger("BaseMode")
        self.ignore_switches = {}
        self.ignore_switches['right_ramp'] = False
        self.ignore_switches['left_ramp'] = False
        self.mtl_shown = False
        self.quick_freeze_lit = False
        self.tilt_debounce = False
        
        self.retina_scan_active = [0,1,2,4,7,10,13,16,19,21,24,27,30,33,36,39,41,44,47,50]
        
        
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
        #self.game.ball_search.enable()

        # Reset tilt warnings and status
        self.times_warned = 0;
        self.tilt_status = 0

        # In case a higher priority mode doesn't install it's own ball_drained
        # handler.
        self.game.trough.drain_callback = self.ball_drained_callback

        #ball save callback - exp
        self.game.ball_save.callback = self.ball_save_callback
        
        self.screen = base.screenManager.getScreen("score")
        self.extraball_screen = base.screenManager.getScreen("extraball")
        
        base.screenManager.showScreen("score")
        self.mtl_shown = False
        self.quick_freeze_lit = False
        
        self.delay('stop_screensaver', event_type=None, delay=300, handler=self.stop_screensaver)
        self.current_ef_sound = random.randint(0,4)
        self.game.lamps.start.pulse(0)
        self.tilt_debounce = False
    
    
    def stop_screensaver(self):
        os.system("xscreensaver-command -deactivate")
        self.delay('stop_screensaver', event_type=None, delay=300, handler=self.stop_screensaver)
    
    def ball_drained_callback(self):
        if self.game.ball_save.is_active():
            return
        if self.game.trough.num_balls_in_play == 0:
            # We lost the last ball we had in play, start the bonus
            self.game.enable_flippers(False)
            self.finish_ball()
            self.stop_timer()
            self.game.current_player().timer = 0
            self.game.current_player().cfb_in_progress = False
            
        for mode in self.game.modes:
            mode.ball_drained()
            
    def ball_save_callback(self):
        #anim = dmd.Animation().load(game_path+"dmd/eternal_life.dmd")
        #self.layer = dmd.AnimatedLayer(frames=anim.frames,hold=False)
        #self.game.sound.play_voice('dont_touch_anything')
        #self.game.sound.play('electricity')
        self.ball_saved = True
        
        if self.game.current_player().cfb_in_progress:
            self.game.current_player().cfb_in_progress = False
            self.game.current_player().call_for_backup = False
            self.game.sound.play("cfb",fade_music=True)
            base.display_queue.put_nowait(partial(self.screen.update_hud))
            return
        
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
        
        self.game.sound.play('dontmove',fade_music=True)
        
            
    def ball_launch_callback(self):
        #print("Debug - Ball Starting var is:"+str(self.ball_starting))
        if self.ball_starting:
            #print("Debug - Starting Ball Save Lamp")
            self.game.ball_save.start_lamp()
            #start background music
            #print("Debug - Starting General Play Music")
            if not self.game.current_player().multiball_lit:
                self.game.sound.play_music('ball_wait_start', -1)
            else:
                self.game.sound.play_music('fortressmb', -1)
            #self.game.sound.play_music('chase',-1)
    
    def mode_stopped(self):

        # Ensure flippers are disabled
        self.game.enable_flippers(enable=False)

        # Deactivate the ball search logic so it won't search due to no
        # switches being hit.
        #self.game.ball_search.disable()
        self.cancel_delayed('quick_freeze')
        self.game.current_player().cfb_in_progress = False

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
        
    def light_quick_freeze(self, speed = "slow"):
        if speed == "slow":
            self.quick_freeze_lit = True
            self.game.lamps.quickFreeze.schedule(schedule=self.BLINK_SLOW,cycle_seconds=0,now=True)
            self.delay("quick_freeze", event_type=None, delay=4, handler=self.light_quick_freeze, param="fast")
        elif speed == "fast":
            self.quick_freeze_lit = True
            self.game.lamps.quickFreeze.schedule(schedule=self.BLINK_FAST,cycle_seconds=0,now=True)
            self.delay("quick_freeze", event_type=None, delay=3, handler=self.light_quick_freeze, param="off")
        elif speed == "off":
            self.quick_freeze_lit = False
            self.game.lamps.quickFreeze.disable()
    
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
        if self.game.current_player().tilted: return
        if self.game.trough.num_balls_in_play == 1: self.pause_timer(3)
        self.game.score(230)
        self.game.sound.play("slingshot")
        self.game.coils.ejectFlasher.pulse(60)
        
    def sw_rightSlingshot_active(self, sw):
        
        if self.game.current_player().tilted: return
        if self.game.trough.num_balls_in_play == 1: self.pause_timer(3)
        self.game.score(230)
        self.game.sound.play("slingshot")
        self.game.coils.lowerReboundFlasher.pulse(60)
        
    def sw_flipperLwR_active(self, sw):
        if not self.mtl_shown: return
        currentM = self.game.current_player().mlit
        currentT = self.game.current_player().tlit
        currentL = self.game.current_player().llit
        
        self.game.current_player().mlit = currentL
        self.game.current_player().tlit = currentM
        self.game.current_player().llit = currentT
        
        self.show_mtl(False)
        
    def sw_rightHandle_active(self, sw):
        if self.game.current_player().tilted: return
        self.sw_flipperLwR_active(sw)
        
    def sw_flipperLwR_closed_for_3s(self, sw):
        if not self.game.status_display_mode.is_started():
            self.game.modes.add(self.game.status_display_mode)
            self.game.status_held_flipper = 'R'
            
    def sw_flipperLwL_closed_for_3s(self, sw):
        if not self.game.status_display_mode.is_started():
            self.game.modes.add(self.game.status_display_mode)
            self.game.status_held_flipper = 'L'
            
    def score_superjet(self):
        self.game.sound.play("superjet")
        self.game.score(1000000)
        self.game.current_player().super_jets_left -= 1
        
        if self.game.current_player().super_jets_left <= 0:
            self.game.current_player().super_jets = False
            self.game.sound.play("computer_superjets_complete",fade_music=True)
            
    def sw_leftJet_active(self, sw):
        if self.game.current_player().tilted: return
        self.show_mtl()
        self.add_acmag_percentage()
        
        if self.game.current_player().super_jets:
            self.score_superjet()
        else:
            self.game.sound.play("jet")
            self.game.score(510)
        self.game.coils.jetsFlasher.pulse(40)
        if self.game.trough.num_balls_in_play == 1: self.pause_timer(3)
        
    def sw_rightJet_active(self, sw):
        if self.game.current_player().tilted: return
        self.show_mtl()
        self.add_acmag_percentage()
        if self.game.current_player().super_jets:
            self.score_superjet()
        else:
            self.game.sound.play("jet")
            self.game.score(510)
        self.game.coils.jetsFlasher.pulse(40)
        if self.game.trough.num_balls_in_play == 1: self.pause_timer(3)
        
    def sw_bottomJet_active(self, sw):
        if self.game.current_player().tilted: return
        self.show_mtl()
        self.add_acmag_percentage()
        if self.game.current_player().super_jets:
            self.score_superjet()
        else:
            self.game.sound.play("jet")
            self.game.score(510)
        self.game.coils.jetsFlasher.pulse(40)
        if self.game.trough.num_balls_in_play == 1: self.pause_timer(3)
    
    def add_acmag_percentage(self):
        # If the player has already completed acmag, ignore it
        if self.game.current_player().acmag or self.game.fortress.is_started(): return
        
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
        if self.game.current_player().tilted: return
        if self.game.ball == 1:
            p = self.game.add_player()
            if p != False:
                base.screenManager.showModalMessage(message=p.name + " added", modal_name="player_add", bg=(0,0,1,1), time = 2)
            
    def sw_eject_active_for_100ms(self, sw):
        if self.game.current_player().tilted:
            self.game.coils.eject.pulse()
            return
        
        self.game.current_player().retina_scans += 1
        if not self.game.current_player().retina_scan_ready:
            if self.game.current_player().retina_scans in self.retina_scan_active:
                self.game.current_player().retina_scan_ready = True
            self.game.score(110000)
        else:
            self.game.current_player().retina_scan_ready = False
            self.game.score(self.game.current_player().retina_value)
            self.game.current_player().retina_value += 3000000
            if not self.game.current_player().claw_lit:
                self.game.current_player().access_claw_lit = True
            
        self.update_lamps()
        self.game.coils.ejectFlasher.schedule(schedule=0xaaaaaaaa, cycle_seconds=1, now=True)
        self.delay('retina_eject', event_type=None, delay=3, handler=self.retina_eject)
        self.game.sound.play("retina")
        if self.game.trough.num_balls_in_play == 1: self.pause_timer(2)
        self.screen.show_retina()
        self.delay('retina_show', event_type=None, delay=1, handler=self.show_retina_text, param=not self.game.current_player().retina_scan_ready)
        
    def show_retina(self):
        self.screen.show_retina()
        self.delay('retina_hide', event_type=None, delay=3, handler=self.hide_retina)
        
    def hide_retina(self):
        self.screen.hide_retina()
        
    def show_retina_text(self, is_accepted = False):
        if is_accepted:
            text = "SCAN\nACCEPTED"
            color = (0,1,1,1)
        else:
            text = "SCAN\nDENIED"
            color = (1,0,0,1)
        base.screenManager.showModalMessage(
                                            message=text, 
                                            modal_name="retina", 
                                            fg=color,
                                            frame_color=(0,0,0,0),
                                            blink_speed=0.25,
                                            blink_color=(0,0,0,0),
                                            bg=(0,0,0,1),
                                            start_location=(-0.9,0,-0.5),
                                            scale=(0.1,0.1,0.1),
                                            time = 2)
        
    def retina_eject(self):
        self.game.sound.play("retina_eject")
        self.game.coils.eject.pulse()
        self.screen.hide_retina()
        self.game.coils.ejectFlasher.schedule(schedule=0x0000aaaa, cycle_seconds=1, now=True)
        
    def add_explode(self):
        base.screenManager.showModalMessage(
                                                message = "Explode Lamp Added",
                                                time = 2.0,
                                                scale = 0.2,
                                                font = "eurostile.ttf",
                                                bg=(0,0,0,1),
                                                fg=(1,1,1,1),
                                                frame_color=(0,0,1,1),
                                                blink_speed = 0.015,
                                                blink_color = (0,0,0,1)
                                                )
        self.game.explode.add_explode_lamp()
        
    def sw_bottomPopper_active_for_250ms(self, sw):
        
        if self.game.current_player().tilted:
            self.game.coils.bottomPopper.pulse(30)
            return
        
        if self.game.simon_says.is_started(): return
        
        if not self.game.current_player().computer_lit and not self.game.current_player().arrow_subway:
            self.add_explode()
        
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
        if self.game.current_player().tilted:
            self.game.coils.topPopper.pulse(30)
            return
        
        if self.game.trough.num_balls_in_play == 1: self.pause_timer(3)
        if self.game.current_player().extraball_lit:
            self.game.gi_off()
            self.game.sound.play("extraball")
            self.game.current_player().extra_balls += 1
            self.delay('top_vuk',event_type=None,delay=3,handler=self.post_extraball_release)
            self.game.lamps.extraBall.disable()
            self.game.lamps.shootAgain.pulse(0)
            self.game.current_player().extraball_lit = False
            base.screenManager.hideScreen("score")
            base.screenManager.showScreen("extraball")
            return
        
        if self.game.current_player().multiball_lit and not self.game.simon_says.is_started():
            self.game.modes.add(self.game.fortress)
            return
        
        self.game.current_player().top_popper_shots += 1
        
        if self.game.current_player().top_popper_shots == 2:
            self.game.current_player().top_popper_shots = 0
        
            self.do_ef_bonus()
        else:
            # Do big points
            self.game.score(1000000)
            self.screen.set_award_text("BIG POINTS\n1,000,000")
            self.screen.show_top_award()
            self.game.sound.play('top_random_award', fade_music=True)
            self.delay('random_award', event_type=None, delay=3, handler=self.end_big_points)
            
    def end_big_points(self):
        self.screen.hide_top_award()
        self.game.coils.topPopper.pulse()
            
    def do_ef_bonus(self):
        self.screen.show_ef_bonus()
        self.game.score(5000000)
        self.delay('ef_bonus', event_type=None, delay=3, handler=self.end_ef_bonus)
        
        ef_sounds = ['leary_jello','leary_bacon','leary_cigar','leary_tbone']
        self.game.sound.play(ef_sounds[self.current_ef_sound], fade_music=True)
        self.current_ef_sound += 1
        if self.current_ef_sound > len(ef_sounds) - 1:
            self.current_ef_sound = 0
    
    def end_ef_bonus(self):
        self.screen.hide_ef_bonus()
        self.game.coils.topPopper.pulse()
            
    def post_extraball_release(self):
        base.screenManager.hideScreen("extraball")
        base.screenManager.showScreen("score")
        if self.game.current_player().multiball_lit:
            self.game.modes.add(self.game.fortress)
            return
        
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
            
            if not self.game.current_player().multiball_lit:
                self.game.sound.play_music('main',-1)
            
            self.game.lampController.save_state('base')
            self.game.lampController.play_show("ball_launch", 
                                               repeat=False,
                                               callback=self.game.update_lamps
                                               )
        
        elif self.game.current_player().call_for_backup and not self.game.current_player().cfb_in_progress:
            self.game.ball_save.add(4.0, allow_multiple_saves=False)
            self.game.current_player().cfb_in_progress = True
            self.delay('cfb_timeout', event_type=None, delay=4, handler=self.cfb_timeout)

    def cfb_timeout(self):
        self.game.current_player().cfb_in_progress = False
            
    def sw_shooterLane_active_for_500ms(self, sw):
        if self.ball_saved:
            self.game.coils.ballLaunch.pulse(50)
            self.game.sound.play("gunshots")
            self.ball_saved = False
            
        if self.game.wtsa.is_started() or \
            self.game.fortress.is_started():
            self.game.coils.ballLaunch.pulse(50)
            
    def sw_shooterLane_open_for_1s(self, sw):
        if self.ball_starting:
            self.ball_starting = False
            self.game.ball_save.start(num_balls_to_save=1, time=10, now=True, allow_multiple_saves=False)
            
    def sw_leftInlane_active(self, sw):
        if self.game.current_player().tilted: return
        self.game.sound.play("inlane")
        
        if self.game.current_player().access_claw_lit and not self.game.fortress.is_started() \
            and not self.game.wtsa.is_started() \
            and not self.game.car_chase.is_started():
            self.game.current_player().claw_lit = True
            self.game.current_player().access_claw_lit = False
            self.game.sound.play("cryo_claw_activated", fade_music=True)
            self.game.open_divertor()
            self.update_lamps()
        
    def sw_rightInlane_active(self, sw):
        if self.game.current_player().tilted: return
        self.game.sound.play("inlane")
        if self.game.current_player().quick_freeze:
            self.light_quick_freeze("slow")
    
    def sw_leftOutlane_active(self, sw):
        if self.game.current_player().tilted: return
        
        if not self.ball_saved and self.game.trough.num_balls_in_play == 1 and not self.game.current_player().call_for_backup:
            self.stop_timer()
            self.game.sound.play_music("drain")
            self.game.bonus_preemptive = True
            self.game.lampController.play_show("top_to_bottom", repeat=False, callback=self.game.dim_lower_pf)
        else:
            self.game.bonus_preemptive = False
        
    def sw_rightOutlane_active(self, sw):
        if self.game.current_player().tilted: return
        if not self.ball_saved and self.game.trough.num_balls_in_play == 1 and not self.game.current_player().call_for_backup:
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
        
    def pause_timer(self, pause_secs = 0):
        self.stop_timer()
        self.cancel_delayed('timer_pause')
        if self.game.current_player().timer <= 0:
            return
        if pause_secs > 0:
            self.delay('timer_pause', event_type=None, delay=pause_secs, handler=self.start_timer)
        
    def add_time(self, time_to_add, max_time = 30):
        self.game.current_player().timer += time_to_add
        if self.game.current_player().timer > max_time:
            self.game.current_player().timer = max_time
        
    def sw_centerRamp_active(self, sw):
        if self.game.current_player().tilted: return
        self.game.score(2010)
        if self.game.trough.num_balls_in_play == 1: self.pause_timer(3)
        if self.game.current_player().arrow_acmag:
            self.do_laser_millions()
            self.game.current_player().arrow_acmag = False
            self.game.lamps.centerRampArrow.disable()
        else:
            self.game.coils.divertorFlasher.schedule(schedule=0x00005555, cycle_seconds=1, now=True)
            self.game.sound.play("acmag_hit")
        self.game.lampController.save_state('base')
        self.game.lampController.play_show("acmag",
                                           repeat=False,
                                           callback=self.game.update_lamps
                                           )
        self.show_mtl()
    def sw_leftLoop_active(self, sw):
        if self.game.current_player().tilted: return
        self.game.score(600)
        self.pause_timer(2)
        if self.game.current_player().arrow_left_loop:
            self.do_laser_millions()
            self.game.current_player().arrow_left_loop = False
            self.game.lamps.leftLoopArrow.disable()
            
    def sw_leftRampExit_active(self, sw):
        if self.game.current_player().tilted: return
        if self.game.current_player().arrow_left_ramp:
            self.do_laser_millions()
            self.game.current_player().arrow_left_ramp = False
            self.game.lamps.leftRampArrow.disable()
            
        if self.quick_freeze_lit:
            self.quick_freeze_lit = False
            self.game.current_player().quick_freeze = False
            self.game.lamps.lightQuickFreeze.disable()
            self.quick_freeze()
            
        self.game.score(2500)
            
    def quick_freeze(self):
        self.game.sound.play("freeze")
        self.check_multiball()
            
    def check_multiball(self):
        p = self.game.current_player()
        
        if not p.freeze1:
            p.freeze1 = True
        elif not p.freeze2:
            p.freeze2 = True
        elif not p.freeze3:
            p.freeze3 = True
        elif not p.freeze4:
            p.freeze4 = True
        
        if p.freeze1 and p.freeze2 and p.freeze3 and p.freeze4:
            # get mb ready
            p.multiball_lit = True
            self.game.sound.play_music("mb_ready",-1)
        
        self.update_lamps()
        
    def sw_upperLeftFlipperGate_active(self, sw):
        if self.game.current_player().tilted: return
        self.screen.spin_spinner()
        self.game.sound.play_delayed(key = "spinner", loops = 20, delay = 0.05, callback = partial(self.game.score, 1000))
        self.delay('spinner_sound', event_type=None, delay=1.3, handler=self.play_spinner_sound, param=2)
        self.show_mtl()
        
    def play_spinner_sound(self, level):
        if level == 2:
            self.game.sound.play_delayed(key = "spinner", loops = 5, delay = 0.25, callback = partial(self.game.score, 1000))
        
    def sw_sideRampExit_active(self, sw):
        if self.game.current_player().tilted: return
        if self.game.current_player().arrow_side_ramp:
            self.do_laser_millions()
            self.game.current_player().arrow_side_ramp = False
            self.game.lamps.sideRampArrow.disable()
            
        else:
            if not base.screenManager.isModalBeingShown() and not self.game.skill_shot_mode.is_started():
                base.screenManager.getScreen("score").show_standup_collected()
            
            self.delay('spot_standup', event_type=None, delay=1, handler=self.spot_standup)
            
    def spot_standup(self):
        p = self.game.current_player()
        if not p.standup1:
            self.sw_standUp1_active(None)
        elif not p.standup2:
            self.sw_standUp2_active(None)
        elif not p.standup3:
            self.sw_standUp3_active(None)
        elif not p.standup4:
            self.sw_standUp4_active(None)
        elif not p.standup5:
            self.sw_standUp5_active(None)
            
        self.game.update_lamps()
        
            
    def sw_rightRampExit_active(self, sw):
        if self.game.current_player().tilted: return
        if self.game.current_player().arrow_right_ramp:
            self.do_laser_millions()
            self.game.current_player().arrow_right_ramp = False
            self.game.lamps.rightRampArrow.disable()
            
        else:
            self.game.score(2500)
        
    def sw_rightFreeway_active(self, sw):
        if self.game.current_player().tilted: return
        self.pause_timer(3)
        if self.game.current_player().arrow_right_loop:
            self.do_laser_millions()
            self.game.current_player().arrow_right_loop = False
            self.game.lamps.rightLoopArrow.disable()
            return
            
        self.show_mtl()
        self.game.sound.play("loop")
        self.game.score(2500)
        
    def sw_rightRampEnter_active(self, sw):
        if self.game.current_player().tilted: return
        if self.ignore_switches["right_ramp"]: return
        if self.game.trough.num_balls_in_play == 1: self.pause_timer(3)
        self.ignore_switch("right_ramp")
        self.game.sound.play("ramp_up")
        self.game.coils.rightRampFlasher.schedule(schedule=0x0000dddd, cycle_seconds=1, now=True)
        self.game.lampController.save_state('base')
        self.game.lampController.play_show("bottom_to_top",
                                           repeat=False,
                                           callback=self.game.update_lamps
                                           )
        
    def sw_leftRampEnter_active(self, sw):
        if self.game.current_player().tilted: return
        
        if self.ignore_switches["left_ramp"]: return
        if self.game.trough.num_balls_in_play == 1: self.pause_timer(3)
        self.ignore_switch("left_ramp")
        self.game.sound.play("ramp_up")
        self.game.coils.leftRampLwrFlasher.schedule(schedule=0x0000dddd, cycle_seconds=1, now=True)
        self.game.lampController.save_state('base')
        self.game.lampController.play_show("bottom_to_top",
                                           repeat=False,
                                           callback=self.game.update_lamps
                                           )
        
    def sw_enter_active(self, sw):
        self.game.modes.remove(self)
        self.game.modes.add(self.game.service)
        #if self.game.current_player().call_for_backup and not self.game.current_player().cfb_in_progress:
        #    self.game.ball_save.add(4.0, allow_multiple_saves=False)
        #    self.game.current_player().cfb_in_progress = True
        
    def do_laser_millions(self):
        self.game.sound.play("zap")
        self.game.score(2000000)
        self.screen.show_laser_millions()
        
    def sw_mtlM_active(self, sw):
        if self.game.current_player().tilted: return
        self.pause_timer(3)
        self.game.current_player().mlit = True
        self.show_mtl()
        self.game.sound.play("mtl_whoosh")
    
    def sw_mtlT_active(self, sw):
        if self.game.current_player().tilted: return
        self.pause_timer(3)
        self.game.current_player().tlit = True
        self.show_mtl()
        self.game.sound.play("mtl_whoosh")
    
    def sw_mtlL_active(self, sw):
        if self.game.current_player().tilted: return
        if self.game.current_player().tilted: return
        self.pause_timer(3)
        self.game.current_player().llit = True
        self.show_mtl()
        self.game.sound.play("mtl_whoosh")
        
    def show_mtl(self, extend_timer = True):
        if not self.game.current_player().mlit and not self.game.current_player().tlit and not self.game.current_player().llit:
            return
        self.screen.hide_timer()
        self.screen.hide_ball()
        self.screen.hide_m()
        self.screen.hide_t()
        self.screen.hide_l()
        if self.game.current_player().mlit:
            self.screen.show_m()
        if self.game.current_player().tlit:
            self.screen.show_t()
        if self.game.current_player().llit:
            self.screen.show_l()
            
        if extend_timer:
            self.mtl_shown = True
                
            self.delay('hide_mtl', event_type=None, delay=5, handler=self.hide_mtl)
            
        if self.game.current_player().mlit and \
            self.game.current_player().tlit and \
            self.game.current_player().llit:
            self.game.current_player().mlit = False
            self.game.current_player().tlit = False
            self.game.current_player().llit = False
            self.game.sound.play("mtl_complete")
            self.game.current_player().bonus_x += 1
            base.display_queue.put_nowait(partial(self.screen.update_hud))
            base.screenManager.showModalMessage(
                                            message="BONUS\n" + str(self.game.current_player().bonus_x) + "X", 
                                            modal_name="bonus_increased",
                                            font = "motorwerk.ttf",
                                            fg=(1,1,1,1),
                                            frame_color=(1,0,0,1),
                                            blink_speed=0.030,
                                            blink_color=(0,0,0,0),
                                            bg=(0,0,0,1), 
                                            time = 2)
        
    def sw_standUp1_active(self, sw):
        if self.game.current_player().tilted: return
        self.game.lamps.standup1.schedule(schedule=0x55555555, cycle_seconds=1, now=True)
        self.delay('standup_1', delay=1, handler=self.game.lamps.standup1.pulse, param=0)
        self.game.sound.play("standup")
        
        if not self.game.current_player().standup1:
            self.game.current_player().standup1 = True
        
        self.game.score(1400)
        self.check_standups()
        
        if self.game.current_player().super_jets:
            self.game.current_player().super_jets_left += 1
    
    def sw_standUp2_active(self, sw):
        if self.game.current_player().tilted: return
        self.game.lamps.standup2.schedule(schedule=0x55555555, cycle_seconds=1, now=True)
        self.delay('standup_2', delay=1, handler=self.game.lamps.standup2.pulse, param=0)
        self.game.sound.play("standup")
        
        if not self.game.current_player().standup2:
            self.game.current_player().standup2 = True
            
        self.game.score(1400)
        self.check_standups()
        
        if self.game.current_player().super_jets:
            self.game.current_player().super_jets_left += 1
    
    def sw_standUp3_active(self, sw):
        if self.game.current_player().tilted: return
        self.game.lamps.standup3.schedule(schedule=0x55555555, cycle_seconds=1, now=True)
        self.delay('standup_3', delay=1, handler=self.game.lamps.standup3.pulse, param=0)
        self.game.sound.play("standup")
        
        if not self.game.current_player().standup3:
            self.game.current_player().standup3 = True
            
        self.game.score(1400)
        self.check_standups()
        
        if self.game.current_player().super_jets:
            self.game.current_player().super_jets_left += 1
    
    def sw_standUp4_active(self, sw):
        if self.game.current_player().tilted: return
        self.game.lamps.standup4.schedule(schedule=0x55555555, cycle_seconds=1, now=True)
        self.delay('standup_4', delay=1, handler=self.game.lamps.standup4.pulse, param=0)
        self.game.sound.play("standup")
        
        if not self.game.current_player().standup4:
            self.game.current_player().standup4 = True
            
        self.game.score(1400)
        self.check_standups()
        
        if self.game.current_player().super_jets:
            self.game.current_player().super_jets_left += 1
        
    def sw_eyeballStandup_active(self, sw):
        if self.game.current_player().tilted: return
        self.game.current_player().retina_value += 5000030
        self.game.current_player().retina_scan_ready = True
        self.game.coils.eyeBallFlasher.schedule(schedule=0x0000aaaa, cycle_seconds=1, now=True)
        self.game.score(1000000)
        self.update_lamps()
        
    
    def sw_standUp5_active(self, sw):
        if self.game.current_player().tilted: return
        self.game.lamps.standup5.schedule(schedule=0x55555555, cycle_seconds=1, now=True)
        self.delay('standup_5', delay=1, handler=self.game.lamps.standup5.pulse, param=0)
        self.game.sound.play("standup")
        
        if not self.game.current_player().standup5:
            self.game.current_player().standup5 = True
            
        self.game.score(1400)
        self.check_standups()
        
        if self.game.current_player().super_jets:
            self.game.current_player().super_jets_left += 1
    
    def debounce_tilt(self):
        self.tilt_debounce = False
    
    def sw_plumbBobTilt_active(self, sw):
        if self.game.current_player().tilted or self.tilt_debounce or self.game.switches.shooterLane.is_active(): return
        self.game.current_player().tilt_warnings += 1
        
        self.tilt_debounce = True
        self.delay('tilt_debounce', event_type=None, delay=2, handler=self.debounce_tilt)
        
        msg = "WARNING!!"
        time = 1.5
        speed = 0.030
        
        if self.game.current_player().tilt_warnings == 1:
            self.game.gi_off()
            self.delay('gi_on', event_type=None, delay=0.2, handler=self.game.gi_on)
        if self.game.current_player().tilt_warnings == 2:
            msg = msg + "\nWARNING!!"
            self.delay('gi_on', event_type=None, delay=0.2, handler=self.game.gi_on)
        
        self.game.sound.play("alarm",fade_music=True)
        
        if self.game.current_player().tilt_warnings >= 3:
            msg = "TILT"
            time = 5
            self.pause_timer(10)
            self.game.enable_flippers(False)
            self.cancel_delayed('gi_on')
            self.game.gi_off()
            self.game.sound.stop_music()
            self.game.current_player().tilted = True
            self.game.ball_save.disable()
            speed = 0.5
            
            for lamp in self.game.lamps:
                lamp.disable()
            
        base.screenManager.showModalMessage(
                                            message=msg, 
                                            modal_name="tilt",
                                            font = "motorwerk.ttf",
                                            fg=(1,1,1,1),
                                            frame_color=(1,0,0,1),
                                            blink_speed=speed,
                                            blink_color=(0,0,0,0),
                                            bg=(1,0,0,1), 
                                            time = time)
            
    def sw_slamTilt_active(self, sw):
        self.game.exit_code = -13
        self.game.exit = True
        
    def check_standups(self):
        if self.game.current_player().standup1 and \
            self.game.current_player().standup2 and \
            self.game.current_player().standup3 and \
            self.game.current_player().standup4 and \
            self.game.current_player().standup5:
            
            if not self.game.current_player().quick_freeze and not self.game.current_player().multiball_lit:
                self.game.current_player().quick_freeze = True
                self.game.sound.play("computer_quick_freeze_activated", fade_music=True)
                self.game.lamps.lightQuickFreeze.pulse(0)
            
            self.game.current_player().standup1 = False
            self.game.current_player().standup2 = False
            self.game.current_player().standup3 = False
            self.game.current_player().standup4 = False
            self.game.current_player().standup5 = False
            
            self.game.lamps.standup1.disable()
            self.game.lamps.standup2.disable()
            self.game.lamps.standup3.disable()
            self.game.lamps.standup4.disable()
            self.game.lamps.standup5.disable()
        
    def hide_mtl(self):
        self.screen.hide_m()
        self.screen.hide_t()
        self.screen.hide_l()
        self.screen.show_timer()
        self.screen.show_ball()
        self.mtl_shown = False
        
    def update_lamps(self):
        
        self.game.restore_player_feature_lamps()
        self.game.lamps.start.pulse(0)
        
        if self.game.current_player().extra_balls > 0:
            self.game.lamps.shootAgain.pulse(0)
            
        if self.game.current_player().standup1: self.game.lamps.standup1.pulse(0)
        if self.game.current_player().standup2: self.game.lamps.standup2.pulse(0)
        if self.game.current_player().standup3: self.game.lamps.standup3.pulse(0)
        if self.game.current_player().standup4: self.game.lamps.standup4.pulse(0)
        if self.game.current_player().standup5: self.game.lamps.standup5.pulse(0)
        
        p = self.game.current_player()
        
        if p.freeze1 and p.freeze2 and p.freeze3 and p.freeze4:
            # get mb ready
            p.multiball_lit = True
            self.game.lamps.freeze1.schedule(schedule=0xff00ff00, cycle_seconds=0, now=True)
            self.game.lamps.freeze2.schedule(schedule=0xff00ff00, cycle_seconds=0, now=True)
            self.game.lamps.freeze3.schedule(schedule=0xff00ff00, cycle_seconds=0, now=True)
            self.game.lamps.freeze4.schedule(schedule=0xff00ff00, cycle_seconds=0, now=True)
            
            self.game.lamps.fortressMultiball.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            
    def random_lamp_effect(self):
        schedule = [0x0000f0f0,0x0000e0e0,0x0000ff0f,0x0000eeee,0x00000e0e,0x00000f0f]
        flashers = ['clawFlasher','jetsFlasher','sideRampFlasher','leftRampUpFlasher',
                    'leftRampLwrFlasher','carChaseCenterFlasher','carChaseLowerFlasher',
                    'rightRampFlasher','ejectFlasher','carChaseUpFlasher','lowerReboundFlasher',
                    'eyeBallFlasher','centerRampFlasher','divertorFlasher','rightRampUpFlasher']
        for lamp in self.game.lamps:
            lamp.schedule(schedule=random.choice(schedule), cycle_seconds=1, now=True)
            
        for flasher in flashers:
            self.game.coils[flasher].schedule(schedule=random.choice(schedule), cycle_seconds=1, now=True)
            
        self.delay('restore_lamps', event_type=None, delay=0.8, handler=self.game.update_lamps)
        self.delay('gi_on', event_type=None, delay=0.5, handler=self.game.gi_on)
        
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