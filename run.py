'''
Created on Dec 1, 2012

This is the main entry point for the program. This particular module is responsible for 
setting up the basic panda3d modules and the task chains to run pyprocgame in a different thread.

@author: compy
'''
import locale
import yaml
import sys
import logging
import threading
import time
import sys
import p3dsound

from functools import partial
from Queue import Queue as pyQueue

from pandac.PandaModules import loadPrcFileData

try:
    locale.setlocale(locale.LC_ALL, 'english_us')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'en_US')
    except:
        pass

SIMULATE = False

# Uncomment for full-screen ness
if not SIMULATE: loadPrcFileData('', 'fullscreen 1')

# This is to force the aspect ratio that Panda3d uses so our contents will stretch to the screen size rather
# than just the window stretching
loadPrcFileData('', 'aspect-ratio 1.3333')
loadPrcFileData('', 'win-size 1024 768')

"""
ShowBase is the basic panda3d element. It is roughly equivalent to BasicGame in pyprocgame.
It sets up the underlying panda3d functionality
"""
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText, TextNode
from video.screenmanager import ScreenManager
from video.utils import FontLoader, PandaKeyboard
from panda3d.core import WindowProperties, TextNode
from direct.showbase.PythonUtil import *


logging.basicConfig(level=logging.INFO,
                    filename='system.log',
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


import os
from dm import hwcontroller
"""
These are the paths to search for fonts for Panda3d. We pass these paths to our custom
font loader class (in video.utils) so one call searches all the paths and can load
precompiled fonts as well as ttf fonts
"""
FONT_PATHS = []
FONT_PATHS.append('assets/fonts/')

class PinboxApp(ShowBase):
    """
    This is our core Panda3d game class and is also located on the main thread.
    This class can be referenced by using the 'base' keyword since Panda3d puts
    this into the python builtins.
    """
    
    hwgame = None
    
    def __init__(self):
        if os.path.exists("EXIT_CODE"):
            os.remove("EXIT_CODE")
        logging.info("Starting Pinbox...")
        ShowBase.__init__(self)
        
        self.SIMULATE = SIMULATE
        
        base.displayFlipped = not SIMULATE
        
        #render.setShaderAuto()
        threading.current_thread().setName("Display")
        
        # *** Setup title 
        wp = WindowProperties() 
        wp.setTitle("Pinbox") 
        base.win.requestProperties(wp) 
        
        self.sprites = []
        
        # Set up the base queue for thread-safe communication
        base.display_queue = pyQueue()
        
        self.fontLoader = FontLoader(FONT_PATHS)
        
        self.keyboard = PandaKeyboard()
        self.soundController = p3dsound.SoundController()
        
        
        self.screenManager = ScreenManager(self)
 
        # Set our background color to black
        base.setBackgroundColor(0,0,0)
        # Disable all mouse controls. This prevents the default ShowBase functionality of
        # the moving the camera with the mouse.
        base.disableMouse()
        
        base.accept("play_music", self.soundController.play_music)
        base.accept("stop_music", self.soundController.stop_music)
        base.accept("fadeout_music", self.soundController.fadeout_music)
        base.accept("load_music", self.soundController.load_music)
        base.accept("register_sound", self.soundController.register_sound)
        base.accept("register_music", self.soundController.register_music)
        base.accept("play", self.soundController.play)
        base.accept("play_delayed", self.soundController.play_delayed)
        base.accept("stop_delayed", self.soundController.stop_delayed)
        base.accept("play_voice", self.soundController.play_voice)
        base.accept("stop", self.soundController.stop)
        base.accept("volume_up", self.soundController.volume_up)
        base.accept("volume_down", self.soundController.volume_down)
        base.accept("set_volume", self.soundController.set_volume)
        base.accept("set_music_volume", self.soundController.set_music_volume)
        base.accept("mouse1", self.mouse_down)
        
        # Load up our screens and assets
        self.screenManager.loadScreens()
        
        # Register the events for the screen manager
        # Currently the main use for this is so the screen manager will listen for an event thrown by
        # pyprocgame when the score display needs to be updated. This is thread-safe
        self.screenManager.registerEvents()
        
        # Set up a local instance of HWGame which is the basic pyprocgame class
        self.hwgame = hwcontroller.HWGame(self)
        
        # Set up our task chain so we can handle hardware events in another thread.
        # This prevents us from being throttled at the 60fps framerate by running in the
        # video thread.
        logging.info("Setting up task manager")
        self.taskMgr.setupTaskChain('hw_chain', numThreads = 1)
 
        # Add the hardware interaction to the task manager so we can control
        # the game hardware through pyprocgame
        # We associate it with another task chain called "hw chain" so it can run
        # in another thread
        self.taskMgr.add(self.hw_ctrl, "hw_ctrl", taskChain = "hw_chain")
        self.taskMgr.add(self.check_display_queue, "display_q")
        self.last_loop_time = time.time()
        self.hz = 0
        self.loopcount = 0
        self.do_exit = False
        self.exit_code = 0
        
        # Set up the garbage collector to run every 10 seconds
        self.taskMgr.doMethodLater(10.0, self.garbage_collect, 'Pinbox GC')
        
        # Show the boot screen, this is really the only time that the display thread should
        # manually invoke a screen. Most screen invocations from pyprocgame modes should be performed
        # with:
        # base.screenManager.showScreen("screen_name")
        #
        # The main exception here is in service menus where the underlying hardware controller code
        # only wants to be notified when the user has made a selection from a large list of
        # menus. In that case, its easier to handle screen linking internally within panda3d.
        self.screenManager.showScreen("boot")
        
    def garbage_collect(self, task):
        sprites_to_delete = []
        for s in self.sprites:
            if s.trash:
                s.destroy()
                sprites_to_delete.append(s)
                
        if len(sprites_to_delete) > 0:
            logging.info("GC: Cleaned up " + str(len(sprites_to_delete)) + " sprites")
            for s in sprites_to_delete:
                self.sprites.remove(s)
                del s
                
        return Task.again
 
    def check_display_queue(self, task):
        if self.do_exit:
            text_file = open("EXIT_CODE", "w")
            text_file.write(str(self.exit_code))
            text_file.close()
            sys.exit(self.exit_code)
        try:
            item = base.display_queue.get_nowait()
            item()
        except:
            return Task.cont
        return Task.cont
 
    # This serves to process the run loop iteration in pyprocgame
    def hw_ctrl(self, task):
        
        threading.current_thread().setName("Hardware")
        """
        This is the function that gets called once per loop in panda3d's main framework
        This function calls pyprocgame's run_loop() function, which is only a single iteration
        compared to the usual functionality of performing an infinite loop.
        """
        if (time.time() - self.last_loop_time) >= 1.0:
            self.last_loop_time = time.time();
            self.hz = self.loopcount
            self.loopcount = 0
            
            logging.info("Loop rate is " + str(self.hz) + " hz")
            
        self.hwgame.run_loop()
        self.loopcount += 1
        
        if self.hwgame.exit:
            base.display_queue.put_nowait(partial(self.exit, exit_code = self.hwgame.exit_code))
            logging.critical("Hardware got exit status, killing game loop " + str(self.hwgame.exit_code))
            return Task.done
        
        # Return Task.cont so the task continues to run on the next iteration
        return Task.cont
    
    def mouse_down(self):
        x=base.mouseWatcherNode.getMouseX()
        y=base.mouseWatcherNode.getMouseY()
        base.screenManager.showDebugMessage("(" + str(x)[:7] + ",    " + str(y)[:7] + ")")
        
    def exit(self, exit_code = 0):
        self.do_exit = True
        self.exit_code = exit_code

if __name__ == '__main__':
    app = PinboxApp()
    app.run()