import procgame
import pinproc
import logging
from procgame import *
from dmmode import DMMode

class ClawState(object):
    IDLE = 0
    ORIENTING = 1
    PICKING_BALL_UP = 2
    RETURNING_HOME = 3

class ClawMode(DMMode):
    
    def __init__(self, game):
        super(ClawMode, self).__init__(game, 9)
        self.logger = logging.getLogger("Claw")
        
        self.current_claw_state = ClawState.IDLE
        self.divertor_open = False
        
    def mode_started(self):
        self.logger.info("Starting claw mode...")
        self.current_claw_state = ClawState.IDLE
    
    def mode_stopped(self):
        self.logger.info("Claw mode complete")
        
    def cycle_ball(self):
        """
        Sends the claw to clawPos1, activates the elevator, picks the ball up, then drops the ball
        at the leftmost location
        """
        self.cycle_elevator()
        
    def orient(self):
        if self.current_claw_state != ClawState.IDLE: return
        self.current_claw_state = ClawState.ORIENTING
        
        # Run through a full cycle of elevator+claw+pickupball+dropball
        self.move_claw_alltheway_right()
        
    def move_claw_alltheway_right(self):
        if self.game.switches.clawPos1.is_active():
            self.pick_ball_up()
            return
        self.game.coils.clawRight.pulse(0)
        self.delay(name='claw_right', event_type=None, delay=4, handler=self._disable_claw_right)
        
    def _disable_claw_right(self):
        self.game.coils.clawRight.disable()
        
    def move_claw_alltheway_left(self):
        if self.game.switches.clawPos2.is_active():
            return
        self.game.coils.clawLeft.pulse(0)
        self.delay(name='claw_left', event_type=None, delay=4, handler=self._disable_claw_left)
        
    def _disable_claw_left(self):
        self.game.coils.clawLeft.disable()
        
    def stop(self):
        self.game.coils.clawLeft.disable()
        self.game.coils.clawRight.disable()
        self.cancel_delayed('claw_left')
        self.cancel_delayed('claw_right')
        
    def idle(self):
        self.current_claw_state = ClawState.IDLE
        
    def sw_clawPos2_open(self, sw):
        self.game.coils.clawLeft.disable()
        self.cancel_delayed('claw_left')
        
        if self.current_claw_state == ClawState.ORIENTING:
            self.current_claw_state = ClawState.IDLE
            self.drop_ball()
            
        if self.current_claw_state == ClawState.RETURNING_HOME:
            self.current_claw_state = ClawState.IDLE
            
    def sw_clawPos1_open(self, sw):
        self.game.coils.clawRight.disable()
        self.cancel_delayed('claw_right')
        
        self.pick_ball_up()
        
    def drop_ball(self):
        self.game.coils.clawMagnet.disable()
        
    def pick_ball_up(self):
        # enable claw magnet
        self.game.coils.clawMagnet.pulse(0)
        # move elevator up and back down to grab the ball
        self.cycle_elevator()
        
    def cycle_elevator(self):
        self.game.coils.elevatorMotor.pulse(0)
        self.delay(name='disable_elevator', event_type=None, delay=2, handler=self._disable_elevator)
        
    def _disable_elevator(self):
        self.game.coils.elevatorMotor.disable()
        
    def sw_elevatorHold_closed(self, sw):
        self.game.coils.elevatorMotor.disable()
        
        if self.current_claw_state == ClawState.ORIENTING:
            # If we're orienting, this is the phase where the elevator has just completed
            # a cycle, so move the claw all the way back to the left
            self.move_claw_alltheway_left()
        elif self.current_claw_state == ClawState.PICKING_BALL_UP:
            self.move_claw_alltheway_left()
            
    
    def open_divertor(self):
        self.divertor_open = True
        self.game.coils.divertorHold.pulse(0)
        self.game.coils.divertorMain.pulse(100)
        
    def close_divertor(self):
        self.divertor_open = False
        self.game.coils.divertorHold.disable()
        
    def gameplay_timeout(self):
        self.current_claw_state = ClawState.RETURNING_HOME
        self.drop_ball()
        self.delay(name='claw_return_home', event_type=None, delay=2, handler=self.move_claw_alltheway_left)
        
    def gameplay_pick_ball_up(self):
        if self.current_claw_state != ClawState.IDLE: return
        self.current_claw_state = ClawState.PICKING_BALL_UP
        self.move_claw_alltheway_right()
        
    