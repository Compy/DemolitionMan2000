import procgame
import pinproc
import logging
from procgame import *
from dmmode import DMMode

class StatusDisplayMode(DMMode):
    status_display_options = [
                              'player_stats',
                              'player_scores',
                              'bonus',
                              'high_scores'
                              ]
    shown_screens = []
    def __init__(self, game):
        super(StatusDisplayMode, self).__init__(game, 11)
        self.logger = logging.getLogger("StatusDisplay")
        
        
    def mode_started(self):
        self.logger.info("Starting status mode...")
        #base.screenManager.showScreen("skillshot", False)
        #self.status_screen = base.screenManager.getScreen("status_display")
        #self.game.sound.play_music("launch_wait",-1)
        self.shown_screens = base.screenManager.getShownScreens()
    
    def mode_stopped(self):
        self.logger.info("StatusDisplay mode complete")
        # hide our status display screen
        
        # show all previously shown screens
        #for screen in self.shown_screens:
        #    base.screenManager.showScreen(screen, False)
    
    def sw_flipperLwR_open(self,sw):
        # If this flipper is the status held flipper, then abort the mode
        if self.game.status_held_flipper == 'R':
            self.game.modes.remove(self)
    
    def sw_flipperLwL_open(self,sw):
        # If this flipper is the status held flipper, then abort the mode
        if self.game.status_held_flipper == 'L':
            self.game.modes.remove(self)
            
    def sw_flipperLwL_active(self, sw):
        # If this flipper is not the status held flipper, then advance to the next status screen
        if self.game.status_held_flipper != 'L':
            self.advance_status()
    
    def sw_flipperLwR_active(self, sw):
        # If this flipper is not the status held flipper, then advance to the next status screen
        if self.game.status_held_flipper != 'R':
            self.advance_status()
    
    def advance_status(self):
        self.logger.info("Advancing status screen")
            
        