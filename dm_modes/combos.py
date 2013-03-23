import procgame
import pinproc
import logging
from procgame import *
from dmmode import DMMode

class ComboLampState(object):
    OFF = 0
    FAST = 1
    SLOW = 2

class ComboMode(DMMode):
    COMBO_HOLD_TIME = 4 # 4 seconds to make each combo
    BLINK_SLOW = 0xf0f0f0f0
    BLINK_FAST = 0xbbbbbbbb
    
    COMBO_COMPUTER = [2,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200]
    COMBO_EXTRABALL = [15,45]
    
    LOCATION_SUBWAY = (0.3261,0,-0.4973)
    LOCATION_LEFTRAMP = (-0.27148,0,-0.875)
    LOCATION_TARGET = (-0.10351,0,-0.8723)
    LOCATION_CENTER = (0.0292,0,-0.3202)
    LOCATION_SIDERAMP = (0.5195,0,-0.3489)
    LOCATION_LEFTLOOP = (0.52539,0,-0.7812)
    LOCATION_FREEWAY = (0.8847,0,0.8347)
    LOCATION_RIGHTRAMP = (0.5039,0,-0.36197)
    
    def __init__(self, game):
        super(ComboMode, self).__init__(game, 10)
        self.logger = logging.getLogger("Combos")
        
        self.left_combos  = ComboLampState.OFF
        self.side_combos  = ComboLampState.OFF
        self.right_combos = ComboLampState.OFF
        
        self.can_blink_left_loop = True
        self.can_blink_left_ramp = True
        self.can_blink_center_ramp = True
        self.can_blink_side_scoop = True
        self.can_blink_side_ramp = True
        self.can_blink_right_ramp = True
        self.can_blink_right_loop = True
        
        
        
    def mode_started(self):
        self.logger.info("Starting combo mode...")
        self.cancel_all_delayed()
        #base.screenManager.showScreen("skillshot", False)
        #self.skillshot_screen = base.screenManager.getScreen("skillshot")
        
    def blink_right(self, rate):
        self.cancel_delayed("right_slow")
        self.cancel_delayed("right_fast")
        
        if rate == ComboLampState.OFF:
            if self.can_blink_right_loop: self.game.lamps.rightLoopArrow.disable()
            if self.can_blink_right_ramp: self.game.lamps.rightRampArrow.disable()
            if self.can_blink_center_ramp: self.game.lamps.centerRampArrow.disable()
        elif rate == ComboLampState.SLOW:
            if self.can_blink_right_loop: self.game.lamps.rightLoopArrow.schedule(schedule=self.BLINK_SLOW,cycle_seconds=0,now=True)
            if self.can_blink_right_ramp: self.game.lamps.rightRampArrow.schedule(schedule=self.BLINK_SLOW,cycle_seconds=0,now=True)
            if self.can_blink_center_ramp: self.game.lamps.centerRampArrow.schedule(schedule=self.BLINK_SLOW,cycle_seconds=0,now=True)
            
            self.delay(name="right_slow", event_type=None, delay=2, handler=self.blink_right, param=ComboLampState.FAST)
        elif rate == ComboLampState.FAST:
            if self.can_blink_right_loop: self.game.lamps.rightLoopArrow.schedule(schedule=self.BLINK_FAST,cycle_seconds=0,now=True)
            if self.can_blink_right_ramp: self.game.lamps.rightRampArrow.schedule(schedule=self.BLINK_FAST,cycle_seconds=0,now=True)
            if self.can_blink_center_ramp: self.game.lamps.centerRampArrow.schedule(schedule=self.BLINK_FAST,cycle_seconds=0,now=True)
            
            self.delay(name="right_fast", event_type=None, delay=2, handler=self.blink_right, param=ComboLampState.OFF)
            
        self.right_combos = rate
        
    def blink_side(self, rate):
        self.cancel_delayed("side_slow")
        self.cancel_delayed("side_fast")
        
        if rate == ComboLampState.OFF:
            if self.can_blink_side_scoop: self.game.lamps.undergroundArrow.disable()
            if self.can_blink_side_ramp: self.game.lamps.sideRampArrow.disable()
        elif rate == ComboLampState.SLOW:
            if self.can_blink_side_scoop: self.game.lamps.undergroundArrow.schedule(schedule=self.BLINK_SLOW, cycle_seconds=0, now=True)
            if self.can_blink_side_ramp: self.game.lamps.sideRampArrow.schedule(schedule=self.BLINK_SLOW, cycle_seconds=0, now = True)
            
            self.delay(name="side_slow", event_type=None, delay=2, handler=self.blink_side, param=ComboLampState.FAST)
            
        elif rate == ComboLampState.FAST:
            if self.can_blink_side_scoop: self.game.lamps.undergroundArrow.schedule(schedule=self.BLINK_FAST, cycle_seconds=0, now=True)
            if self.can_blink_side_ramp: self.game.lamps.sideRampArrow.schedule(schedule=self.BLINK_FAST, cycle_seconds=0, now = True)
            
            self.delay(name="side_fast", event_type=None, delay=2, handler=self.blink_side, param=ComboLampState.OFF)
            
        self.side_combos = rate
    
    def blink_left(self, rate):
        self.cancel_delayed("left_slow")
        self.cancel_delayed("left_fast")
        
        if rate == ComboLampState.OFF:
            if self.can_blink_left_loop: self.game.lamps.leftLoopArrow.disable()
            if self.can_blink_left_ramp: self.game.lamps.leftRampArrow.disable()
            if self.can_blink_center_ramp: self.game.lamps.centerRampArrow.disable()
        elif rate == ComboLampState.SLOW:
            if self.can_blink_left_loop: self.game.lamps.leftLoopArrow.schedule(schedule=self.BLINK_SLOW,cycle_seconds=0,now=True)
            if self.can_blink_left_ramp: self.game.lamps.leftRampArrow.schedule(schedule=self.BLINK_SLOW,cycle_seconds=0,now=True)
            if self.can_blink_center_ramp: self.game.lamps.centerRampArrow.schedule(schedule=self.BLINK_SLOW,cycle_seconds=0,now=True)
            
            self.delay(name="left_slow", event_type=None, delay=2, handler=self.blink_left, param=ComboLampState.FAST)
        elif rate == ComboLampState.FAST:
            if self.can_blink_left_loop: self.game.lamps.leftLoopArrow.schedule(schedule=self.BLINK_FAST,cycle_seconds=0,now=True)
            if self.can_blink_left_ramp: self.game.lamps.leftRampArrow.schedule(schedule=self.BLINK_FAST,cycle_seconds=0,now=True)
            if self.can_blink_left_ramp: self.game.lamps.centerRampArrow.schedule(schedule=self.BLINK_FAST,cycle_seconds=0,now=True)
            
            self.delay(name="left_fast", event_type=None, delay=2, handler=self.blink_left, param=ComboLampState.OFF)
            
        self.left_combos = rate
    
    def sw_rightFreeway_active(self, sw):
        # Score combo if active
        if self.right_combos != ComboLampState.OFF: self.add_combo(self.LOCATION_FREEWAY)
        self.blink_side(ComboLampState.SLOW)
        self.blink_right(ComboLampState.OFF)
        
    def sw_leftInlane_active(self, sw):
        self.blink_right(ComboLampState.SLOW)
        
    def sw_rightInlane_active(self, sw):
        self.blink_left(ComboLampState.SLOW)
        
    def sw_rightRampExit_active(self, sw):
        if self.right_combos != ComboLampState.OFF: self.add_combo(self.LOCATION_RIGHTRAMP)
        self.blink_right(ComboLampState.OFF)
        
    def sw_sideRampExit_active(self, sw):
        if self.side_combos != ComboLampState.OFF: self.add_combo(self.LOCATION_SIDERAMP)
        self.blink_side(ComboLampState.OFF)
        
    def sw_bottomPopper_active(self, sw):
        if self.side_combos != ComboLampState.OFF: self.add_combo(self.LOCATION_SUBWAY)
        self.blink_side(ComboLampState.OFF)
        
    def sw_centerRamp_active(self, sw):
        if self.right_combos != ComboLampState.OFF or self.left_combos != ComboLampState.OFF:
            self.add_combo(self.LOCATION_CENTER)
        self.blink_left(ComboLampState.OFF)
        self.blink_right(ComboLampState.OFF)
        self.blink_side(ComboLampState.SLOW)
        
    def sw_upperLeftFlipperGate_active(self, sw):
        if self.left_combos != ComboLampState.OFF: self.add_combo(self.LOCATION_LEFTLOOP)
        self.blink_left(ComboLampState.OFF)
        self.blink_right(ComboLampState.OFF)
        
    def sw_leftRampExit_active(self, sw):
        if self.left_combos != ComboLampState.OFF: self.add_combo(self.LOCATION_LEFTRAMP)
        self.blink_left(ComboLampState.OFF)
        self.blink_right(ComboLampState.OFF)
    
    def add_combo(self, position):
        self.game.current_player().player_stats['combos'] += 1
        self.logger.info("Combo added: " + str(self.game.current_player().player_stats['combos']))
        
        # Check if our current combo count calls for an award
        if self.game.current_player().player_stats['combos'] in self.COMBO_COMPUTER and not self.game.current_player().computer_lit:
            self.logger.info("Combo awards 'light computer'")
            base.screenManager.showModalMessage(
                                                message = "COMPUTER IS LIT!",
                                                time = 2.0,
                                                font = "motorwerk.ttf",
                                                scale = 0.2,
                                                bg=(0,0,0,1),
                                                blink_speed = 0.015,
                                                blink_color = (0,0,0,1),
                                                #l r t b
                                                frame_margin = (0.1,0.25,0,0)
                                                )
            
            self.game.current_player().computer_lit = True
            self.game.modes.add(self.game.computer)
            
            return
        
        if self.game.current_player().player_stats['combos'] in self.COMBO_EXTRABALL:
            self.logger.info("Combo awards 'light extra ball")
            base.screenManager.showModalMessage(
                                                message = "EXTRA BALL IS LIT!",
                                                time = 2.0,
                                                scale = 0.2,
                                                font = "motorwerk.ttf",
                                                bg=(0,0,0,1),
                                                fg=(1,1,1,1),
                                                frame_color=(0,0,1,1),
                                                blink_speed = 0.015,
                                                blink_color = (0,0,0,1)
                                                )
            self.game.current_player().extraball_lit = True
            self.game.lamps.extraBall.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            return
        
        base.screenManager.showModalMessage(
                                            message = str(self.game.current_player().player_stats['combos']) + "\nCOMBOS", 
                                            time = 1.5, 
                                            scale = 0.06, 
                                            bg=(0,0,0,1),
                                            animation='up',
                                            start_location=position,
                                            end_location=(position[0],position[1],position[2] + 0.5),
                                            blink_speed = 0.08,
                                            blink_color = (1,1,1,1))
        
        self.game.sound.play("flyby")
                                            
    
    