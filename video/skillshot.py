'''
Created on Dec 18, 2012

@author: compy
'''
from direct.task import Task
from direct.gui.DirectGui import *
from pandac.PandaModules import *
from direct.gui.OnscreenText import OnscreenText,TextNode
from gamescreen import GameScreen
from video.uielements import Menu, Sprite
from direct.interval.IntervalGlobal import *
from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
import os, sys

class SkillShotScreen(GameScreen):

    awards = [
              "ADVANCE BONUS X",
              "5000 POINTS",
              "SPOT MTL",
              "START MODE"
              ]

    current_side = 1
    current_award = 0
    cube = None
    _awardText = None
    cubeMovement = None
    cubeRotation = None
    awardMovement = None
    SKILLSHOT_THRESHOLD = 2.34726002216
    def __init__(self, screen_manager):
        super(SkillShotScreen, self).__init__(screen_manager, "skillshot_screen")
        
        # Load our trunk model
        self.cube = base.loader.loadModel("assets/models/powerup.egg")
        # Set its position to:
        # X: -0.4 (just to the left of h-center)
        # Y: 40 (way far back away from the viewer)
        # Z: 0 (vertically center)
        self.cube.setPos(11,40,0)
        # Set the scaling size of the trunk
        self.cube.setScale(0.05,0.05,0.05)
        
        if base.displayFlipped:
            self.cube.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullCounterClockwise))

        # Insert the trunk into this screen's rendering tree
        self.cube.reparentTo(self.node)
        """
        # Set up a splotlight to project onto the trunk
        self.dlight = Spotlight('my dlight')
        # Associate the spotlight to the rendering system
        self.dlnp = render.attachNewNode(self.dlight)
        # Set this trunk's light explicitly so it only takes light from this light
        self.cube.setLight(self.dlnp)
        self.dlnp.lookAt(self.cube)
        
        plight = PointLight('plight')
        plight.setColor(VBase4(1, 1, 1, 1))
        self.plnp = render.attachNewNode(plight)
        self.plnp.setPos(11, 35, 12)
        """
        
        self.dlight = DirectionalLight('dlight')
        self.dlight.setColor(VBase4(1, 1, 1, 1))
        self.dlnp = render.attachNewNode(self.dlight)
        self.dlnp.setHpr(0, -60, 0)
        self.dlnp.lookAt(self.cube)
        
        self.obj = DirectObject()
        
        self.movement_speed = 0.7
        """
        self.explosion = Sprite(
                                parent=self.node, 
                                file_name="assets/sprites/explosion/explosion_", 
                                file_type="png", 
                                num_frames=29, 
                                int_padding=2,
                                scale=(5,5,5))
        """
        
        self.explosion = Sprite(
                                parent=self.node, 
                                file_name="assets/sprites/blue_explosion/blue_explosion_", 
                                file_type="png", 
                                num_frames=13, 
                                int_padding=2,
                                scale=(5,5,5))
        #0.6 - high
        #-0.4 - low
        self._awardText=OnscreenText("RANDOM AWARD",
                                       1,
                                       font=base.fontLoader.load('digital.ttf'),
                                       fg=((0.0/255.0),(255.0/255.0),(255.0/255.0),1),
                                       pos=(1,-0.4),
                                       align=TextNode.ACenter,
                                       scale=.1,
                                       mayChange=True,
                                       parent=self.node2d)
        
        self.cubeRotation = self.cube.hprInterval( 1.2, Vec3(360,0,0) )
        # Set up a sequence to perform the animation in, pause and out... "sequentially"
        self.cubeMovement = Sequence(
                     # Lerp stands for "linearly interpolate", so we move from one position to the other with
                     # an 'easeOut' blend so it comes to a nice slow stop at the end instead of an abrupt finish
                     LerpPosInterval(self.cube,
                        self.movement_speed,
                        pos=(13,40,11),
                        startPos=(13,40,0),
                        blendType='easeOut'
                     ),
                     # Animate back to our home position (off screen) with an ease in so it starts moving gradually
                     LerpPosInterval(self.cube,
                        self.movement_speed,
                        pos=(13,40,0),
                        blendType='easeIn'
                     )
             )
        self.awardMovement = Sequence(
                    LerpFunc(self._updateAwardTextPosition,
                                     fromData=-0.4,
                                     toData=0.6,
                                     duration=self.movement_speed,
                                     blendType='easeOut',
                                     extraArgs=[],
                                     name=None),
                    LerpFunc(self._updateAwardTextPosition,
                                fromData=0.6,
                                toData=-0.4,
                                duration=self.movement_speed,
                                blendType='easeIn',
                                extraArgs=[],
                                name=None)
                    
              )
        
    def _updateAwardTextPosition(self, t):
        self._awardText.setPos(1,t)
        
    def show(self):
        """
        Overridden method that is invoked when the screen is shown.
        
        We use this to orient our camera and spotlights to the appropriate place. We do this because
        not every screen has its own camera. I suppose we could do that in the future the same way that
        each screen has its own 2d and 3d nodes.
        """
        
        # Set the camera a bit up in the air (vertically, not moving forward. Just straight up)
        base.camera.setZ(9.6)
        # Set the pitch negatively a bit so we can look down upon the trunk
        base.camera.setP(-5)
        
        
        # Call our base class show method now so it can render anything it wants
        super(SkillShotScreen, self).show()
        
        # Fire off the sequence
        self.cubeMovement.loop()
        self.cubeRotation.loop()  
        self.awardMovement.loop()   
        base.taskMgr.doMethodLater(0.1, self._advanceAward, 'award_advance')   
        
        self.cube.setLight(self.dlnp)
        
        self.obj.ignoreAll()
        self.obj.acceptOnce("skillshot_hit", self.stop_skillshot_motion)
        self.cube.show()
        self._awardText.show()
    
    def stop_skillshot_motion(self):
        
        self.explosion = Sprite(
                                parent=self.node, 
                                file_name="assets/sprites/blue_explosion/blue_explosion_", 
                                file_type="png", 
                                num_frames=13, 
                                int_padding=2,
                                scale=(5,5,5))
        
        self.cubeRotation.pause()
        self.cubeMovement.pause()
        self.awardMovement.pause()
        base.taskMgr.remove('award_advance')
        self.cube.hide()
        self._awardText.hide()
        self.explosion.setPos(self.cube.getX() - 0.50, 40, self.cube.getZ())
        self.explosion.fps=24
        self.explosion.play(loops=1)
        # -0.3550 is the threshold
        if self.cube.getZ() <= self.SKILLSHOT_THRESHOLD:
            
            base.screenManager.showModalMessage(
                                                message = self.awards[self.current_award],
                                                time = 5.0,
                                                font = "eurostile.ttf",
                                                scale = 0.08,
                                                bg=(0,0,0,1),
                                                fg=(0,1,1,1),
                                                frame_color=(0,1,1,1),
                                                blink_speed = 0.015,
                                                blink_color = (0,0,0,1),
                                                #l r t b
                                                frame_margin = (0.1,0.25,0,0),
                                                animation = 'slide',
                                                start_location = (1.7,0,0.8),
                                                end_location = (1, 0, 0.8)
                                                )
            
    def is_skillshot_hit(self):
        if self.cube.getZ() <= self.SKILLSHOT_THRESHOLD:
            return self.awards[self.current_award]
        else:
            return False
        
    def _advanceAward(self, task):
        self.current_award = (self.current_award + 1) % len(self.awards)
        self._awardText.setText(self.awards[self.current_award])
        return task.again
        
    def hide(self):
        """
        Called when the screen manager wants to remove this screen from the display.
        
        We have no choice but to obey when this method is called. So hide our background.
        
        Our models will be hidden automatically as the 3d nodes are removed from the render tree
        """
        super(SkillShotScreen, self).hide()
        
        if self.cube != None: self.cube.clearLight(self.dlnp)
        if self.cubeMovement: self.cubeMovement.finish()
        if self.cubeRotation: self.cubeRotation.finish()
        if self.awardMovement: self.awardMovement.finish()
        base.taskMgr.remove('award_advance')
        if self._awardText != None: self._awardText.hide()
        
        