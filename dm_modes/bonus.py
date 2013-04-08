import procgame
import pinproc
import logging
from procgame import *
from functools import partial
from dmmode import DMMode

class BonusMode(DMMode):
    def __init__(self, game):
        super(BonusMode, self).__init__(game, 10)
        self.logger = logging.getLogger("Bonus")
        
        
    def mode_started(self):
        self.logger.info("Starting bonus mode...")
        #base.screenManager.showScreen("skillshot", False)
        #self.skillshot_screen = base.screenManager.getScreen("skillshot")
        self.game.dim_lower_pf()
        if not self.game.bonus_preemptive:
            self.game.sound.play_music("ball_end")
        else:
            self.game.bonus_preemptive = False
        self.delay(name='end_of_bonus', event_type=None, delay=2.0, handler=self.end_bonus)
        self.bonus_screen = base.screenManager.getScreen("bonus")
        base.display_queue.put_nowait(partial(self.calculate_bonus_items))
        
    def calculate_bonus_items(self):
        self.bonus_screen.clear_bonus_items()
        self.bonus_screen.add_bonus_item("Headshots", 15, True)
        self.bonus_screen.add_bonus_item("Ricochets", 24, True)
        self.bonus_screen.add_bonus_item("Explosions", self.game.current_player().explosions, True)
        if self.game.current_player().player_stats['combos'] > 0:
            self.bonus_screen.add_bonus_item("Combos", self.game.current_player().player_stats['combos'], True)
        
        if self.game.current_player().bonus_x > 1:
            self.bonus_screen.add_bonus_item("Multiplier", self.game.current_player().bonus_x, True)
            
        total = self.game.current_player().player_stats['combos'] * 250000
        total += self.game.current_player().explosions * 40000
        total = total * self.game.current_player().bonus_x
        
        self.total = total
        
        self.bonus_screen.add_bonus_item("Total", total, True)
        base.screenManager.showScreen("bonus", False)
        self.bonus_screen.start_animation()
        self.game.current_player().explosions = 0
    
    def mode_stopped(self):
        self.logger.info("Bonus mode complete")
        self.game.base_game_mode.end_ball()
        base.screenManager.hideScreen("bonus")
        
    def end_bonus(self):
        self.game.score(self.total)
        self.game.sound.play("bonus_total")
        self.delay(name='end_bonus', event_type=None, delay=1.5, handler=self.start_next_ball)
        
    def start_next_ball(self):
        
        # First check if its the last ball on the last player
        
        
        self.logger.info("Starting next ball")
        self.game.modes.remove(self)