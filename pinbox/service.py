#===============================================================================
'''
 Created on Dec 19, 2012
 
 @author: compy
'''
import procgame
import pinproc
import logging
import commands, os, sys
from procgame import *
from procgame.game import Mode
from distutils import dir_util
 
class ServiceModeBase(Mode):
    '''
    This is the game's service mode
    '''
    
    def __init__(self, game, priority = 3):
        super(ServiceModeBase, self).__init__(game, priority)
        
    def mode_started(self):
        self.game.sound.play('service_enter')
    
    def mode_stopped(self):
        self.game.sound.play('service_exit')
        
    def sw_exit_active(self, sw):
        logging.info("%s sw_exit_active" % (str(self)))
        self.game.modes.remove(self)
        return True
        
    def sw_down_active(self, sw):
        if self.game.switches.enter.is_active():
            self.game.modes.remove(self)
            return True
 
class ServiceMainMenu(ServiceModeBase):
    '''
    This is the main service menu that displays all of the options on the service menu
    screen when you first enter the mode.
    '''
    
    def __init__(self, game):
        super(ServiceMainMenu, self).__init__(game, 4)
        self.screen = base.screenManager.getScreen("svc_main")
        
        # Wire up our menu selection events
        self.screen.addMenuSelectionHandler("3D Placement", self._enter3D)
        self.screen.addMenuSelectionHandler("Diagnostics", self._enterDiagnostics)
        self.screen.addMenuSelectionHandler("Update Code", self._updateCode)
        
    def mode_started(self):
        super(ServiceMainMenu, self).mode_started()
        
        self.game.modes.modes = []
        self.game.modes.modes.append(self)
        
        self.game.sound.stop_music()
        
        base.screenManager.hideAllScreens()
        
        # Show the screen finally
        base.screenManager.showScreen("svc_main")
        self.game.disable_all_lamps()
        self.game.gi_off()
        base.screenManager.clearModalMessages()
        
    def mode_stopped(self):
        super(ServiceMainMenu, self).mode_stopped()
        base.screenManager.hideScreen("svc_main")
        self.game.reset()
        
    def sw_down_active(self, sw):
        self.screen.menu.down()
        self.game.sound.play('service_down')
    
    def sw_up_active(self, sw):
        self.screen.menu.up()
        self.game.sound.play('service_up')
        
    def sw_enter_active(self, sw):
        self.screen.menu.enter()
        
    def _enter3D(self):
        logging.info("Enter 3D")
        self.game.modes.add(self.game.service_3d)
        
    def _enterDiagnostics(self):
        logging.info("EnterDiagnostics")
        self.game.modes.add(self.game.service_diagnostics)
        
    def _updateCode(self):
        logging.info("UpdateCode")
        self.game.modes.add(self.game.service_update_code)
        
 
class ServiceDiagnosticsMenu(ServiceModeBase):
    '''
    This is the main diagnostics menu that allows the user to perform
    coil tests, flasher tests, lamp tests, claw tests and switch tests
    '''
    
    def __init__(self, game):
        super(ServiceDiagnosticsMenu, self).__init__(game, 5)
        self.screen = base.screenManager.getScreen("svc_diagnostics")
        
        self.screen.addMenuSelectionHandler("Coil Tests", self._coilTests)
        self.screen.addMenuSelectionHandler("Switch Tests", self._switchTests)
        self.screen.addMenuSelectionHandler("Flasher Tests", self._flasherTests)
        self.screen.addMenuSelectionHandler("View Log", self._viewLog)
        
    def mode_started(self):
        super(ServiceDiagnosticsMenu, self).mode_started()
        
        
        base.screenManager.showScreen("svc_diagnostics")
        
    def mode_stopped(self):
        super(ServiceDiagnosticsMenu, self).mode_stopped()
        base.screenManager.showScreen("svc_main")
        
    def _coilTests(self):
        pass
        
    def _switchTests(self):
        self.game.modes.add(self.game.service_switches)
        
    def _flasherTests(self):
        self.game.modes.add(self.game.service_flashers)
        
    def _viewLog(self):
        self.game.modes.add(self.game.service_log)
        
    def sw_down_active(self, sw):
        self.screen.menu.down()
        self.game.sound.play('service_down')
        return True
    
    def sw_up_active(self, sw):
        self.screen.menu.up()
        self.game.sound.play('service_up')
        return True
        
    def sw_enter_active(self, sw):
        self.screen.menu.enter()
        return True
    
    def sw_exit_active(self, sw):
        self.game.modes.remove(self)
        return True

