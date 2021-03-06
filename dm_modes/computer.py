import procgame
import pinproc
import logging
import random
from procgame import *
from dmmode import DMMode
from functools import partial

class ComputerMode(DMMode):
    """
    ('Extra Ball Lit', 'computer_light_eb'),
    ('3X Car Crash', 'computer_triple_car_crash'),
    ('3X Car Crash', 'computer_triple_car_crash'),
    ('3X Car Crash', 'computer_triple_car_crash'),
    ('2X Retina Scan', 'computer_double_retina_scan'),
    ('2X Retina Scan', 'computer_double_retina_scan'),
    ('2X Retina Scan', 'computer_double_retina_scan'),
    ('Light Arrows', 'computer_light_arrows'),
    ('Light Arrows', 'computer_light_arrows'),
    ('Light Arrows', 'computer_light_arrows'),
    ('Mystery Mode', None),
    ('Mystery Mode', None),
    ('Mystery Mode', None),
    ('Mystery Mode', None),
    ('Mystery Mode', None),
    ('Increase Bonus X', None),
    ('Increase Bonus X', None),
    ('Call For Backup', None),
    ('Call For Backup', None),
    ('Collect Standups', 'collect_standups'),
    ('Collect Standups', 'collect_standups'),
    ('Collect Standups', 'collect_standups'),
    ('Collect Standups', 'collect_standups'),
    ('250,000', None),
    ('500,000', None),
    ('1,000,000', None),
    """
    computer_awards = [
                        #('Extra Ball Lit', 'computer_light_eb'),
                        #('3X Car Crash', 'computer_triple_car_crash'),
                        #('3X Car Crash', 'computer_triple_car_crash'),
                        #('3X Car Crash', 'computer_triple_car_crash'),
                        #('2X Retina Scan', 'computer_double_retina_scan'),
                        #('2X Retina Scan', 'computer_double_retina_scan'),
                        #('2X Retina Scan', 'computer_double_retina_scan'),
                        #('Light Arrows', 'computer_light_arrows'),
                        #('Light Arrows', 'computer_light_arrows'),
                        #('Light Arrows', 'computer_light_arrows'),
                        #('Mystery Mode', None),
                        #('Mystery Mode', None),
                        #('Mystery Mode', None),
                        #('Mystery Mode', None),
                        #('Mystery Mode', None),
                        #('Mystery Mode', None),
                        #('Increase Bonus X', None),
                        #('Increase Bonus X', None),
                        #('Call For Backup', None),
                        #('Call For Backup', None),
                        #('Collect Standups', 'collect_standups'),
                        #('Collect Standups', 'collect_standups'),
                        #('250,000', None),
                        #('500,000', None),
                        #('1,000,000', None),
                        ('Simon Says',None),
                        ('Simon Says',None),
                        ('Simon Says',None),
                        ('Simon Says',None),
                        ('Simon Says',None),
                        ('Simon Says',None),
                        ('Simon Says',None)
                       ]
    def __init__(self, game):
        super(ComputerMode, self).__init__(game, 11)
        self.logger = logging.getLogger("Computer")
        self.award = ""
        
        
    def mode_started(self):
        self.logger.info("Starting computer mode...")
        self.cancel_all_delayed()
        self.game.lamps.computer.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
        self.computer_screen = base.screenManager.getScreen("computer")
        self.award_in_progress = False
    
    def mode_stopped(self):
        self.game.lamps.computer.disable()
        self.logger.info("Computer mode complete")
        base.screenManager.hideScreen("computer")
        self.award_in_progress = False
        
    def sw_bottomPopper_active_for_200ms(self, sw):
        # Computer award
        if self.game.simon_says.is_started(): return
        self.logger.info("Bottom Popper Active for 200ms, starting computer mode")
        self.start_award()
        return True
    
    def start_award(self):
        if self.award_in_progress: return
        base.screenManager.showScreen("computer", False)
        #self.game.sound.set_music_volume(0.2)
        self.game.sound.play("computer_award", fade_music=True)
        self.select_award()
        
        self.cancel_delayed('say_computer_award')
        self.delay(name='say_computer_award', event_type=None, delay=2.1, handler=self.announce_award)
        self.cancel_delayed('end_computer')
        self.delay(name='end_computer', event_type=None, delay=4, handler=self.end_computer)
        self.award_in_progress = True
    
    def select_award(self):
        random.shuffle(self.computer_awards)
        self.award = self.computer_awards[random.randrange(0,len(self.computer_awards) - 1)]
        if self.award[0] == "Light Arrows" and self.game.current_player().light_arrows:
            self.select_award()
            
        if self.award[0] == "Mystery Mode" and self.game.current_player().wtsa:
            self.select_award()
        
        if self.award[0] == "Extra Ball Lit" and self.game.current_player().extraball_lit:
            self.select_award()
        if self.award[0] == "Call For Backup" and self.game.current_player().call_for_backup:
            self.select_award()
        if self.award[0] == "Simon Says" and self.game.fortress.is_started():
            self.select_award()
    
    def announce_award(self):
        self.logger.info("announce_award::Computer awards " + self.award[0])
        if self.award[1] != None:
            self.game.sound.play(self.award[1], fade_music=True)
        
        if self.award[0] == "Light Arrows":
            self.game.current_player().light_arrows = True
            self.game.current_player().arrow_left_loop = True
            self.game.current_player().arrow_left_ramp = True
            self.game.current_player().arrow_acmag = True
            self.game.current_player().arrow_subway = True
            self.game.current_player().arrow_side_ramp = True
            self.game.current_player().arrow_right_ramp = True
            self.game.current_player().arrow_right_loop = True

            self.game.lamps.leftLoopArrow.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)   
            self.game.lamps.rightRampArrow.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            self.game.lamps.undergroundArrow.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            self.game.lamps.leftRampArrow.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            self.game.lamps.sideRampArrow.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            self.game.lamps.centerRampArrow.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            self.game.lamps.rightLoopArrow.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            
        if self.award[0] == "Mystery Mode":
            self.game.current_player().computer_lit = False
            self.game.current_player().wtsa = True
            self.game.modes.add(self.game.wtsa)
            self.game.modes.remove(self)
            
        if self.award[0] == "Collect Standups":
            self.cancel_delayed('end_computer')
            self.collect_standups(1)
        
        if self.award[0] == "3X Car Crash":
            self.delay('3x_car_crash', event_type=None, delay=1.5, handler=self.award_3x_car_crash)
        
        if self.award[0] == "250,000":
            self.game.score(250000)
            
        if self.award[0] == "500,000":
            self.game.score(500000)
            
        if self.award[0] == "1,000,000":
            self.game.score(1000000)
        
        if self.award[0] == "Extra Ball Lit":
            self.game.current_player().extraball_lit = True
            self.game.lamps.extraBall.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
            
        if self.award[0] == "Increase Bonus X":
            self.game.current_player().bonus_x += 1
            base.display_queue.put_nowait(partial(base.screenManager.getScreen("score").update_hud))
            
        if self.award[0] == "2X Retina Scan":
            self.game.score(1500000)
            self.game.sound.play("retina")
            
            self.game.base_game_mode.show_retina()
            self.delay('retina_show', event_type=None, delay=1, handler=self.show_retina_text)
            
        if self.award[0] == "Call For Backup":
            self.game.current_player().call_for_backup = True
            base.display_queue.put_nowait(partial(base.screenManager.getScreen("score").update_hud))
            
        if self.award[0] == "Simon Says":
            self.game.current_player().computer_lit = False
            self.game.modes.add(self.game.simon_says)
            self.game.modes.remove(self)
        
    def award_3x_car_crash(self):
        self.game.sound.play("tires")
        if self.game.current_player().car_crashes == 0:
            self.game.score(3000000 * 3)
            message = "9,000,000"
        elif self.game.current_player().car_crashes == 1:
            self.game.score(6000000 * 3)
            message = "18,000,000"
        elif self.game.current_player().car_crashes >= 2:
            self.game.score(10000000 * 3)
            message = "30,000,000"
            
        base.screenManager.showModalMessage(
                                            message=message, 
                                            modal_name="triple_car_crash", 
                                            fg=(1,1,1,1),
                                            frame_color=(0,0,0,0),
                                            blink_speed=0.25,
                                            blink_color=(0,0,0,0),
                                            bg=(0,0,0,1),
                                            scale=(0.2,0.2,0.2),
                                            time = 4)
        
    def show_retina_text(self):
        base.screenManager.showModalMessage(
                                            message="1,500,000", 
                                            modal_name="retina", 
                                            fg=(1,1,1,1),
                                            frame_color=(0,0,0,0),
                                            blink_speed=0.25,
                                            blink_color=(0,0,0,0),
                                            bg=(0,0,0,1),
                                            start_location=(-0.9,0,-0.5),
                                            scale=(0.1,0.1,0.1),
                                            time = 2)
            
    
    def collect_standups(self,num):
        if num <= 5:
            new_num = num + 1
            self.game.base_game_mode.spot_standup()
            self.game.update_lamps()
            self.delay('spot_standup', event_type=None, delay=0.8, handler=self.collect_standups, param=new_num)
        else:
            self.delay(name='end_computer', event_type=None, delay=1, handler=self.end_computer)
    
    def update_lamps(self):
        if self.game.current_player().computer_lit:
            self.game.lamps.computer.schedule(schedule=0x0f0f0f0f, cycle_seconds=0, now=True)
        else:
            self.game.lamps.computer.disable()
    
    def end_computer(self):
        #self.game.sound.set_music_volume(0.6)
        self.logger.info("Computer::end_computer called")
        self.game.current_player().computer_lit = False
        self.game.base_game_mode.release_bottomPopper()
        self.game.modes.remove(self)