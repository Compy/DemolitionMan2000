'''
Created on Dec 4, 2012

@author: compy
'''
import logging
import time
import sys
import os
import yaml
import traceback
import procgame
import threading

from procgame import *
from procgame.highscore import *
from procgame.modes import BallSave, Trough, BallSearch
from procgame.game import BasicPinboxGame
from dm_modes import elevator, boot, attract, blocks, skillshot, basemode, status, bonus, claw, combos, carcrash, sanangeles
from dm_modes import computer, acmag, match, carchase
from pinbox import service
from player import DMPlayer
import pinproc

curr_file_path = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(curr_file_path, os.path.pardir))
        
machine_config_path = parent_dir + "/config/dm.yaml"
settings_path = parent_dir + "/config/settings.yaml"
game_data_path = parent_dir + "/config/game_data.yaml"
game_data_template_path = parent_dir + "/config/game_data_template.yaml"
settings_template_path = parent_dir + "/config/settings_template.yaml"
lampshow_path = parent_dir + "/lampshows/"
        
class HWGame(BasicPinboxGame):
    def __init__(self, video):
        """
        Create a new HWGame instance that controls all hardware aspects of the Pinball 2000 (pinbox)
        experience.
        All calls related to video controls are marshaled back to self.video
        """
        
        # Check out our command line arguments to see what mode we should boot in
        self.fakePinProc = (len(sys.argv) > 1 and 'fakepinproc' in sys.argv)
        self.recording = (len(sys.argv) > 1 and 'record' in sys.argv)
        self.playback = (len(sys.argv) > 1 and 'playback' in sys.argv)
        self.SIMULATE = video.SIMULATE
        self.video = video
        
        if self.fakePinProc:
            if self.playback:
                config.values['pinproc_class'] = 'procgame.fakepinproc.FakePinPROCPlayback'
            else:
                config.values['pinproc_class'] = 'procgame.fakepinproc.FakePinPROC'
            self.fakePinProc = True
        else:
            self.fakePinProc = False
        
        if video.SIMULATE:
            config.values['pinproc_class'] = 'procgame.fakepinproc.FakePinPROC'
            self.fakePinProc = True
            
        # Initialize our parent class
        # Grabbing machine types from config files in game specific code is pointless, so we
        # statically specify it here to prevent errors.
        super(HWGame, self).__init__(pinproc.MachineTypeWPC)
        
        self.balls_per_game = 3
        
        # If we're in playback mode, force ourselves to use fakePinProc
        if self.playback:
            self.fakePinProc = True
        
        self.status_held_flipper = 'L'
        self.bonus_preemptive = False
        
        self.exit = False
        self.exit_code = 0
        
        # Run the setup function to actually begin the boot sequence
        self.setup()
        
        self.is_divertor_open = False
        
    def setup(self):
        """
        Sets up the entire game including registering sounds with our AV controller.
        We let Panda3D handle all the stereo aspects and sound queues.
        
        We will also load the initial mode stack here
        """
        
        logging.info("Beginning setup sequence")
        logging.info("Loading game configuration")
        self.load_config(machine_config_path)
        logging.info("Loading sound controller")
        self.sound = procgame.sound.PinboxSoundController(self)
        logging.info("Loading lamp controller")
        self.lampController = procgame.lamps.LampController(self)
        logging.info("Loading game settings file")
        self.load_settings(settings_template_path, settings_path)
        self.load_game_data(game_data_template_path, game_data_path)
        
        logging.info("Setting up ball search")
        self.setup_ball_search()
        
        logging.info("Setting up ball save")
        self.ball_save = BallSave(self, self.lamps.ballSave, 'shooterLane')
        
        logging.info("Setting up trough switches")
        # Set up trough switches
        trough_switchnames = []
        for i in range(1, 6):
            trough_switchnames.append('trough' + str(i))
        
        early_save_switchnames = ['leftOutlane', 'rightOutlane']
        logging.info("Setting up trough")
        self.trough = Trough(self, trough_switchnames, 'trough1', 'trough', early_save_switchnames, 'shooterLane', self.drain_callback)
        
        self.elevator = elevator.Elevator(self)
        self.boot = boot.BootMode(self)
        self.attract = attract.AttractMode(self)
        self.blocks = blocks.BlocksMode(self)
        self.skill_shot_mode = skillshot.SkillShotMode(self)
        self.combo_mode = combos.ComboMode(self)
        self.base_game_mode = basemode.BaseMode(self)
        self.bonus = bonus.BonusMode(self)
        self.status_display_mode = status.StatusDisplayMode(self)
        self.claw = claw.ClawMode(self)
        self.computer = computer.ComputerMode(self)
        self.acmag = acmag.AcmagMode(self)
        self.match = match.MatchMode(self)
        self.carcrash = carcrash.CarCrashMode(self)
        self.wtsa = sanangeles.SanAngelesMode(self)
        self.car_chase = carchase.CarChaseMode(self)
        ## SERVICE MODES AND SUBMODES ##
        self.service = service.ServiceMainMenu(self)
        self.service_diagnostics = service.ServiceDiagnosticsMenu(self)
        self.service_update_code = service.ServiceUpdateCode(self)
        self.service_3d = service.Service3D(self)
        self.service_flashers = service.ServiceFlashers(self)
        self.service_switches = service.ServiceSwitches(self)
        self.service_log = service.ServiceLog(self)
        
        # Link ball_save to trough
        self.trough.ball_save_callback = self.ball_save.launch_callback
        self.trough.num_balls_to_save = self.ball_save.get_num_balls_to_save
        self.ball_save.trough_enable_ball_save = self.trough.enable_ball_save
        
        self.highscore_categories = []
        cat = highscore.HighScoreCategory()
        cat.scores = [highscore.HighScore(score=500000000, inits='JWL'),
                      highscore.HighScore(score=450000000, inits='GSS'),
                      highscore.HighScore(score=400000000, inits='ASP'),
                      highscore.HighScore(score=350000000, inits='JFP'),
                      highscore.HighScore(score=300000000, inits='JAP')
                      ]
        cat.game_data_key = "ClassHighScoreData"
        self.highscore_categories.append(cat)
        
        for category in self.highscore_categories:
            category.load_from_game(self)
        
        logging.info("Trough ball count: %s" % str(self.trough.num_balls()))
        
        self.ballsearch_coils = ['leftSlingshot', 'rightSlingshot', 'leftJet', 'rightJet', 'bottomJet', 'eject', 'topPopper', 'bottomPopper']
        
        self.assets()
        self.reset()
        
    def assets(self):
        logging.info("Loading sound effects")
        ##
        ## SOUND EFFECTS (SFX)
        ##
        self.sound.register_sound("boot", "assets/sfx/boot.wav")
        self.sound.register_sound("bonus_award", "assets/sfx/bonusaward.wav")
        self.sound.register_sound("trunk_hit", "assets/sfx/trunkhit.wav")
        self.sound.register_sound("trunk_turn", "assets/sfx/trunkturn.wav")
        self.sound.register_sound("service_enter", "assets/sfx/service_enter.wav")
        self.sound.register_sound("service_exit", "assets/sfx/service_exit.wav")
        self.sound.register_sound("service_down", "assets/sfx/service_down.wav")
        self.sound.register_sound("service_up", "assets/sfx/service_up.wav")
        self.sound.register_sound("slingshot", "assets/sfx/slingshot.wav")
        self.sound.register_sound("jet", "assets/sfx/jet_1.wav")
        self.sound.register_sound("jet", "assets/sfx/jet_2.wav")
        self.sound.register_sound("jet", "assets/sfx/jet_3.wav")
        self.sound.register_sound("explode", "assets/sfx/explode_1.wav")
        self.sound.register_sound("explode", "assets/sfx/explode_2.wav")
        self.sound.register_sound("explode", "assets/sfx/explode_3.wav")
        self.sound.register_sound("player1", "assets/speech/comp_player1.wav")
        self.sound.register_sound("player2", "assets/speech/comp_player2.wav")
        self.sound.register_sound("player3", "assets/speech/comp_player3.wav")
        self.sound.register_sound("player4", "assets/speech/comp_player4.wav")
        self.sound.register_sound("computer_acmag", "assets/speech/computer_acmag.wav")
        self.sound.register_sound("woosh", "assets/sfx/woosh.wav")
        self.sound.register_sound("inlane", "assets/sfx/inlane.wav")
        self.sound.register_sound("flyby", "assets/sfx/flyby_1.wav")
        self.sound.register_sound("flyby", "assets/sfx/flyby_2.wav")
        self.sound.register_sound("drain", "assets/sfx/drain.wav")
        self.sound.register_sound("bonus_total", "assets/sfx/bonus_total.wav")
        self.sound.register_sound("gunshot", "assets/sfx/gunshot.wav")
        self.sound.register_sound("gunshots", "assets/sfx/multiple_gunshots.wav")
        self.sound.register_sound("computer_award", "assets/sfx/computer_award.wav")
        self.sound.register_sound("spinner", "assets/sfx/spinner.wav")
        self.sound.register_sound("acmag_hit", "assets/sfx/acmag_hit.wav")
        self.sound.register_sound("skillshot", "assets/sfx/skillshot.wav")
        self.sound.register_sound("vuk", "assets/sfx/vuk.wav")
        self.sound.register_sound("target_hit", "assets/sfx/target_hit.wav")
        self.sound.register_sound("freeze", "assets/sfx/freeze.wav")
        self.sound.register_sound("loop", "assets/sfx/loop.wav")
        self.sound.register_sound("ramp_up", "assets/sfx/ramp_up.wav")
        self.sound.register_sound("extraball", "assets/sfx/extraball_music.wav")
        self.sound.register_sound("mtl_whoosh", "assets/sfx/mtl_whoosh.wav")
        self.sound.register_sound("dontmove", "assets/speech/spartan_dontmove.wav")
        
        
        self.sound.register_sound("tires", "assets/sfx/tires.wav")
        self.sound.register_sound("crash", "assets/sfx/crash.wav")
        self.sound.register_sound("zap", "assets/sfx/zap.wav")
        self.sound.register_sound("engine", "assets/sfx/engine.wav")
        self.sound.register_sound("retina", "assets/sfx/retina_scan.wav")
        self.sound.register_sound("retina_eject", "assets/sfx/retina_eject.wav")
        
        # SPEECH
        self.sound.register_sound("boggle", "assets/speech/boggle.wav")
        self.sound.register_sound("cows", "assets/speech/huxley_cows.wav")
        self.sound.register_sound("leary_jello", "assets/speech/leary_jello.wav")
        self.sound.register_sound("seashells", "assets/speech/seashells.wav")
        self.sound.register_sound("verbal_fine", "assets/speech/verbal_fine.wav")
        
        self.sound.register_sound("computer_double_retina_scan", "assets/speech/computer_double_retina_scan.wav")
        self.sound.register_sound("computer_explode_activated", "assets/speech/computer_explode_activated.wav")
        self.sound.register_sound("computer_explode_hurryup", "assets/speech/computer_explode_hurryup.wav")
        self.sound.register_sound("computer_light_arrows", "assets/speech/computer_light_arrows.wav")
        self.sound.register_sound("computer_light_eb", "assets/speech/computer_light_eb.wav")
        self.sound.register_sound("computer_max_freezes", "assets/speech/computer_max_freezes.wav")
        self.sound.register_sound("computer_mb_activated", "assets/speech/computer_mb_activated.wav")
        self.sound.register_sound("computer_quick_freeze_activated", "assets/speech/computer_quick_freeze_activated.wav")
        self.sound.register_sound("computer_shoot_left_loop", "assets/speech/computer_shoot_left_loop.wav")
        self.sound.register_sound("computer_triple_car_crash", "assets/speech/computer_triple_car_crash.wav")
        self.sound.register_sound("praise", "assets/speech/spartan_greatshot.wav")
        self.sound.register_sound("praise", "assets/speech/spartan_amazing.wav")
        self.sound.register_sound("praise", "assets/speech/spartan_nice.wav")
        self.sound.register_sound("praise", "assets/speech/spartan_nicemove.wav")
        self.sound.register_sound("praise", "assets/speech/spartan_niceshooting.wav")
        self.sound.register_sound("praise", "assets/speech/spartan_niceshot.wav")
        self.sound.register_sound("praise", "assets/speech/spartan_verynice.wav")
        self.sound.register_sound("huxley_gotit", "assets/speech/huxley_gotit.wav")
        self.sound.register_sound("huxley_scream", "assets/speech/huxley_scream.wav")
        self.sound.register_sound("simon_lovely", "assets/speech/simon_lovely.wav")
        self.sound.register_sound("simon_right", "assets/speech/simon_right.wav")
        self.sound.register_sound("spartan_catchup", "assets/speech/spartan_catchup.wav")
        self.sound.register_sound("spartan_left", "assets/speech/spartan_left.wav")
        self.sound.register_sound("spartan_push_pedal", "assets/speech/spartan_push_pedal.wav")
        self.sound.register_sound("spartan_push", "assets/speech/spartan_push.wav")
        self.sound.register_sound("spartan_scream", "assets/speech/spartan_scream.wav")
        self.sound.register_sound("spartan_yeah", "assets/speech/spartan_yeah.wav")
        
        logging.info("Loading music")
        #self.sound.register_music("main", "assets/music/mainplay.wav")
        #self.sound.register_music("main", "assets/music/mainplay2.wav")
        #self.sound.register_music("main", "assets/music/mainplay3.wav")
        self.sound.register_music("main", "assets/music/mainplay4.wav")
        self.sound.register_music("hurryup", "assets/music/hurryup.wav")
        self.sound.register_music("acmag", "assets/music/acmag.wav")
        self.sound.register_music("capture_simon", "assets/music/capture_simon.wav")
        self.sound.register_music("ball_wait_start", "assets/music/ball_wait_start.wav")
        self.sound.register_music("ball_end", "assets/music/ball_end.wav")
        self.sound.register_music("drain", "assets/music/drain.wav")
        self.sound.register_music("gameend", "assets/music/game_end.wav")
        self.sound.register_music("match", "assets/music/match.wav")
        self.sound.register_music("wtsa", "assets/music/wtsa.wav")
        self.sound.register_music("chase", "assets/music/chase.ogg")
        
        ##
        ## MUSIC
        ##
        logging.info("Loading lampshows")
        ##
        ## LAMP SHOWS
        ##
        self.lampController.register_show("attract", lampshow_path + "attract.txt")
        self.lampController.register_show("bottom_to_top", lampshow_path + "bottom_to_top.lampshow")
        self.lampController.register_show("top_to_bottom", lampshow_path + "top_to_bottom.lampshow")
        self.lampController.register_show("random", lampshow_path + "random.txt")
        self.lampController.register_show("gameend", lampshow_path + "gameend.txt")
        self.lampController.register_show("acmag", lampshow_path + "acmag.txt")
        self.lampController.register_show("vuk", lampshow_path + "vuk.txt")
        self.lampController.register_show("ball_launch", lampshow_path + "ball_launch.txt")
        self.lampController.register_show("wtsa", lampshow_path + "wtsa.txt")
        
    def reset(self):
        logging.critical("GAME RESETTING")
        super(HWGame, self).reset()
        self.enable_flippers(False)
        self.modes.add(self.ball_search)
        self.modes.add(self.ball_save)
        self.modes.add(self.trough)
        self.modes.add(self.claw)
        self.modes.add(self.boot)
        self.save_game_data()
        
    def open_divertor(self):
        if self.is_divertor_open == False:
            logging.info("Opening claw divertor")
            self.coils['divertorMain'].pulse(30)
            self.coils['divertorHold'].pulse(0)
            self.is_divertor_open = True
            
    def close_divertor(self):
        logging.info("Closing claw divertor")
        self.coils['divertorHold'].disable()
        self.coils['divertorMain'].disable()
        self.is_divertor_open = False
        
    def ball_starting(self):
        logging.info("Ball starting")
        super(HWGame, self).ball_starting()
        self.modes.add(self.base_game_mode)
        self.modes.add(self.skill_shot_mode)
        self.modes.add(self.combo_mode)
        self.modes.add(self.carcrash)
        
        base.messenger.send("update_ball", [self.ball])
        
        p = self.current_player()
        base.messenger.send("update_score", [p.name, p.score])
        
        self.restore_player_feature_lamps()
        
        if len(self.players) > 1:
            self.sound.play("player" + str(self.current_player_index + 1))
        elif len(self.players) == 1 and self.ball == 1:
            self.sound.play("player1")
        
    def restore_player_feature_lamps(self):
        logging.info("Restoring feature lamps")
        
        self.disable_all_lamps()
        p = self.current_player()
        if p.computer_lit:
            self.modes.add(self.computer)
        if p.claw_lit:
            self.open_divertor()
            self.lamps.clawReady.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
        if p.access_claw_lit:
            self.lamps.accessClaw.pulse(0)
            
        if p.extraball_lit:
            self.lamps.extraBall.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            
        if p.multiball_lit:
            self.lamps.startMultiball.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            
        if p.retina_scan_ready:
            self.lamps.retinaScan.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            
        if p.mlit:
            self.lamps.middleRollOver.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
        if p.tlit:
            self.lamps.topRollOver.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
        if p.llit:
            self.lamps.lowerRollOver.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
        
        
        if p.arrow_loop:
            self.lamps.leftLoopArrow.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)   
        if p.arrow_right_ramp:
            self.lamps.rightRampArrow.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
        if p.arrow_subway:
            self.lamps.undergroundArrow.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
        if p.arrow_left_ramp:
            self.lamps.leftRampArrow.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
        if p.arrow_side_ramp:
            self.lamps.sideRampArrow.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
        if p.arrow_acmag:
            self.lamps.centerRampArrow.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
        if p.arrow_right_loop:
            self.lamps.rightLoopArrow.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
        
    def disable_all_lamps(self):
        for lamp in self.lamps:
            lamp.disable()
        
    def gi_on(self):
        self.lamps.gi01.pulse(0)  # not used
        self.lamps.gi02.pulse(0)  # upper right
        self.lamps.gi03.pulse(0)  # upper left
        self.lamps.gi04.pulse(0)  # lower right
        self.lamps.gi05.pulse(0)  # lower left
        
    def gi_off(self):
        self.lamps.gi01.disable()
        self.lamps.gi02.disable()
        self.lamps.gi03.disable()
        self.lamps.gi04.disable()
        self.lamps.gi05.disable()
        
    def dim_lower_pf(self):
        logging.info("Dimming lower playfield")
        self.gi_off()
        self.lamps.gi04.schedule(schedule=0xaaaaaaaa, cycle_seconds=0, now=True)  # lower right
        self.lamps.gi05.schedule(schedule=0xaaaaaaaa, cycle_seconds=0, now=True)  # lower left
        
    def ball_ended(self):
        logging.info("Ball ended")
        self.modes.remove(self.base_game_mode)
        self.modes.remove(self.combo_mode)
        self.modes.remove(self.acmag)
        self.modes.remove(self.carcrash)
        if self.current_player().computer_lit:
            self.modes.remove(self.computer)
        if self.current_player().sanangeles_in_progress:
            self.modes.remove(self.wtsa)
        
        super(HWGame, self).ball_ended()
        
    def game_ended(self):
        logging.info("Game ended")
        super(HWGame, self).game_ended()
        
        scores = []
        for p in self.players:
            scores.append(p.score)
            
        self.game_data['PreviousScores'] = scores
        self.save_game_data()
        
        self.modes.add(self.match)
        
    def setup_ball_search(self):
        special_handler_modes = []
        self.ball_search = BallSearch(self, priority=100, \
            countdown_time=10, coils=self.ballsearch_coils, \
            reset_switches=self.ballsearch_resetSwitches, \
            stop_switches=self.ballsearch_stopSwitches, \
            special_handler_modes=special_handler_modes)
        self.ball_search.disable()
        
    def invert_flippers(self, enable):
        """Enables or disables the flippers AND bumpers."""
        for flipper in self.config['PRFlippers']:
            self.logger.info("Programming flipper %s", flipper)
            main_coil = self.coils[flipper+'Main'] 
            hold_coil = self.coils[flipper+'Hold']
            switch_num = self.switches[flipper].number
            
            if flipper == 'flipperLwL':
                upper_main_coil = self.coils['flipperUpLMain'] 
                upper_hold_coil = self.coils['flipperUpLHold']

            drivers = []
            if enable:
                drivers += [pinproc.driver_state_pulse(main_coil.state(), main_coil.default_pulse_time)]
                drivers += [pinproc.driver_state_pulse(hold_coil.state(), 0)]
                if flipper == 'flipperLwL':
                    drivers += [pinproc.driver_state_pulse(upper_main_coil.state(), upper_main_coil.default_pulse_time)]
                    drivers += [pinproc.driver_state_pulse(upper_hold_coil.state(), 0)]

            self.proc.switch_update_rule(switch_num, 'open_nondebounced', {'notifyHost':False, 'reloadActive':False}, drivers, len(drivers) > 0)
            if flipper == 'flipperLwL':
                self.proc.switch_update_rule(self.switches['leftHandle'].number, 'open_nondebounced', {'notifyHost':False, 'reloadActive':False}, drivers, len(drivers) > 0)
            elif flipper == 'flipperLwR':
                self.proc.switch_update_rule(self.switches['rightHandle'].number, 'open_nondebounced', {'notifyHost':False, 'reloadActive':False}, drivers, len(drivers) > 0)
            
            drivers = []
            if enable:
                drivers += [pinproc.driver_state_disable(main_coil.state())]
                drivers += [pinproc.driver_state_disable(hold_coil.state())]
                if flipper == 'flipperLwL':
                    drivers += [pinproc.driver_state_disable(upper_main_coil.state())]
                    drivers += [pinproc.driver_state_disable(upper_hold_coil.state())]
                
    
            self.proc.switch_update_rule(switch_num, 'closed_nondebounced', {'notifyHost':False, 'reloadActive':False}, drivers, len(drivers) > 0)
            if flipper == 'flipperLwL':
                self.proc.switch_update_rule(self.switches['leftHandle'].number, 'closed_nondebounced', {'notifyHost':False, 'reloadActive':False}, drivers, len(drivers) > 0)
            elif flipper == 'flipperLwR':
                self.proc.switch_update_rule(self.switches['rightHandle'].number, 'closed_nondebounced', {'notifyHost':False, 'reloadActive':False}, drivers, len(drivers) > 0)
            
            if not enable:
                main_coil.disable()
                hold_coil.disable()
                if flipper == 'flipperLwL':
                    upper_main_coil.disable()
                    upper_hold_coil.disable()

        self.enable_bumpers(enable)
        
    def enable_flippers(self, enable):
        """Enables or disables the flippers AND bumpers."""
        for flipper in self.config['PRFlippers']:
            self.logger.info("Programming flipper %s", flipper)
            main_coil = self.coils[flipper+'Main'] 
            hold_coil = self.coils[flipper+'Hold']
            switch_num = self.switches[flipper].number
            
            if flipper == 'flipperLwL':
                upper_main_coil = self.coils['flipperUpLMain'] 
                upper_hold_coil = self.coils['flipperUpLHold']

            drivers = []
            if enable:
                drivers += [pinproc.driver_state_pulse(main_coil.state(), main_coil.default_pulse_time)]
                drivers += [pinproc.driver_state_pulse(hold_coil.state(), 0)]
                if flipper == 'flipperLwL':
                    drivers += [pinproc.driver_state_pulse(upper_main_coil.state(), upper_main_coil.default_pulse_time)]
                    drivers += [pinproc.driver_state_pulse(upper_hold_coil.state(), 0)]

            self.proc.switch_update_rule(switch_num, 'closed_nondebounced', {'notifyHost':False, 'reloadActive':False}, drivers, len(drivers) > 0)
            if flipper == 'flipperLwL':
                self.proc.switch_update_rule(self.switches['leftHandle'].number, 'closed_nondebounced', {'notifyHost':False, 'reloadActive':False}, drivers, len(drivers) > 0)
            elif flipper == 'flipperLwR':
                self.proc.switch_update_rule(self.switches['rightHandle'].number, 'closed_nondebounced', {'notifyHost':False, 'reloadActive':False}, drivers, len(drivers) > 0)
            
            drivers = []
            if enable:
                drivers += [pinproc.driver_state_disable(main_coil.state())]
                drivers += [pinproc.driver_state_disable(hold_coil.state())]
                if flipper == 'flipperLwL':
                    drivers += [pinproc.driver_state_disable(upper_main_coil.state())]
                    drivers += [pinproc.driver_state_disable(upper_hold_coil.state())]
                
    
            self.proc.switch_update_rule(switch_num, 'open_nondebounced', {'notifyHost':False, 'reloadActive':False}, drivers, len(drivers) > 0)
            if flipper == 'flipperLwL':
                self.proc.switch_update_rule(self.switches['leftHandle'].number, 'open_nondebounced', {'notifyHost':False, 'reloadActive':False}, drivers, len(drivers) > 0)
            elif flipper == 'flipperLwR':
                self.proc.switch_update_rule(self.switches['rightHandle'].number, 'open_nondebounced', {'notifyHost':False, 'reloadActive':False}, drivers, len(drivers) > 0)
            
            if not enable:
                main_coil.disable()
                hold_coil.disable()
                if flipper == 'flipperLwL':
                    upper_main_coil.disable()
                    upper_hold_coil.disable()

        self.enable_bumpers(enable)
        
    def dmd_event(self):
        pass
    
    def save_game_data(self):
        super(HWGame, self).save_game_data(game_data_path)
    
    def add_player(self):
        """Adds a new player to :attr:`players` and assigns it an appropriate name."""
        if len(self.players) < 4:
            player = self.create_player('Player %d' % (len(self.players) + 1))
            self.players += [player]
            return player
        return False
    
    def create_player(self, name):
        """Instantiates and returns a new instance of the :class:`Player` class with the
        name *name*.
        This method is called by :meth:`add_player`.
        This can be used to supply a custom subclass of :class:`Player`.
        """
        return DMPlayer(name)
    
    def drain_callback(self):
        pass
    
    def shoot_again(self):
        base.screenManager.showModalMessage(
            message = self.current_player().name + " SHOOTS AGAIN",
            time = 2.0,
            font = "motorwerk.ttf",
            scale = 0.15,
            bg=(0,0,0,1),
            blink_speed = 0.015,
            blink_color = (0,0,0,1),
            #l r t b
            frame_margin = (0.1,0.25,0,0)
            )
        super(HWGame, self).shoot_again()