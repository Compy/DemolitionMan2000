import procgame
import pinproc
import logging
from procgame import *
from functools import partial
from dmmode import DMMode

class WizardBlocksMode(DMMode):
    def __init__(self, game):
        super(WizardBlocksMode, self).__init__(game, 10)
        self.logger = logging.getLogger("WizardBlocks")
        self.ignore_switches = {}
        self.ignore_switches['right_ramp'] = False
        self.ignore_switches['left_ramp'] = False
        
        
    def mode_started(self):
        self.logger.info("Starting Wizard Blocks mode...")
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
        
        self.screen = base.screenManager.getScreen("blocks")
        base.screenManager.showScreen("blocks")
        self.game.sound.play_music("wb", loops=-1)
        
    
    def ball_drained_callback(self):
        if self.game.ball_save.is_active():
            return
        if self.game.trough.num_balls_in_play == 0:
            # We lost the last ball we had in play, start the bonus
            self.game.enable_flippers(False)
            self.finish_ball()
            self.stop_timer()
            self.game.current_player().timer = 0
            
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
        
            
    def ball_launch_callback(self):
        #print("Debug - Ball Starting var is:"+str(self.ball_starting))
        if self.ball_starting:
            #print("Debug - Starting Ball Save Lamp")
            self.game.ball_save.start_lamp()
            #start background music
            #print("Debug - Starting General Play Music")
            #self.game.sound.play_music('chase',-1)
    
    def mode_stopped(self):

        # Ensure flippers are disabled
        self.game.enable_flippers(enable=False)

        # Deactivate the ball search logic so it won't search due to no
        # switches being hit.
        #self.game.ball_search.disable()

    def finish_ball(self):
        #self.game.sound.fadeout_music()
        # Add bonus mode, or something
        pass
        

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
        self.game.coils.ejectFlasher.pulse(60)
        
    def sw_rightSlingshot_active(self, sw):
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
        self.game.coils.jetsFlasher.pulse(40)
        
    def sw_rightJet_active(self, sw):
        self.game.coils.jetsFlasher.pulse(40)
        
    def sw_bottomJet_active(self, sw):
        self.game.coils.jetsFlasher.pulse(40)

    def sw_eject_active_for_100ms(self, sw):
        self.game.coils.ejectFlasher.schedule(schedule=0xaaaaaaaa, cycle_seconds=1, now=True)
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
        self.game.coils.topPopper.pulse()
            
    def sw_ballLaunch_active(self, sw):
        if self.game.switches.shooterLane.is_active():
            self.game.coils.ballLaunch.pulse(50)
            self.game.lamps.gi01.schedule(schedule=0x55555555, cycle_seconds=0, now=True)
            self.game.lamps.gi02.schedule(schedule=0x55555555, cycle_seconds=0, now=True)
            self.game.lamps.gi03.schedule(schedule=0x55555555, cycle_seconds=0, now=True)
            self.game.lamps.gi04.schedule(schedule=0x55555555, cycle_seconds=0, now=True)
            self.game.lamps.gi05.schedule(schedule=0x55555555, cycle_seconds=0, now=True)
            self.delay(name='gi_reactivate', event_type=None, delay=0.3, handler=self.game.gi_on)
            self.game.sound.play("wb_bang")
            self.game.lampController.save_state('base')
            self.game.lampController.play_show("ball_launch", 
                                               repeat=False,
                                               callback=self.game.update_lamps
                                               )

            
    def sw_shooterLane_active_for_500ms(self, sw):
        if self.ball_saved:
            self.game.coils.ballLaunch.pulse(50)
            self.ball_saved = False
            
    def sw_shooterLane_open_for_1s(self, sw):
        if self.ball_starting:
            self.ball_starting = False
            self.game.ball_save.start(num_balls_to_save=1, time=60, now=True, allow_multiple_saves=True)
            self.do_flash(True)
            
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

        
    def sw_centerRamp_active(self, sw):
        self.screen.turn_wizard(70)
        self.delay('turn_wizard', event_type=None, delay=3, handler=self.screen.turn_wizard, param=20)
        self.game.sound.play("wb_bang")
        print "HIT " + self.screen.get_cube_color(1,1) + " CUBE"
        self.screen.explode_cube(1)
        self.screen.remove_cube(1)
        self.delay('move_c_cubes', event_type=None, delay=1, handler=self.screen.move_cubes_down, param=1)
        
        self.delay('add_c_cube', event_type=None, delay=2, handler=self.screen.add_cube, param=1)
        
    
    def do_flash(self, rerun=False):
        self.game.sound.play_delayed("trunk_hit",4,0.8)
        self.delay('flash_section', event_type=None, delay=0.8, handler=self.flash_section, param=1)
        
        if rerun:
            self.delay('delayed_flash', event_type=None, delay=25, handler=self.do_flash, param=True)
    
    def flash_section(self, sect):
        print "FLASH SECTION " + str(sect)
        
        if sect == 1:
            self.game.coils.lowerReboundFlasher.schedule(schedule=0x0000aaaa, cycle_seconds=1, now=True)
            self.game.coils.rightRampFlasher.schedule(schedule=0x0000aaaa, cycle_seconds=1, now=True)
        if sect == 2:
            self.game.coils.divertorFlasher.schedule(schedule=0x0000aaaa, cycle_seconds=1, now=True)
            self.game.coils.jetsFlasher.schedule(schedule=0x0000aaaa, cycle_seconds=1, now=True)
        if sect == 3:
            self.game.coils.leftRampUpFlasher.schedule(schedule=0x0000aaaa, cycle_seconds=1, now=True)
            self.game.coils.leftRampLwrFlasher.schedule(schedule=0x0000aaaa, cycle_seconds=1, now=True)
        if sect == 4:
            self.game.coils.ejectFlasher.schedule(schedule=0x0000aaaa, cycle_seconds=1, now=True)
            self.game.coils.eyeBallFlasher.schedule(schedule=0x0000aaaa, cycle_seconds=1, now=True)
        
        if sect < 4:
            self.delay('flash_section', event_type=None, delay=0.8, handler=self.flash_section, param=sect + 1)
    
    def sw_leftLoop_active(self, sw):
        self.game.score(600)
            
    def sw_leftRampExit_active(self, sw):
        pass
        
    def sw_upperLeftFlipperGate_active(self, sw):
        self.screen.toggle_wi(False)
        self.delay('toggle_wi', event_type=None, delay=0.2, handler=self.toggle_wi_text, param=True)
        self.delay('stop_toggle_wi', event_type=None, delay=4, handler=self.stop_toggle_wi)
        self.game.sound.play("sparkle")
        
    def stop_toggle_wi(self):
        self.cancel_delayed('toggle_wi')
        self.screen.hide_wizard_text()
        
    def toggle_wi_text(self, toggle):
        new_toggle = not toggle
        self.screen.toggle_wi(new_toggle)
        
        self.delay('toggle_wi', event_type=None, delay=0.2, handler=self.toggle_wi_text, param=new_toggle)

    def sw_sideRampExit_active(self, sw):
        pass
    def sw_rightRampExit_active(self, sw):
        pass
        
    def sw_rightFreeway_active(self, sw):
        pass
        
    def sw_rightRampEnter_active(self, sw):
        if self.ignore_switches["right_ramp"]: return
        self.ignore_switch("right_ramp",3)
        self.game.coils.rightRampFlasher.schedule(schedule=0x0000dddd, cycle_seconds=1, now=True)

        self.game.lampController.play_show("bottom_to_top",
                                           repeat=False,
                                           callback=self.game.update_lamps
                                           )
        
        self.game.sound.play("wb_bang")
        print "HIT " + self.screen.get_cube_color(2,1) + " CUBE"
        self.screen.explode_cube(2)
        self.screen.remove_cube(2)
        self.delay('move_r_cubes', event_type=None, delay=1, handler=self.screen.move_cubes_down, param=2)
        
        self.delay('add_r_cube', event_type=None, delay=2, handler=self.screen.add_cube, param=2)
        
        
    def sw_leftRampEnter_active(self, sw):
        if self.ignore_switches["left_ramp"]: return
        self.ignore_switch("left_ramp")
        self.game.coils.leftRampLwrFlasher.schedule(schedule=0x0000dddd, cycle_seconds=1, now=True)
        self.game.lampController.play_show("bottom_to_top",
                                           repeat=False,
                                           callback=self.game.update_lamps
                                           )
        
        self.game.sound.play("wb_bang")
        print "HIT " + self.screen.get_cube_color(0,1) + " CUBE"
        self.screen.explode_cube(0)
        self.screen.remove_cube(0)
        self.delay('move_r_cubes', event_type=None, delay=1, handler=self.screen.move_cubes_down, param=0)
        
        self.delay('add_r_cube', event_type=None, delay=2, handler=self.screen.add_cube, param=0)
        
    def sw_enter_active(self, sw):
        self.game.modes.remove(self)
        self.game.modes.add(self.game.service)
        
    
        