class ServiceFlashers(ServiceModeBase):
    '''
    This is our flasher test mode
    '''
    def __init__(self, game):
        super(ServiceFlashers, self).__init__(game, 6)
        self.flashers = []
        self.flashers.append("clawFlasher")
        self.flashers.append("jetsFlasher")
        self.flashers.append("sideRampFlasher")
        self.flashers.append("leftRampUpFlasher")
        self.flashers.append("leftRampLwrFlasher")
        self.flashers.append("carChaseCenterFlasher")
        self.flashers.append("carChaseLowerFlasher")
        self.flashers.append("rightRampFlasher")
        self.flashers.append("ejectFlasher")
        self.flashers.append("carChaseUpFlasher")
        self.flashers.append("lowerReboundFlasher")
        self.flashers.append("eyeBallFlasher")
        self.flashers.append("centerRampFlasher")
        self.flashers.append("centerRampFlasher")
        self.flashers.append("elevator2Flasher")
        self.flashers.append("elevator1Flasher")
        self.flashers.append("divertorFlasher")
        self.flashers.append("rightRampUpFlasher")
        
        self.current_selection = 0
        
    def mode_started(self):
        self.current_selection = 0
        self.screen = base.screenManager.getScreen("svc_flashers")
        base.screenManager.showScreen("svc_flashers")
        self.flash()
        
    def mode_stopped(self):
        super(ServiceFlashers, self).mode_stopped()
        base.screenManager.showScreen("svc_diagnostics")
        self.cancel_delayed('flasher_test')
        
    def sw_down_active(self, sw):
        self.current_selection = (self.current_selection - 1)
        if self.current_selection < 0: self.current_selection = len(self.flashers) - 1
        self.game.sound.play('service_down')
        self.screen.set_flasher(self.flashers[self.current_selection])
        return True
    
    def sw_up_active(self, sw):
        self.current_selection = (self.current_selection + 1) % len(self.flashers)
        self.screen.set_flasher(self.flashers[self.current_selection])
        self.game.sound.play('service_up')
        return True
        
    def sw_enter_active(self, sw):
        return True
    
    def sw_exit_active(self, sw):
        self.game.modes.remove(self)
        return True
    
    def flash(self):
        self.game.coils[self.flashers[self.current_selection]].pulse(60)
        self.delay('flasher_test', event_type=None, delay=0.8, handler=self.flash)
        
class ServiceLog(ServiceModeBase):
    '''
    This is our service log viewer
    '''
    def __init__(self, game):
        super(ServiceLog, self).__init__(game, 6)
        self.lines_per_page = 25
        self.num_lines = 0
        self.line_ptr = 0
        self.lines = []
        
    def mode_started(self):
        self.screen = base.screenManager.getScreen("svc_log")
        base.screenManager.showScreen("svc_log")
        
        log_text = ""
        
        with open("system.log","r") as f:
            self.lines = f.readlines()
        
        self.num_lines = len(self.lines)
        if self.num_lines < self.lines_per_page:
            self.lines_per_page = self.num_lines
            
        self.line_ptr = self.num_lines - self.lines_per_page
        
        for i in range(self.line_ptr, self.line_ptr + self.lines_per_page):
            log_text += self.lines[i]
        
        self.screen.set_log_text(log_text)
        
    def mode_stopped(self):
        super(ServiceLog, self).mode_stopped()
        base.screenManager.showScreen("svc_diagnostics")
        
    def sw_down_active(self, sw):
        self.game.sound.play('service_down')
        
        self.line_ptr += self.lines_per_page
        if self.line_ptr >= len(self.lines) - 1:
            self.line_ptr = len(self.lines) - 1 - self.lines_per_page;
            if self.line_ptr < 0:
                self.line_ptr = 0
                
        self.update_page()
        
        return True
    
    def sw_up_active(self, sw):
        self.game.sound.play('service_up')
        
        self.line_ptr -= self.lines_per_page
        if self.line_ptr < 0:
            self.line_ptr = 0
             
        self.update_page()
        
        return True
    
    def update_page(self):
        log_text = ""
        for i in range(self.line_ptr, self.line_ptr + self.lines_per_page):
            log_text += self.lines[i]
        
        self.screen.set_log_text(log_text)
        
    def sw_enter_active(self, sw):
        return True
    
    def sw_exit_active(self, sw):
        self.game.modes.remove(self)
        return True
        
class ServiceSwitches(ServiceModeBase):
    '''
    This is our flasher test mode
    '''
    def __init__(self, game):
        super(ServiceSwitches, self).__init__(game, 6)
        
    def mode_started(self):
        self.screen = base.screenManager.getScreen("svc_switches")
        base.screenManager.showScreen("svc_switches")
        self.screen.set_active(18)
        
    def mode_stopped(self):
        super(ServiceSwitches, self).mode_stopped()
        base.screenManager.showScreen("svc_diagnostics")
        
    def sw_down_active(self, sw):
        return True
    
    def sw_up_active(self, sw):
        return True
        
    def sw_enter_active(self, sw):
        return True
    
    def sw_exit_active(self, sw):
        self.game.modes.remove(self)
        return True

