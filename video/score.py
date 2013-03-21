from direct.interval.IntervalGlobal import *
from direct.gui.OnscreenText import OnscreenText, TextNode
from direct.showbase.DirectObject import DirectObject
from panda3d.core import *
import sys, imp, os, locale
from uielements import DMDSpriteFont
from gamescreen import GameScreen
from direct.gui.OnscreenImage import OnscreenImage
import random

from direct.gui.DirectGui import *
from pandac.PandaModules import *

class ScoreScreen(GameScreen):
    def __init__(self, screen_manager):
        '''
        Constructor
        '''
        super(ScoreScreen, self).__init__(screen_manager, 'score_screen')
        
        self.player_text=OnscreenText("Player 1",
                                       1,
                                       font=base.fontLoader.load('digital.ttf'),
                                       fg=(1,1,1,1),
                                       pos=(0,.93),
                                       align=TextNode.ACenter,
                                       scale=.1,
                                       mayChange=True,
                                       parent=self.node2d)
        
        self.score_text=OnscreenText("00",
                                       1,
                                       font=base.fontLoader.load('arial.ttf'),
                                       fg=((0.0/255.0),(255.0/255.0),(255.0/255.0),1),
                                       pos=(0,.8),
                                       align=TextNode.ACenter,
                                       scale=.15,
                                       mayChange=True,
                                       parent=self.node2d)
        
        self.ball_text=OnscreenText("BALL 1",
                                       1,
                                       font=base.fontLoader.load('motorwerk.ttf'),
                                       fg=(1,1,1,1),
                                       pos=(1.15,0.92),
                                       scale=.1,
                                       mayChange=True,
                                       parent=self.node2d)
        
        self.acmag_text = DMDSpriteFont("assets/sprites/num_font_dotmatrix", self.node2d, sX = 0.2, sY = 0.2, sZ = 0.2)
        self.acmag_text.hide()
        self.acmag_text.setPos((1.0,0,0.7))
        
        self.clock = OnscreenImage(image = 'assets/images/time.png', pos = (0.78, 0, 0.93),
                                   parent=self.node2d,
                                   scale=.06)
        self.timer_text = OnscreenText("--",
                                       1,
                                       font=base.fontLoader.load('motorwerk.ttf'),
                                       fg=(1,0,0,1),
                                       pos=(0.88,0.92),
                                       scale=.1,
                                       mayChange=True,
                                       parent=self.node2d)
        
        modInfo = self.place_model(model_name = "spinner.egg",
                         scale = (0.1, 0.2, 0.2),
                         pos = (-25,120,-30),
                         rotate = False,
                         p = 7,
                         h = 15,
                         reference = "spinner")
        #modInfo['interval'] = modInfo['model'].hprInterval( 0.6, Vec3(15,450,0) )
        #modInfo['interval'].loop()
        modInfo['interval'] = None
        
        self.spinner = modInfo
        
        self.laser_millions = OnscreenImage(
                                 parent=self.node2d,                        # Parented to our 2d node renderer
                                 image="assets/images/laser_millions.png",     # File name specified
                                 pos=(0,0,-2),                              # z: -2 is off screen at the bottom
                                 scale=(0.3,0.3,0.3))                         # Scale it down a bit horizontally and vertically to make it look right

        
    def spin_spinner(self):
        blue_side = 3435
        red_side = 3255
        
        if random.randint(1,2) == 1:
            angle = blue_side
        else:
            angle = red_side
            
        if self.spinner['interval'] != None:
            self.spinner['interval'].finish()
            self.spinner['interval'] = None
        
        self.spinner['model'].setP(0)
        self.spinner['interval'] = self.spinner['model'].hprInterval( 3, Vec3(15,angle,0), blendType = 'easeOut' )
        self.spinner['interval'].start()
        

        
    def update_acmag_text(self, text):
        self.acmag_text.setText(text)
        self.acmag_text.show()
        
    def hide_acmag_text(self):
        self.acmag_text.hide()
        
    def update_timer_text(self, text):
        self.timer_text.setText(text)
        
    def update_score(self, player, score):
        self.player_text.setText(str(player))
        if score == 0:
            self.score_text.setText("00")
        else:
            self.score_text.setText(str(locale.format("%d", score, grouping=True)))
        
    def update_ball(self, ball):
        self.ball_text.setText("BALL " + str(ball))
        
    def show_score(self):
        self.player_text.show()
        self.score_text.show()
        
    def hide_score(self):
        self.player_text.hide()
        self.score_text.hide()
        
    def blink_score(self):
        i = Sequence(LerpColorScaleInterval(self.score_text, 0.5, VBase4(0, 0, 1, 1)), 
                     LerpColorScaleInterval(self.score_text, 0.5, VBase4(1, 1, 1, 1))
                     ) 
              
        i.start()
        
    def set_score_color(self, color):
        self.score_text.setFg(color)
        
    def show_laser_millions(self):
        # Load our trunk bonus image, parent it to our 2d renderer
        
        # We must also enable transparency on the image otherwise we get big ugly black squares
        self.laser_millions.setTransparency(TransparencyAttrib.MAlpha)
        
        # Set up a sequence to perform the animation in, pause and out... "sequentially"
        s = Sequence(
                     # Lerp stands for "linearly interpolate", so we move from one position to the other with
                     # an 'easeOut' blend so it comes to a nice slow stop at the end instead of an abrupt finish
                     LerpPosInterval(self.laser_millions,
                        0.7,
                        pos=(-1,0,0.7),
                        startPos=(-3,0,0.7),
                        blendType='easeOut'
                     ),
                     # Pause the sequence for 2.5 seconds
                     Wait(2.5),
                     # Animate back to our home position (off screen) with an ease in so it starts moving gradually
                     LerpPosInterval(self.laser_millions,
                        0.7,
                        pos=(-3,0,0.7),
                        blendType='easeIn'
                     )
             )
        # Fire off the sequence
        s.start()