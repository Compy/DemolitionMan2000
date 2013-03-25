import procgame
import pinproc
import logging
from procgame import *
from dmmode import DMMode

class SkillShotMode(DMMode):
    def __init__(self, game):
        super(SkillShotMode, self).__init__(game, 10)
        self.logger = logging.getLogger("SkillShot")
        self.freeway_hit_yet = False
        
        
    def mode_started(self):
        self.logger.info("Starting skillshot mode...")
        self.cancel_all_delayed()
        base.screenManager.showScreen("skillshot", False)
        self.skillshot_screen = base.screenManager.getScreen("skillshot")
        self.game.sound.play_music("ball_wait_start",-1)
        #self.game.sound.play_music("chase",-1)
        base.screenManager.showScreen("score", False)
        self.freeway_hit_yet = False
        
    
    def mode_stopped(self):
        self.logger.info("Skillshot mode complete")
        base.screenManager.hideScreen("skillshot")
        
    def on_skillshot_hit(self, skillshot):
        if skillshot == "ADVANCE BONUS X":
            self.game.current_player().player_stats['bonus_x'] += 1
        elif skillshot == "5000 POINTS":
            self.game.score(5000)
        elif skillshot == "SPOT MTL":
            if not self.game.current_player().mlit: self.game.current_player().mlit = True
            elif not self.game.current_player().tlit: self.game.current_player().tlit = True
            elif not self.game.current_player().llit: self.game.current_player().llit = True
        elif skillshot == "START MODE":
            pass
        
        
        
    def sw_ballLaunch_active(self, sw):
        if self.game.switches.shooterLane.is_active():
            self.delay(name='end_skillshot', event_type=None, delay=4,handler=self.end_skillshot)
            
    def sw_rightFreeway_active(self, sw):
        # If the freeway switch has already been hit, then ignore this
        if self.freeway_hit_yet: return
        # Check display screen to see if the skillshot target is low enough,
        # if so, count it as a hit. Otherwise, cancel the mode
        base.messenger.send("skillshot_hit")
        self.game.sound.play("woosh")
        self.game.score(1000)
        
        skillshot = self.skillshot_screen.is_skillshot_hit()
        if skillshot != False:
            self.on_skillshot_hit(skillshot)
        
    def sw_sideRampExit_active(self, sw):
        # Skillshot obtained!
        self.game.current_player().player_stats['completed_skillshots'] += 1
        award = (self.game.current_player().player_stats['completed_skillshots']) * 5000000
        self.game.score()
        self.game.sound.play("skillshot")
        # Play some awesome sfx and speech
        
        base.screenManager.showModalMessage(
                                            message="Skillshot!\n" + str(award), 
                                            modal_name="ball_save", 
                                            fg=(1,0,0,1),
                                            frame_color=(1,0,0,1),
                                            blink_speed=0.030,
                                            blink_color=(0,0,0,0),
                                            bg=(0,0,0,1), 
                                            start_location=(1.5,0,0),
                                            end_location=(0,0,0),
                                            animation='slide',
                                            time = 4)
        
        self.end_skillshot()
        
    def end_skillshot(self):
        self.cancel_delayed('end_skillshot')
        self.game.modes.remove(self)
        