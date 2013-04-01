'''
Created on Dec 18, 2012

@author: compy
'''
import logging
import threading
import random

from panda3d.core import PandaNode, TextNode
from boot import BootScreen
from service import MainMenu, DiagnosticsMenu, TestMainMenu, UpdateCode, ThreeDPlacement, Flashers, Switches, Log
from attract import PCCScreen, DMIntroScreen, HighScoreDisplay, GameScoreDisplay, ThanksDisplay
from bonus import BonusScreen
from blocks import BlocksScreen
from skillshot import SkillShotScreen
from score import ScoreScreen
from computer import ComputerScreen
from acmag import AcmagScreen
from match import MatchScreen
from sanangeles import SanAngelesScreen
from stack import StackScreen
from carchase import CarChaseScreen
from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenText import OnscreenText, TextNode
from functools import partial
from direct.task import Task
from direct.interval.IntervalGlobal import *

class ScreenManager(object):
    '''
    Maintain all instances of screens within this class.
    Screen order is as follows:
    
    ScreenManager
     - render (root node)
       - modal node
         - individual screen nodes
         
    Each screen has its own node in the tree which is the parent of all objects drawn on that screen
    Changing screens is merely done by hiding the individual screen's parent node and show()ing the
    next screen's parent object node
    '''

    
    def __init__(self, game):
        '''
        Set up a 2d node and a 3d node for drawing 2d and 3d objects.
        
        All objects must be parented to their respective nodes in order to be rendered
        '''
        self.game = game
        self._flipNode = render.attachNewNode("flip_node")
        self._flipNode2d = aspect2d.attachNewNode("flip_node2d")
        
        if base.displayFlipped:
            self._flipNode.setScale(-1,1,1)
            self._flipNode2d.setScale(-1,1,1)
        
        self._node = self._flipNode.attachNewNode(PandaNode("screen_manager"))
        self._2dnode = self._flipNode2d.attachNewNode(PandaNode("2dscreen_manager"))
        self.logger = logging.getLogger("ScreenManager")
        self.logger.info("Initializing Screen Manager")
        
        # Create a dictionary to hold our screens
        self.screens = {}
        self.modal_screens = {}
        
        # This shows the frame rate meter at the top right of the screen for diagnostic purposes
        base.setFrameRateMeter(False)
        
        self.modaltext = None
        self.modal_text_color = ""
        self.modal_text_blink_status = False
        
        self.obj = DirectObject()
        
        self.debug_text=OnscreenText("",
            1,
            font=base.fontLoader.load('arial.ttf'),
            fg=(1,1,1,1),
            pos=(1.2,-0.9),
            align=TextNode.ARight,
            scale=.05,
            mayChange=True,
            parent=self._2dnode)
        self.debug_text.hide()
        
    def loadScreens(self):
        '''
        Load all screens into the 'screens' dictionary for quick access.
        '''
        self.screens['boot'] = BootScreen(self)
        self.screens['svc_main_old'] = MainMenu(self)
        self.screens['svc_diagnostics'] = DiagnosticsMenu(self)
        self.screens['svc_update'] = UpdateCode(self)
        self.screens['svc_3d'] = ThreeDPlacement(self)
        self.screens['svc_main'] = MainMenu(self)
        self.screens['svc_flashers'] = Flashers(self)
        self.screens['svc_switches'] = Switches(self)
        self.screens['svc_log'] = Log(self)
        self.screens['stack'] = StackScreen(self)
        self.screens['attract1'] = PCCScreen(self)
        self.screens['attract2'] = DMIntroScreen(self)
        self.screens['attract3'] = HighScoreDisplay(self)
        self.screens['attract4'] = GameScoreDisplay(self)
        self.screens['attract5'] = ThanksDisplay(self)
        self.screens['blocks'] = BlocksScreen(self)
        self.screens['skillshot'] = SkillShotScreen(self)
        self.screens['score'] = ScoreScreen(self)
        self.screens['bonus'] = BonusScreen(self)
        self.screens['computer'] = ComputerScreen(self)
        self.screens['acmag'] = AcmagScreen(self)
        self.screens['match'] = MatchScreen(self)
        self.screens['wtsa'] = SanAngelesScreen(self)
        self.screens['carchase'] = CarChaseScreen(self)
    
    def getScreen(self, name):
        return self.screens[name]
    
    def registerEvents(self):
        self.logger.info("Registering event handlers")
        base.accept("update_score", self._onScoreUpdate)
        self.obj.accept("show_screen", self._thread_safe_showScreen)
        self.obj.accept("update_ball", self._onBallUpdate)
        
    def _onScoreUpdate(self, player, score):
        self.logger.info("onScoreUpdate triggered")
        self.screens['score'].update_score(player, score)
    
    def _onBallUpdate(self, ball):
        self.logger.info("onBallUpdate triggered")
        self.screens['score'].update_ball(ball)
    
    def showScreen(self, screen_name, hideOthers = True, hideScore = False):
        self.logger.info("screenmanager::showScreen Thread: %s Screen: %s" %(str(threading.current_thread().getName()), screen_name))
        #base.messenger.send("show_screen", [screen_name, hideOthers, hideScore])
        #print base.display_queue
        base.display_queue.put_nowait(partial(self._thread_safe_showScreen, screen_name = screen_name, hideOthers = hideOthers, hideScore = hideScore))
        
    def getShownScreens(self):
        shown_screens = []
        for screen in self.screens:
            if not self.screens[screen].is_hidden():
                shown_screens.append(screen)
                
        return shown_screens
        
    def _thread_safe_showScreen(self, screen_name, hideOthers = True, hideScore = False):
        '''
        Show the given screen. If hideOthers is true, all other screens are hidden
        before showing the desired screen.
        '''
        
        if not screen_name in self.screens:
            self.logger.warning("Tried to show screen %s, not in screen list", screen_name)
        if hideOthers:
            for screen in self.screens:
                if screen != 'score':
                    self.screens[screen].hide()
        
            if hideScore:
                self.screens['score'].hide()
                
        # Show the given screen
        self.screens[screen_name].show()
        self.logger.info("Showing screen %s Thread %s" % (screen_name, str(threading.current_thread().getName())))
        
    def hideScreen(self, screen_name):
        base.display_queue.put_nowait(partial(self._thread_safe_hideScreen, screen_name = screen_name))
        
    def hideAllScreens(self):
        base.display_queue.put_nowait(partial(self._thread_safe_hideAllScreens))
        
    def _thread_safe_hideAllScreens(self):
        for screen in self.screens:
            self.screens[screen].hide()
        
    def _thread_safe_hideScreen(self, screen_name):
        self.screens[screen_name].hide()
        
    def getNode(self):
        '''
        Return the 3d node for this screen manager. This is useful for screens
        to obtain a node to parent objects to for drawing (done in the GameScreen constructor)
        '''
        return self._node
    
    def get2dNode(self):
        '''
        Return the 2d node for this screen manager.
        '''
        return self._2dnode
    
    def showDebugMessage(self,
                         message):
        base.taskMgr.remove('hide_debugmsg')
        self.debug_text.setText(message)
        self.debug_text.show()
        base.taskMgr.doMethodLater(10, self.hideDebugMessage, 'hide_debugmsg', extraArgs = [])
        
    def hideDebugMessage(self):
        self.debug_text.hide()
    
    def showModalMessage(self, 
                         message, 
                         modal_name = "", 
                         time = 0, 
                         scale = 0.2, 
                         font = "arial.ttf", 
                         fg = (1,1,0,1), 
                         bg = (0,0,0,1), 
                         frame_color = (1,1,0,1), 
                         animation = "none",
                         start_location = None,
                         end_location = None,
                         animation_duration = 2,
                         blink_speed = 0,
                         blink_color = (0,0,0,1),
                         frame_blink_color = None,
                         frame_width = 4,
                         frame_margin = (0.1,0.1,0.1,0.1)):
        #cardMaker.setFrame(-sizeX/2.0, sizeX/2.0, -sizeY/2.0, sizeY/2.0)
        if modal_name in self.modal_screens:
            self._hideModalMessage(modal_name)
            base.taskMgr.remove('hide_' + modal_name)
            
        if modal_name == "":
            modal_name = "modal_" + str(random.randint(1,63463))
            
        modal_object = {}
            
        modal_object['modaltext'] = TextNode('modal')
        modal_object['modaltext'].setText(message)
        modal_object['modal_text_color'] = fg
        modal_object['blink_color'] = blink_color
        modal_object['modaltext'].setFont(base.fontLoader.load(font))
        modal_object['modaltext'].setTextColor(fg[0], fg[1], fg[2], fg[3])
        
        modal_object['modaltext'].setAlign(TextNode.ACenter)
        
        modal_object['blink_status'] = False
        
        if frame_blink_color == None:
            frame_blink_color = frame_color
        
        # Set our text shadows
        #self.modaltext.setShadow(0.05, 0.05)
        #self.modaltext.setShadowColor(0, 0, 0, 1)
        
        # Set the border
        modal_object['modaltext'].setFrameColor(frame_color[0],frame_color[1],frame_color[2],frame_color[3])
        modal_object['modaltext'].setFrameAsMargin(frame_margin[0],frame_margin[1],frame_margin[2],frame_margin[3])
        modal_object['modaltext'].setFrameLineWidth(frame_width)
        
        # Set the background styling up
        modal_object['modaltext'].setCardColor(bg[0],bg[1],bg[2],bg[3])
        modal_object['modaltext'].setCardAsMargin(0, 0, 0, 0)
        modal_object['modaltext'].setCardDecal(True)
        modal_object['frame_color'] = frame_color
        modal_object['frame_blink_color'] = frame_blink_color
        
        modal_object['modaltextNodePath'] = self._2dnode.attachNewNode(modal_object['modaltext'], 20)
        modal_object['modaltextNodePath'].setScale(scale)
        if start_location != None:
            modal_object['modaltextNodePath'].setPos(start_location)
            
        if animation == "easeIn" or animation == "up":
            interval = LerpPosInterval(modal_object['modaltextNodePath'],
                pos=end_location,
                startPos=start_location,
                blendType='easeIn',
                duration = animation_duration
             ).start()
             
        if animation == "slide":
            seq = Sequence(
                           LerpPosInterval(modal_object['modaltextNodePath'],
                                           pos=end_location,
                                           startPos=start_location,
                                           blendType='easeOut',
                                           duration = 0.8),
                           Wait(time - 1.6),
                           LerpPosInterval(modal_object['modaltextNodePath'],
                                           pos=start_location,
                                           startPos=end_location,
                                           blendType='easeIn',
                                           duration = 0.8)
                           ).start()
        
        self.modal_screens[modal_name] = modal_object
        
        # Set our timer so this message can expire if time is > 0
        if time > 0:
            base.taskMgr.doMethodLater(time, self._hideModalMessage, 'hide_' + modal_name, extraArgs = [modal_name])
            
        if blink_speed > 0:
            base.taskMgr.doMethodLater(blink_speed, self._blinkModalMessage, 'blink_' + modal_name, extraArgs = [modal_name])
            
    def _blinkModalMessage(self, modal_name):
        self.modal_screens[modal_name]['blink_status'] = not self.modal_screens[modal_name]['blink_status']
        
        if self.modal_screens[modal_name]['blink_status']:
            self.modal_screens[modal_name]['modaltext'].setTextColor(
                                         self.modal_screens[modal_name]['modal_text_color'][0], 
                                         self.modal_screens[modal_name]['modal_text_color'][1], 
                                         self.modal_screens[modal_name]['modal_text_color'][2], 
                                         self.modal_screens[modal_name]['modal_text_color'][3])
            self.modal_screens[modal_name]['modaltext'].setFrameColor(
                                         self.modal_screens[modal_name]['frame_color'][0], 
                                         self.modal_screens[modal_name]['frame_color'][1], 
                                         self.modal_screens[modal_name]['frame_color'][2], 
                                         self.modal_screens[modal_name]['frame_color'][3])
        else:
            self.modal_screens[modal_name]['modaltext'].setTextColor(
                                         self.modal_screens[modal_name]['blink_color'][0], 
                                         self.modal_screens[modal_name]['blink_color'][1], 
                                         self.modal_screens[modal_name]['blink_color'][2], 
                                         self.modal_screens[modal_name]['blink_color'][3])
            self.modal_screens[modal_name]['modaltext'].setFrameColor(
                                         self.modal_screens[modal_name]['frame_blink_color'][0], 
                                         self.modal_screens[modal_name]['frame_blink_color'][1], 
                                         self.modal_screens[modal_name]['frame_blink_color'][2], 
                                         self.modal_screens[modal_name]['frame_blink_color'][3])
        return Task.again
            
    def hideModalMessage(self, modal_name):
        if not modal_name in self.modal_screens: return
        self.modal_screens[modal_name]['modaltextNodePath'].removeNode()
        del self.modal_screens[modal_name]
        base.taskMgr.remove('blink_' + modal_name)
        
    def clearModalMessages(self):
        for modal_name in self.modal_screens.copy():
            self.hideModalMessage(modal_name)
        
    def _hideModalMessage(self, modal_name):
        self.hideModalMessage(modal_name)