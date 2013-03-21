'''
Created on Dec 10, 2012

@author: compy
'''

from direct.gui.OnscreenText import OnscreenText, TextNode
from direct.gui.OnscreenImage import OnscreenImage
from gamescreen import GameScreen
from direct.gui.DirectGui import *
from direct.task.Task import Task
from direct.stdpy.file import *
from uielements import Sprite
from panda3d.core import *
import sys, imp, os, locale

class AttractScreenBase(GameScreen):
    '''
    This is the base class for all attract screens.
    All attract screens must have the credit flashing at the bottom, so the easiest way
    is to have all attract screens sublcass this class, where the common elements live.
    '''
    _creditAnim = None

    def __init__(self, screen_manager, name):
        '''
        Constructor
        '''
        super(AttractScreenBase, self).__init__(screen_manager, name)
        
        self._creditText=OnscreenText("Credits: 0      Insert Coin",
                                       1,
                                       font=base.fontLoader.load('digital.ttf'),
                                       fg=(1,1,1,1),
                                       pos=(0,-.95),
                                       align=TextNode.ACenter,
                                       scale=.1,
                                       mayChange=True,
                                       parent=self.node2d)
        self._creditAnim = None
        
    def startAnimations(self):
        self._creditAnim = base.taskMgr.doMethodLater(0.8, self.toggleCreditLine, 'credit_flash')
        
    def stopAnimations(self):
        if self._creditAnim == None: return
        base.taskMgr.remove(self._creditAnim)
        self._creditAnim = None
        
    def toggleCreditLine(self, task):
        if self._creditText.isHidden():
            self._creditText.show()
        else:
            self._creditText.hide()
        return task.again
    
    def show(self):
        self.startAnimations()
        super(AttractScreenBase, self).show()
        
        
    def hide(self):
        self.stopAnimations()
        super(AttractScreenBase, self).hide()
        
class PCCScreen(AttractScreenBase):
    tex = None
    def __init__(self, screen_manager):
        super(PCCScreen, self).__init__(screen_manager, "attract_demo")
        
        self.startAnimations()
        
        self.tex = MovieTexture("intro")
        assert self.tex.read("assets/video/PinballControllers_Intro.mp4"), "Failed to load video!"
        
        # Set up a fullscreen card to set the video texture on.
        cm = CardMaker("My Fullscreen Card");
        #cm.setFrame(-1,1,-1,1)
        cm.setFrameFullscreenQuad()
        cm.setUvRange(self.tex)
        card = NodePath(cm.generate())
        card.reparentTo(self.node2d)
        card.setTexture(self.tex)
        card.setBin("fixed",-20)
        #card.setTexScale(TextureStage.getDefault(), self.tex.getTexScale())
        #card.setPos(-0.4,0,0)
    
    def show(self):
        super(PCCScreen, self).show()
        # Load the texture. We could use loader.loadTexture for this,
        # but we want to make sure we get a MovieTexture, since it
        # implements synchronizeTo.
        
        self.tex.setLoop(False)
        self.tex.stop()
        self.tex.play()
        
        #self.screen_manager.showModalMessage("Locating pinballs...", time = 2, scale = 0.07)
        
    def hide(self):
        super(PCCScreen, self).hide()
        if self.tex != None:
            self.tex.setTime(0)

class DMIntroScreen(AttractScreenBase):
    tex = None
    def __init__(self, screen_manager):
        super(DMIntroScreen, self).__init__(screen_manager, "attract_demo2")
        
        #self._testText=OnscreenText("Attract Screen 2",
        #                               1,
        #                               fg=(1,1,1,1),
        #                               pos=(0,0),
        #                               align=TextNode.ACenter,
        #                               scale=.1,
        #                               mayChange=False,
        #                               parent=self.node2d)
        
        self.startAnimations()
        
        self.tex = MovieTexture("dm_title")
        assert self.tex.read("assets/video/DMIntro.mp4"), "Failed to load video!"
        
        # Set up a fullscreen card to set the video texture on.
        cm = CardMaker("DMIntro");
        #cm.setFrame(-1,1,-1,1)
        cm.setFrameFullscreenQuad()
        cm.setUvRange(self.tex)
        card = NodePath(cm.generate())
        card.reparentTo(self.node2d)
        card.setTexture(self.tex)
        card.setBin("fixed",-20)
        #card.setTexScale(TextureStage.getDefault(), self.tex.getTexScale())
        #card.setPos(-0.4,0,0)
        
    def show(self):
        super(DMIntroScreen, self).show()
        # Load the texture. We could use loader.loadTexture for this,
        # but we want to make sure we get a MovieTexture, since it
        # implements synchronizeTo.
        
        self.tex.setLoop(False)
        self.tex.stop()
        self.tex.play()
        
    def hide(self):
        super(DMIntroScreen, self).hide()
        if self.tex != None:
            self.tex.setTime(0)
