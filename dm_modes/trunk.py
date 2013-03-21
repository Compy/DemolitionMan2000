import procgame
import pinproc
import logging
from procgame import *
from dmmode import DMMode

class TrunkMode(DMMode):
    def __init__(self, game):
        super(TrunkMode, self).__init__(game, 10)
        self.logger = logging.getLogger("Trunk")
        self.trunkhits = 0
        self.trunkTurning = False;
        
    def mode_started(self):
        self.logger.info("Starting trunk mode...")
        base.screenManager.showScreen("trunk")
        self.trunk_screen = base.screenManager.getScreen("trunk")
        self.trunkhits = 0
        self.game.sound.play_music("main",-1)
    
    def mode_stopped(self):
        self.logger.info("Trunk mode complete")
        
    def sw_trunkSwitch_active(self, sw):
        if self.trunkTurning: return
        self.logger.info("Trunk hit")
        self.trunk_screen.turnCW(1, self._trunkTurnFinished)
        self.trunk_screen.vibrate()
        self._handleTrunkHit()
        
    def sw_trunkCC_active(self, sw):
        if self.trunkTurning: return
        self.logger.info("Trunk CC hit")
        self.trunk_screen.turnCC(1, self._trunkTurnFinished)
        self.trunk_screen.vibrate()
        self._handleTrunkHit()
        
    def _handleTrunkHit(self):
        self.trunkTurning = True
        self.game.sound.play("trunk_hit")
        self.game.sound.play("trunk_turn")
        self.trunkhits += 1
        self.logger.info("Trunk hits %s" % str(self.trunkhits))
        if self.trunkhits % 3 == 0:
            # Do something magical
            self.trunk_screen.showTrunkBonus()
            self.game.score(250000)
            self.game.sound.play("bonus_award")
        else:
            self.game.score(4000)
        
        self.trunk_screen.blink_score()
            
    def _trunkTurnFinished(self):
        self.trunkTurning = False
        