class Service3D(ServiceModeBase):
    '''
    This is the main 3D object placement menu
    '''
    
    def __init__(self, game):
        super(Service3D, self).__init__(game, 5)

        
    def mode_started(self):
        super(Service3D, self).mode_started()
        self.screen = base.screenManager.getScreen("svc_3d")
        base.screenManager.showScreen("svc_3d")

        
    def mode_stopped(self):
        super(Service3D, self).mode_stopped()
        base.screenManager.showScreen("svc_main")
        
    def sw_down_active(self, sw):
        self.screen.down()
        self.game.sound.play('service_down')
        return True
    
    def sw_up_active(self, sw):
        self.screen.up()
        self.game.sound.play('service_up')
        return True
        
    def sw_enter_active(self, sw):
        self.screen.enter()
        return True
    
    def sw_exit_active(self, sw):
        self.game.modes.remove(self)
        return True
    
    def sw_flipperLwR_active(self, sw):
        """
        Move objects right if the left flipper button is not pressed.
        If the left flipper button is pressed, move objects up
        """
        if self.game.switches.flipperLwL.is_active():
            self.screen.move_up()
        else:
            self.screen.move_right()
            
    def sw_flipperLwL_active(self, sw):
        """
        Move objects left if the right flipper button is not pressed.
        If the right flipper button is pressed, move objects down
        """
        if self.game.switches.flipperLwR.is_active():
            self.screen.move_down()
        else:
            self.screen.move_left()

class ServiceUpdateCode(ServiceModeBase):
    '''
    This is the main update code menu
    '''
    
    def __init__(self, game):
        super(ServiceUpdateCode, self).__init__(game, 5)
        self.mount_points = []
        self.game_path = os.path.realpath(os.path.dirname(sys.argv[0]))
        
    def mode_started(self):
        super(ServiceUpdateCode, self).mode_started()
        self.screen = base.screenManager.getScreen("svc_update")
        base.screenManager.showScreen("svc_update")
        self.mount_points = self.get_mount_list()
        self.delay(name='mount_search', event_type=None, delay=2, handler=self.scan_drives)
        self.screen.set_progress("Backing up current game...")
        if os.path.exists(os.path.join(self.game_path, "backup")):
            dir_util.remove_tree(os.path.join(self.game_path, "backup"))
        dir_util.copy_tree(self.game_path, os.path.join(self.game_path, "backup"))
        self.screen.set_progress("Please insert USB update stick...")
        
    def scan_drives(self):
        '''
        Scan the list of new mount points for any that were recently added.
        Once the mount point is seen, check for a 'Pinbox' folder on that device
        
        If one exists, start the update process
        '''
        current_mounts = self.get_mount_list()
        
        if len(current_mounts) < len(self.mount_points):
            self.mount_points = current_mounts
        
        if len(current_mounts) > len(self.mount_points):
            for mp in current_mounts:
                if not mp in self.mount_points:
                    # This one is new!
                    update_folder_path = os.path.join(mp, "pinbox_update/")
                    if os.path.exists(update_folder_path):
                        logging.info("Update folder found at %s")
                        self.screen.set_progress("Updating from USB stick...")
                        dir_util.copy_tree(update_folder_path, self.game_path)
                        self.game.exit_code = -13
                        self.game.exit = True
                        return
                    else:
                        self.screen.set_progress("Update path not found on USB stick\n" + str(update_folder_path))
                        # Kill it all with a -13 restart code
                        
                        
                        return
        
        self.delay(name='mount_search', event_type=None, delay=2, handler=self.scan_drives)
        
    def get_mount_list(self):
        logging.info("Game path " + os.path.realpath(os.path.dirname(sys.argv[0])))
        mount = commands.getoutput('mount -v')
        lines = mount.split('\n')
        points = map(lambda line: line.split()[2], lines)
        return points
        
    def mode_stopped(self):
        super(ServiceUpdateCode, self).mode_stopped()
        base.screenManager.showScreen("svc_main")
        
    def sw_down_active(self, sw):
        self.screen.down()
        self.game.sound.play('service_down')
        return True
    
    def sw_up_active(self, sw):
        self.screen.up()
        self.game.sound.play('service_up')
        return True
        
    def sw_enter_active(self, sw):
        self.screen.enter()
        return True
    
    def sw_exit_active(self, sw):
        self.game.modes.remove(self)
        return True