class HighScoreDisplay(AttractScreenBase):
    def __init__(self, screen_manager):
        super(HighScoreDisplay, self).__init__(screen_manager, "attract_demo3")
        
        
        self._testText=OnscreenText("This would be a high score screen or something",
                                       1,
                                       fg=(1,1,1,1),
                                       pos=(0,0),
                                       align=TextNode.ACenter,
                                       scale=.1,
                                       mayChange=False,
                                       parent=self.node2d)
        hs_bg = list()
        for i in range(1,6):
            hs_bg.append(OnscreenImage(image = 'assets/images/highscore_bg.png', pos = (-0.1, 0, 0.5)))
            
        pZ = 0.8
        for img in hs_bg:
            img.setScale(1.6,1,0.2)
            img.reparentTo(self.node2d)
            img.setPos(-0.1,0,pZ)
            pZ -= 0.4
        
        self.startAnimations()
        
        self._playerInitials = []
        self._playerScores = []
        currentPos = 0.75
        for i in range(5):
            self._playerInitials.append(OnscreenText("JWL",
                                    1,
                                    fg = (0,1,1,1),
                                    font = base.fontLoader.load('motorwerk.ttf'),
                                    pos=(-1,currentPos),
                                    scale = 0.3,
                                    mayChange = True,
                                    parent = self.node2d))
            self._playerScores.append(OnscreenText("00",
                                    1,
                                    fg = (1,1,1,1),
                                    font = base.fontLoader.load('motorwerk.ttf'),
                                    pos=(1.2,currentPos),
                                    scale = 0.3,
                                    align=TextNode.ARight,
                                    mayChange = True,
                                    parent = self.node2d))
            currentPos -= 0.4
        
    def show(self):
        super(HighScoreDisplay, self).show()
        
        # High score category
        high_scores = base.hwgame.highscore_categories[0].scores
        i = 0
        for score in high_scores:
            self._playerInitials[i].setText(score.inits)
            self._playerScores[i].setText(str(locale.format("%d", score.score, grouping=True)))
            i += 1

class GameScoreDisplay(AttractScreenBase):
    def __init__(self, screen_manager):
        super(GameScoreDisplay, self).__init__(screen_manager, "attract_demo4")
        
        
        self._gameOverText=OnscreenText("GAME OVER",
                                       1,
                                       fg=(0,1,1,1),
                                       font=base.fontLoader.load('motorwerk.ttf'),
                                       pos=(0,0.8),
                                       align=TextNode.ACenter,
                                       scale=.2,
                                       mayChange=False,
                                       parent=self.node2d)
        
        self._scoreNodes = {}
        self._playerTextNodes = {}
        
        self._playerTextNodes['1'] = OnscreenText("Player 1",
                                    1,
                                    fg = (1,1,1,1),
                                    font = base.fontLoader.load('motorwerk.ttf'),
                                    pos=(-1,0.6),
                                    scale = 0.15,
                                    mayChange = False,
                                    parent = self.node2d
                                    )
        self._playerTextNodes['2'] = OnscreenText("Player 2",
                                    1,
                                    fg = (1,1,1,1),
                                    font = base.fontLoader.load('motorwerk.ttf'),
                                    pos=(-1,0.2),
                                    scale = 0.15,
                                    mayChange = False,
                                    parent = self.node2d
                                    )
        self._playerTextNodes['3'] = OnscreenText("Player 3",
                                    1,
                                    fg = (1,1,1,1),
                                    font = base.fontLoader.load('motorwerk.ttf'),
                                    pos=(-1,-0.2),
                                    scale = 0.15,
                                    mayChange = False,
                                    parent = self.node2d
                                    )
        self._playerTextNodes['4'] = OnscreenText("Player 4",
                                    1,
                                    fg = (1,1,1,1),
                                    font = base.fontLoader.load('motorwerk.ttf'),
                                    pos=(-1,-0.6),
                                    scale = 0.15,
                                    mayChange = False,
                                    parent = self.node2d
                                    )
        
        self._scoreNodes['1'] = OnscreenText(str(locale.format("%d", 00, grouping=True)),
                                    1,
                                    fg = (1,0,0,1),
                                    font = base.fontLoader.load('motorwerk.ttf'),
                                    pos=(1.2,0.6),
                                    scale = 0.15,
                                    align=TextNode.ARight,
                                    mayChange = True,
                                    parent = self.node2d
                                    )
        self._scoreNodes['2'] = OnscreenText("00",
                                    1,
                                    fg = (1,0,0,1),
                                    font = base.fontLoader.load('motorwerk.ttf'),
                                    pos=(1.2,0.2),
                                    scale = 0.15,
                                    align=TextNode.ARight,
                                    mayChange = True,
                                    parent = self.node2d
                                    )
        self._scoreNodes['3'] = OnscreenText("00",
                                    1,
                                    fg = (1,0,0,1),
                                    font = base.fontLoader.load('motorwerk.ttf'),
                                    pos=(1.2,-0.2),
                                    scale = 0.15,
                                    align=TextNode.ARight,
                                    mayChange = True,
                                    parent = self.node2d
                                    )
        self._scoreNodes['4'] = OnscreenText("00",
                                    1,
                                    fg = (1,0,0,1),
                                    font = base.fontLoader.load('motorwerk.ttf'),
                                    pos=(1.2,-0.6),
                                    scale = 0.15,
                                    align=TextNode.ARight,
                                    mayChange = True,
                                    parent = self.node2d
                                    )
        
        self.showPlayerScores(1)
        
        
    def show(self):
        super(GameScoreDisplay, self).show()
        scores = base.hwgame.game_data['PreviousScores']
        for i in range(len(scores)):
            if scores[i] == 0:
                self._scoreNodes[str(i+1)].setText("00")
            else:
                self._scoreNodes[str(i+1)].setText(str(locale.format("%d", scores[i], grouping=True)))
            
        
    def hidePlayerScores(self, starting_at = 1):
        for i in range(starting_at,5):
            self._scoreNodes[str(i)].hide()
            self._playerTextNodes[str(i)].hide()
            
    def showPlayerScores(self, num_players):
        for i in range(1,5):
            self._scoreNodes[str(i)].hide()
            self._playerTextNodes[str(i)].hide()
            
        for i in range(1,num_players+1):
            self._scoreNodes[str(i)].show()
            self._playerTextNodes[str(i)].show()
        
    
            
        
    