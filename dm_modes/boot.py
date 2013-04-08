import procgame
import pinproc
import logging
from procgame import *
from dmmode import DMMode

class BootMode(DMMode):
    def __init__(self, game):
        super(BootMode, self).__init__(game, 3)
        self.logger = logging.getLogger("Boot")
        
    def mode_started(self):
        self.logger.info("Starting boot sequence...")
        base.screenManager.hideScreen("score")
        base.screenManager.showScreen("boot")
        self.delay(name='boot_loader', event_type=None, delay=.1, handler=self.boot_progress)
    
    def mode_stopped(self):
        self.logger.info("Boot sequence complete")
        
    def boot_progress(self):
        if base.screenManager.getScreen('boot').getLoadingProgress() >= 100:
            self.boot_finish()
            return
        base.screenManager.getScreen('boot').incLoadingProgress(2)
        self.delay(name='boot_loader', event_type=None, delay=.1, handler=self.boot_progress)
        
    def boot_finish(self):
        self.game.sound.play("boot")
        #self.game.sound.play_delayed("gunshot", loops=5, delay=0.05)
        self.game.add_player()
        self.game.modes.remove(self)
        self.game.modes.add(self.game.attract)
        base.screenManager.showModalMessage(
                                            message = "Testing...", 
                                            time = 2, 
                                            scale = 0.2, 
                                            bg=(0,0,0,1),
                                            blink_speed = 0.08,
                                            blink_color = (1,1,1,1))