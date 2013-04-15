import procgame
import pinproc
import logging
from procgame import *
from dmmode import DMMode
from combos import ComboMode
from functools import partial

class ClawState(object):
    IDLE = 0
    ORIENTING = 1
    PICKING_BALL_UP = 2
    RETURNING_HOME = 3

class ClawMode(DMMode):
    
    def __init__(self, game):
        super(ClawMode, self).__init__(game, 9)
        self.logger = logging.getLogger("Claw")
        
        self.set_state(ClawState.IDLE)
        self.divertor_open = False
        self.control_enabled = False
        self.do_enable_control = False
        
        self.screen = base.screenManager.getScreen("claw")
        
    def mode_started(self):
        self.logger.info("Starting claw mode...")
        self.set_state(ClawState.IDLE)
        self.control_enabled = False
        self.do_enable_control = False
    
    def mode_stopped(self):
        self.logger.info("Claw mode complete")
        self.stop()
        self.drop_ball()
        self.set_state(ClawState.IDLE)
        self.control_enabled = False
        self.do_enable_control = False
        
    def sw_clawCaptureSimon_active(self, sw):
        if self.game.base_game_mode.is_started():
            self.game.enable_flippers(True)
            
        self.delay('end_claw', event_type=None, delay=3, handler=self.return_home)
        self.control_enabled = False
        self.game.play_music()
        self.game.gi_on()
        self.claw_lights_off(sw.name)
        base.screenManager.hideScreen("claw")
        self.process_award(4)
            
    def sw_clawSuperJets_active(self, sw):
        if self.game.base_game_mode.is_started():
            self.game.enable_flippers(True)
            
        self.delay('end_claw', event_type=None, delay=3, handler=self.return_home)
        self.control_enabled = False
        self.game.play_music()
        self.game.gi_on()
        self.claw_lights_off(sw.name)
        base.screenManager.hideScreen("claw")
        self.process_award(3)
                    
    def sw_clawPrisonBreak_active(self, sw):
        if self.game.base_game_mode.is_started():
            self.game.enable_flippers(True)
            
        self.delay('end_claw', event_type=None, delay=3, handler=self.return_home)
        self.control_enabled = False
        self.game.play_music()
        self.game.gi_on()
        self.claw_lights_off(sw.name)
        base.screenManager.hideScreen("claw")
        self.process_award(2)
            
    def sw_clawFreeze_active(self, sw):
        if self.game.base_game_mode.is_started():
            self.game.enable_flippers(True)
            
        self.delay('end_claw', event_type=None, delay=3, handler=self.return_home)
        self.control_enabled = False
        self.game.play_music()
        self.game.gi_on()
        self.claw_lights_off(sw.name)
        base.screenManager.hideScreen("claw")
        self.process_award(1)
            
    def sw_clawAcmag_active(self, sw):
        if self.game.base_game_mode.is_started():
            self.game.enable_flippers(True)
            
        self.delay('end_claw', event_type=None, delay=3, handler=self.return_home)
        self.control_enabled = False
        self.game.play_music()
        self.game.gi_on()
        self.claw_lights_off(sw.name)
        base.screenManager.hideScreen("claw")
        self.process_award(0)
        
    def claw_lights_on(self):
        self.game.lamps.clawCaptureSimon.pulse(0)
        self.game.lamps.clawSuperJets.pulse(0)
        self.game.lamps.clawPrisonBreak.pulse(0)
        self.game.lamps.clawFreeze.pulse(0)
        self.game.lamps.clawAcmag.pulse(0)
        
    def claw_lights_off(self, except_lamp="clawAcmag"):
        self.game.lamps.clawCaptureSimon.disable()
        self.game.lamps.clawSuperJets.disable()
        self.game.lamps.clawPrisonBreak.disable()
        self.game.lamps.clawFreeze.disable()
        self.game.lamps.clawAcmag.disable()
        
        self.game.lamps[except_lamp].schedule(schedule=0x55555555, cycle_seconds=2, now=True)
        
    def process_award(self, award = 0):
        rewards = self.screen.get_slots()
        if len(rewards) < 1: return
        
        reward = rewards[award]
        
        if reward == "5 combos":
            self.add_combo_award(1)
        if reward == "10 million":
            self.game.score(10000000)
        if reward == "extra ball":
            self.game.current_player().extra_balls += 1
            self.delay('eb_delay',event_type=None,delay=3,handler=self.post_extraball_release)
            base.screenManager.hideScreen("score")
            base.screenManager.showScreen("extraball")
            return
        if reward == "lock":
            pass
        if reward == "car chase":
            pass
        if reward == "bonus x":
            self.game.current_player().bonus_x += 1
            base.display_queue.put_nowait(partial(base.screenManager.getScreen("score").update_hud))
        if reward == "superjets":
            self.game.sound.play("computer_superjets_activated",fade_music=True)
            self.game.current_player().super_jets = True
            self.game.current_player().super_jets_left = 25
        if reward == "add explode":
            pass
        if reward == "cfb":
            self.game.current_player().call_for_backup = True
            base.display_queue.put_nowait(partial(base.screenManager.getScreen("score").update_hud))
        if reward == "tz":
            pass
        
        base.screenManager.showScreen("score")
        
    def post_extraball_release(self):
        base.screenManager.hideScreen("extraball")
        base.screenManager.showScreen("score")
        
    def add_combo_award(self, num = 1):
        self.game.combo_mode.add_combo(ComboMode.LOCATION_RIGHTRAMP)
        if num < 5:
            self.delay('add_combo', event_type=None, delay=0.5, handler=self.add_combo_award, param=num + 1)
        
    def sw_eject_active(self, sw):
        if self.current_claw_state != ClawState.IDLE:
            self.sw_clawFreeze_active(sw)
            
    def sw_upperLeftFlipperGate_active(self, sw):
        if self.current_claw_state != ClawState.IDLE:
            self.sw_clawPrisonBreak_active(sw)
            
    def sw_leftJet_active(self, sw):
        if self.current_claw_state != ClawState.IDLE:
            self.sw_clawSuperJets_active(sw)
    
    def sw_rightJet_active(self, sw):
        if self.current_claw_state != ClawState.IDLE:
            self.sw_clawSuperJets_active(sw)
            
    def sw_bottomJet_active(self, sw):
        if self.current_claw_state != ClawState.IDLE:
            self.sw_clawSuperJets_active(sw)
            
    def sw_leftInlane_active(self, sw):
        if self.current_claw_state != ClawState.IDLE:
            self.sw_clawAcmag_active(sw)
        
    def cycle_ball(self):
        """
        Sends the claw to clawPos1, activates the elevator, picks the ball up, then drops the ball
        at the leftmost location
        """
        self.cycle_elevator()
        
    def return_home(self):
        self.set_state(ClawState.RETURNING_HOME)
        self.move_claw_alltheway_left()
        
    def orient(self):
        if self.current_claw_state != ClawState.IDLE: return
        self.set_state(ClawState.ORIENTING)
        
        # Run through a full cycle of elevator+claw+pickupball+dropball
        self.move_claw_alltheway_right()
        
    def move_claw_alltheway_right(self):
        if self.game.switches.clawPos1.is_active():
            if self.current_claw_state == ClawState.PICKING_BALL_UP:
                self.pick_ball_up()
            return
        self.game.coils.clawRight.pulse(0)
        self.delay(name='claw_right', event_type=None, delay=4, handler=self._disable_claw_right)
        
    def _disable_claw_right(self):
        self.game.coils.clawRight.disable()
        
    def move_claw_alltheway_left(self):
        if self.game.switches.clawPos2.is_active():
            self.sw_clawPos2_open(None)
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
        self.set_state(ClawState.IDLE)
        
    def sw_clawPos2_open(self, sw):
        self.game.coils.clawLeft.disable()
        self.cancel_delayed('claw_left')
        
        self.logger.info("Left claw opto activated...")
        
        if self.current_claw_state == ClawState.ORIENTING:
            self.logger.info("Claw was ORIENTING, setting IDLE and dropping ball")
            self.set_state(ClawState.IDLE)
            self.drop_ball()
            
        if self.current_claw_state == ClawState.RETURNING_HOME:
            self.logger.info("Claw was RETURNING_HOME, setting IDLE and wrapping up")
            self.set_state(ClawState.IDLE)
            self.mode_stopped()
            
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
            self.return_home()
        elif self.current_claw_state == ClawState.PICKING_BALL_UP:
            if self.do_enable_control:
                self.do_enable_control = False
                self.control_enabled = True
            self.move_claw_alltheway_left()
            self.delay('gameplay_timeout', event_type=None, delay=10, handler=self.gameplay_timeout)
            
    def sw_elevatorHold_open_for_500ms(self, sw):
        # Only do something (start the mode) if the claw state is currently idle or
        # the attract mode is active
        if not self.current_claw_state == ClawState.IDLE or self.game.attract.is_started():
            self.logger.info("Ball present at claw, but ClawState is not IDLE, it is " + str(self.current_claw_state) +". Ignoring")
            return
        
        if self.game.car_chase.is_started():
            self.logger.info("Ball present at claw, but Car Chase mode is active. Ignoring")
            return
        
        self.game.enable_flippers(False)
        self.close_divertor()
        self.gameplay_pick_ball_up()
        
        # If car chase is NOT active AND our base game mode is active, then we've got a ball
        # that we want to lend control to at the claw.
        if not self.game.car_chase.is_started() and self.game.base_game_mode.is_started():
            self.game.current_player().claw_lit = False
            self.game.lamps.clawReady.disable()
            self.play_instructions(1)
            self.game.gi_off()
            self.do_enable_control = True
            self.control_enabled = False
            self.game.sound.play_music("claw",-1)
            self.claw_lights_on()
            base.screenManager.showScreen("claw")
            
            self.delay('instruction', event_type=None, delay=7, handler=self.play_instructions, param=2)
            
    
    def play_instructions(self, instruction):
        if instruction == 1:
            self.game.sound.play("triggers_move_claw", fade_music=True)
        else:
            self.game.sound.play("buttons_release_ball", fade_music=True)
    
    def open_divertor(self):
        self.divertor_open = True
        self.game.coils.divertorHold.pulse(0)
        self.game.coils.divertorMain.pulse(100)
        
    def close_divertor(self):
        self.divertor_open = False
        self.game.coils.divertorHold.disable()
        
    def gameplay_timeout(self):
        self.stop()
        self.drop_ball()
        self.return_home()
        self.game.gi_on()
        base.screenManager.hideScreen("claw")
        self.claw_lights_off()
        
    def gameplay_pick_ball_up(self):
        if self.current_claw_state != ClawState.IDLE: return
        self.set_state(ClawState.PICKING_BALL_UP)
        self.move_claw_alltheway_right()
        
    
    def sw_flipperLwR_active(self, sw):
        if not self.game.base_game_mode.is_started() or not self.control_enabled: return
        self.move_claw_alltheway_right()
    
    def sw_flipperLwR_inactive(self, sw):
        if not self.game.base_game_mode.is_started() or not self.control_enabled: return
        self.stop()
        
    def sw_flipperLwL_active(self, sw):
        if not self.game.base_game_mode.is_started() or not self.control_enabled: return
        self.move_claw_alltheway_left()
        
    def sw_flipperLwL_inactive(self, sw):
        if not self.game.base_game_mode.is_started() or not self.control_enabled: return
        self.stop()
        
    def sw_leftHandle_active(self, sw):
        if not self.game.base_game_mode.is_started() or not self.control_enabled: return
        self.move_claw_alltheway_left()
        
    def sw_leftHandle_inactive(self, sw):
        if not self.game.base_game_mode.is_started() or not self.control_enabled: return
        self.stop()
        
    def sw_rightHandle_active(self, sw):
        if not self.game.base_game_mode.is_started() or not self.control_enabled: return
        self.move_claw_alltheway_right()
        
    def sw_rightHandle_inactive(self, sw):
        if not self.game.base_game_mode.is_started() or not self.control_enabled: return
        self.stop()
        
    def sw_enter_active(self, sw):
        if not self.game.base_game_mode.is_started() or not self.control_enabled: return
        self.stop()
        self.drop_ball()
        
    def sw_ballLaunch_active(self, sw):
        if not self.game.base_game_mode.is_started() or not self.control_enabled: return
        self.stop()
        self.drop_ball()
        
    def set_state(self, state):
        str_state = "IDLE"
        if state == 0:
            str_state = "IDLE"
        elif state == 1:
            str_state = "ORIENTING"
        elif state == 2:
            str_state = "PICKING_BALL_UP"
        elif state == 3:
            str_state = "RETURNING_HOME"
        self.current_claw_state = state
        
        self.logger.info("Setting claw state " + str_state)
        
        