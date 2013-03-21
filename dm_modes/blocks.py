import procgame
import pinproc
import logging
from procgame import *
from dmmode import DMMode

class BlocksMode(DMMode):
    def __init__(self, game):
        super(BlocksMode, self).__init__(game, 3)
        self.logger = logging.getLogger("Blocks")
        
    def mode_started(self):
        self.logger.info("Starting blocks mode")
        base.screenManager.showScreen("blocks")
    
    def mode_stopped(self):
        self.logger.info("Blocks mode complete")
        