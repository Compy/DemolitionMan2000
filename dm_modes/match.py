import procgame
import pinproc
import logging
from procgame import *
from functools import partial
from dmmode import DMMode

class MatchMode(DMMode):
    def __init__(self, game):
        super(MatchMode, self).__init__(game, 10)
        self.logger = logging.getLogger("Match")
        self.drop_idx = 0
        
    def mode_started(self):
        self.logger.info("Starting match mode...")
        #base.screenManager.showScreen("skillshot", False)
        #self.skillshot_screen = base.screenManager.getScreen("skillshot")
        #self.bonus_screen = base.screenManager.getScreen("bonus")
        #base.display_queue.put_nowait(partial(self.calculate_bonus_items))
        self.screen = base.screenManager.getScreen("match")
        
        self.drop_idx = 0
        
        digits = []
        for p in self.game.players:
            digits.append(str(p.score)[-2:-1] + "0")
            
        base.display_queue.put_nowait(partial(self.screen.set_digits, digits))
        
        print digits
        
        base.screenManager.showScreen("match", hideOthers=True, hideScore=True)
        
        self.delay(name='match_start', event_type=None, delay=0.7, handler=self.start_match)
        
        self.drop()
        
        self.delay(name='match_finish', event_type=None, delay=6, handler=self.end_match)
        
    def start_match(self):
        self.game.sound.play_music("match",loops=1)
        
    def drop(self):
        self.drop_idx += 1
        
        base.display_queue.put_nowait(partial(self.screen.drop))
        
        if self.drop_idx < 6:
            self.delay('match_drop', event_type=None, delay=0.456, handler=self.drop)
        else:
            self.delay('match_explode', event_type=None, delay=0.65, handler=self.screen.explode)
    
    def explode(self):
        base.display_queue.put_nowait(partial(self.screen.explode))
        
    def end_match(self):
        self.game.modes.remove(self)
    
    def mode_stopped(self):
        self.logger.info("Match mode complete")
        #base.screenManager.hideScreen("bonus")
        
        self.game.modes.remove(self.game.base_game_mode)
        self.game.modes.remove(self.game.combo_mode)
        self.game.modes.add(self.game.attract)
        self.game.attract.outtro()
        # We might also add a match here
        self.game.close_divertor()
        self.game.game_in_progress = False
        