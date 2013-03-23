'''
Created on Dec 19, 2012

@author: compy
'''
import procgame
import pinproc
import logging
from procgame import *
from dmmode import DMMode

class AttractMode(DMMode):
    '''
    This is the game's attract mode that is running when the game is not in play.
    
    The mode is designed to handle credits and a player recognition system (pending)
    '''
    
    screen_rotation = [
                       ['attract4', 10.0],
                       ['attract1', 5.5],
                       ['attract2', 16.0],
                       ['attract3', 5.0],
                       ['attract4', 5.0]
                      ]
    current_screen_idx = len(screen_rotation) - 1
    
    def __init__(self, game):
        super(AttractMode, self).__init__(game, 3)
        self.logger = logging.getLogger("Attract")
        
    def mode_started(self):
        self.logger.info("Starting attract mode")
        self.cancel_all_delayed()
        #self.delay(name='mode_started', event_type=None, delay=5, handler=self.boot_finish)
        self.delay(name='stuck_balls', event_type=None, delay=2, handler=self.release_stuck_balls)
        base.screenManager.hideScreen("score")
        self.rotate_screens()
        self.game.gi_on()
        self.game.lampController.play_show("random", repeat=True)
    
    def mode_stopped(self):
        self.logger.info("Stopping attract mode")
        self.cancel_delayed('stuck_balls')
        self.cancel_delayed('rotate_attract_screens')
        self.game.lampController.stop_show()
        
    def rotate_screens(self):
        
        self.logger.info("Current screen idx %s" % str(self.current_screen_idx))
        if self.current_screen_idx >= len(self.screen_rotation) - 1:
            self.current_screen_idx = 0
        else:
            self.current_screen_idx += 1
        
        self.logger.info("Current screen idx post check %s" % str(self.current_screen_idx))
        
        current_screen_info = self.screen_rotation[self.current_screen_idx]
        screen_name = current_screen_info[0]
        delay_time = current_screen_info[1]
        #self.logger.info("Showing screen %s" % screen_name)
        base.screenManager.showScreen(screen_name)
        #self.logger.info("Showing screen %s for %s seconds", screen_name, str(delay_time))
        self.delay(name='rotate_attract_screens', event_type=None, delay=delay_time,handler=self.rotate_screens)
        
    def release_stuck_balls(self):
        if (self.game.switches.topPopper.is_active()):
            self.game.coils.topPopper.pulse(50)
        if (self.game.switches.eject.is_active()):
            self.game.coils.eject.pulse(20)
        if (self.game.switches.bottomPopper.is_active()):
            self.game.coils.bottomPopper.pulse(50)
        if (self.game.switches.shooterLane.is_active()):
            self.game.coils.ballLaunch.pulse(50)
        if (self.game.switches.elevatorHold.is_active()):
            self.game.claw.orient()
        self.delay(name='stuck_balls', event_type=None, delay=2, handler=self.release_stuck_balls)
    
    def sw_startButton_active(self, sw):
        if self.game.trough.is_full():
            self.logger.info("Trough is full, starting game")
            self.cancel_delayed('rotate_attract_screens')
            base.screenManager.hideScreen(self.screen_rotation[self.current_screen_idx][0])
            self.game.modes.remove(self)
            self.game.start_game()
            self.game.add_player()
            self.game.start_ball()
        else:
            base.screenManager.showModalMessage(message = "Pinball Missing...", time = 4, scale = 0.2)
            self.logger.info("Trough is not full. Performing ball search")
            self.game.ball_search.perform_search(5)
            
        return True
    
    def sw_coinDoor_closed(self, sw):
        base.screenManager.hideModalMessage('coin_door_open')
    
    def sw_coinDoor_open(self, sw):
        base.screenManager.showModalMessage(
                                            modal_name = "coin_door_open",
                                            message = "COIN DOOR OPEN\nPOWER DISABLED", 
                                            time = 0, 
                                            scale = 0.2, 
                                            blink_speed = 0.3,
                                            blink_color = (1,1,0,1),
                                            frame_blink_color = (0,0,0,1))
    
    def sw_enter_active(self, sw):
        self.game.modes.remove(self)
        self.game.modes.add(self.game.service)
        
    def outtro(self):
        self.game.disable_all_lamps()
        self.game.gi_off()
        self.game.lampController.play_show("gameend", repeat=True)
        self.game.sound.play_music("gameend")
        self.cancel_delayed('outtro_out')
        self.delay('outtro_out', event_type=None, delay=23, handler=self.end_outtro)
        
    def end_outtro(self):
        self.game.gi_on()
        self.game.lampController.play_show("random", repeat=True)