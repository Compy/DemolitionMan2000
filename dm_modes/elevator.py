import procgame
import pinproc
from procgame import *
from dmmode import DMMode

class Elevator(DMMode):
    def __init__(self, game):
        super(Elevator, self).__init__(game, 2)
    
    def mode_started(self):
        self.isClawMoving = False
        self.isOrienting = False
        self.isModeEnding = False
        
    def mode_stopped(self):
        # Is the game is still in progress, enable the flippers
        if self.game.isGameInProgress() == True:
            self.game.enable_dm_flippers()
    
    # Activate the coil until elevatorHold is closed
    def orient(self):
        self.isOrienting = True
        # Run through a full cycle of elevator+claw+pickupball+dropball
        self.move_claw_alltheway_right()
        self.delay(name='pickBallUp', event_type=None, delay=3, handler=self.pickBallUp)
        
    def cycle_elevator(self):
        self.isElevatorMoving = True
        self.game.coils.elevatorMotor.pulse(0)
        self.delay(name='elevCallback', event_type=None, delay=2, handler=self.elevatorTimeout)
        
    def elevatorTimeout(self):
        self.game.coils.elevatorMotor.disable()
        self.isElevatorMoving = False
        
    def mode_tick(self):
        pass
        
    def sw_elevatorHold_closed(self, sw):
        self.game.coils.elevatorMotor.disable()
        
    def sw_leftInlane_active(self, sw):
        if self.isModeEnding == False and self.game.isGameInProgress():
            self.game.open_divertor()
        
    def sw_elevatorHold_open_for_1s(self, aw):
        self.game.disable_dm_flippers()
    
        # Got ball in elevator
        self.game.close_divertor()
        # Move claw all the way over to the right
        self.move_claw_alltheway_right()
        
        # Wait about 3 seconds and pick the ball up
        self.delay(name='pickBallUp', event_type=None, delay=3, handler=self.pickBallUp)
        pass
        
    # Move claw until position 1 is open
    def move_claw_alltheway_left(self):
        if not self.game.switches.clawPos2.is_active():
            return
            
        self.game.coils.clawLeft.pulse(0)
        
    # Move claw until position 2 is open
    def move_claw_alltheway_right(self):
        if not self.game.switches.clawPos1.is_active():
            return
            
        self.game.coils.clawRight.pulse(0)
        
    def sw_enter_closed(self, sw):
        if not self.game.switches.clawPos2.is_active() or not self.game.isGameInProgress():
            return
        
        self.game.coils.clawLeft.pulse(0)
        
    def sw_enter_open(self, sw):
        self.game.coils.clawLeft.disable()
    
    def sw_rightHandle_closed(self, sw):
        if not self.game.switches.clawPos1.is_active() or not self.game.isGameInProgress():
            return
        
        self.game.coils.clawRight.pulse(0)
        
    def sw_ballLaunch_closed(self, sw):
        # Let the ball go
        self.dropBall()
        
    def sw_leftHandle_closed(self, sw):
        # Let the ball go
        self.dropBall()
        
    def sw_rightHandle_open(self, sw):
        self.game.coils.clawRight.disable()
        
    def sw_clawPos2_open(self, sw):
        self.game.coils.clawLeft.disable()
        self.game.coils.clawRight.pulse(50)
        
        if self.isOrienting == True:
            self.dropBall()
            self.isOrienting = False
            self.game.modes.remove(self)
        
    def sw_clawPos1_open(self, sw):
        self.game.coils.clawRight.disable()
        
    def sw_clawAcmag_closed(self, sw):
        # End the mode
        self.endMode()
    
    def sw_clawFreeze_closed(self, sw):
        # End the mode
        self.endMode()
        
    def sw_clawPrisonBreak_closed(self, sw):
        # End the mode
        self.endMode()
        
    def sw_clawSuperJets_closed(self, sw):
        # End the mode
        self.endMode()
        
    def sw_clawCaptureSimon_closed(self, sw):
        # End the mode
        self.endMode()
        
    def endMode(self):
        self.isModeEnding = True
        self.move_claw_alltheway_left()
        self.delay(name='endMode', event_type=None, delay=3, handler=self.doEndMode)
        
    def doEndMode(self):
        self.game.coils.clawLeft.disable()
        self.game.coils.clawRight.disable()
        self.game.coils.clawMagnet.disable()
        self.game.modes.remove(self)
        
    def moveBall(self):
        self.game.coils.clawLeft.pulse(0)
        if self.isOrienting == False:
            self.delay(name='stopClaw', event_type=None, delay=1, handler=self.game.coils.clawLeft.disable)
            self.delay(name='dropBall', event_type=None, delay=8, handler=self.dropBall)
        else:
            self.delay(name='stopClaw', event_type=None, delay=4, handler=self.game.coils.clawLeft.disable)
            self.delay(name='dropBall', event_type=None, delay=4, handler=self.dropBall)
        
    def pickBallUp(self):
        # Enable claw magnet
        self.game.coils.clawMagnet.pulse(0)
        # Move elevator up and back down to grab the ball
        self.cycle_elevator()
        self.delay(name='moveBall', event_type=None, delay=2, handler=self.moveBall)
        
    def dropBall(self):
        self.game.coils.clawMagnet.disable()
        if self.game.isGameInProgress() == True:
            self.game.enable_dm_flippers()