'''
Created on Dec 18, 2012

@author: compy
'''
from direct.task import Task
from direct.gui.DirectGui import *
from pandac.PandaModules import *
from direct.gui.OnscreenText import OnscreenText,TextNode
from gamescreen import GameScreen
from video.uielements import Menu
from direct.interval.IntervalGlobal import *
from panda3d.core import Vec3, DirectionalLight, VBase4, AmbientLight, Vec4, PerspectiveLens, Spotlight, TexGenAttrib, TextureStage
import os, sys

class TrunkScreen(GameScreen):
    '''
    classdocs
    '''
    current_side = 1
    def __init__(self, screen_manager):
        '''
        Creates a new trunk screen with a reference to the given screen manager.
        This function also loads all of our models and stage backgrounds and positions them on the scene accordingly
        '''
        super(TrunkScreen, self).__init__(screen_manager, "trunk_screen")
        
        # Load our trunk model
        self.cube = base.loader.loadModel("assets/models/trunk.egg")
        # Set its position to:
        # X: -0.4 (just to the left of h-center)
        # Y: 40 (way far back away from the viewer)
        # Z: 0 (vertically center)
        self.cube.setPos(-0.4,40,0)
        # Set the scaling size of the trunk
        self.cube.setScale(1.5,1.5,1.5)
        
        if base.displayFlipped:
            self.cube.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullCounterClockwise))

        # Insert the trunk into this screen's rendering tree
        self.cube.reparentTo(self.node)
        
        # Set up a splotlight to project onto the trunk
        self.dlight = Spotlight('my dlight')
        # Associate the spotlight to the rendering system
        self.dlnp = render.attachNewNode(self.dlight)
        # Set this trunk's light explicitly so it only takes light from this light
        self.cube.setLight(self.dlnp)
        
        # Load the curtain background
        self.loadBackground("assets/images/stage-background.png")
        
    def turnCC(self, sides, callback=None):
        """
        Turn the trunk model counter clockwise the number of 'sides' specified
        """
        # Turns run in sequences so that we can optionally call a callback once the
        # rotation is complete.
        seq = Sequence()
        # Get the current heading value (where the trunk is facing)
        hInc = self.cube.getH()
        # Repeat this 90 degree rotation for the number of sides to rotate
        for i in range(sides):
            # Add 90 degrees to the heading so we can rotate to the new face
            hInc = (hInc + 90);
            # Add the 'hpr' (heading/pitch/roll) interval over 1 second to the sequence.
            # This says "Rotate the cube to the new hpr values over a period of 1 second"
            seq.append(self.cube.hprInterval(1, Vec3(hInc,0,0)))
        # If we have a callback specified, tack it on to the end of the sequence as this will be performed when
        # the entire animation sequence is complete
        if callback != None:
            seq.append(Func(callback))
            
        # Fire off the sequence
        seq.start()
        
    def turnCW(self, sides, callback=None):
        """
        Turn the trunk model clockwise the number of 'sides' specified
        """
        seq = Sequence()
        hInc = self.cube.getH()
        for i in range(sides):
            hInc = (hInc - 90);
            seq.append(self.cube.hprInterval(1, Vec3(hInc,0,0)))
            
        if callback != None:
            seq.append(Func(callback))
        seq.start()
        
    def showSide(self, side):
        """
        This function probably doesn't even work and isn't used in code other than for testing.
        It was written at 35,000 feet with some massive dude sitting next to me on the plane, so
        concentration (and trackpad real-estate) was at a damn premium.
        """
        sidesToMove = self.current_side - side
        self.current_side = side
        if sidesToMove > 0:
            self.turnCW(sidesToMove)
        else:
            self.turnCC(sidesToMove * -1)
        
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
        
        # Set our spotlight up in the air (straight up, again)
        self.dlnp.setPos(0,0,6.6)
        # Set the pitch negatively again so the spotlight is shining on the trunk (down from above at an angle)
        self.dlnp.setP(-5)
        
        # Call our base class show method now so it can render anything it wants
        super(TrunkScreen, self).show()
        
        # Rotate the trunk randomly to show some animation
        self.showSide(3)
        
        
        # Display our background image
        self.background.show()
        
    def hide(self):
        """
        Called when the screen manager wants to remove this screen from the display.
        
        We have no choice but to obey when this method is called. So hide our background.
        
        Our models will be hidden automatically as the 3d nodes are removed from the render tree
        """
        self.background.hide()
        super(TrunkScreen, self).hide()
        
    def turnFinished(self):
        self.showSide(1)
        
    def vibrate(self):
        """
        This method is called in order to show a vibration effect on the trunk model after it is hit.
        """
        seq = Sequence()
        # First, we get the current 'home' position so we know where to return the cube to
        # after vibrating
        pos = self.cube.getPos()
        for i in range(4):
            # Now, over 0.02 secs, move the cube to the x,y,z coordinates
            seq.append(self.cube.posInterval(0.02, (-0.1,40,0)))
            # Then move it back home
            seq.append(self.cube.posInterval(0.02, pos))
            # Now move it right
            seq.append(self.cube.posInterval(0.02, (0.1, 40, 0)))
            # Make sure we end back home
            seq.append(self.cube.posInterval(0.02, pos))
        
        seq.start()
        
    def showTrunkBonus(self):
        """
        Show the trunk bonus image on screen by doing an animate up, pause, animate down sequence
        """
        
        # Load our trunk bonus image, parent it to our 2d renderer
        self.trunk_bonus = OnscreenImage(
                                         parent=self.node2d,                        # Parented to our 2d node renderer
                                         image="assets/images/trunk_bonus.png",     # File name specified
                                         pos=(0,0,-2),                              # z: -2 is off screen at the bottom
                                         scale=(0.7,0,0.3))                         # Scale it down a bit horizontally and vertically to make it look right
        
        # We must also enable transparency on the image otherwise we get big ugly black squares
        self.trunk_bonus.setTransparency(TransparencyAttrib.MAlpha)
        
        # Set up a sequence to perform the animation in, pause and out... "sequentially"
        s = Sequence(
                     # Lerp stands for "linearly interpolate", so we move from one position to the other with
                     # an 'easeOut' blend so it comes to a nice slow stop at the end instead of an abrupt finish
                     LerpPosInterval(self.trunk_bonus,
                        0.7,
                        pos=(0,0,0),
                        startPos=(0,0,-2),
                        blendType='easeOut'
                     ),
                     # Pause the sequence for 2.5 seconds
                     Wait(2.5),
                     # Animate back to our home position (off screen) with an ease in so it starts moving gradually
                     LerpPosInterval(self.trunk_bonus,
                        0.7,
                        pos=(0,0,-2),
                        blendType='easeIn'
                     )
             )
        # Fire off the sequence
        s.start()
        
    def loadBackground(self, imagepath): 
        ''' Load a background image behind the models ''' 

        # We use a special trick of Panda3D: by default we have two 2D renderers: render2d and render2dp, the two being equivalent. We can then use render2d for front rendering (like modelName), and render2dp for background rendering. 
        self.background = OnscreenImage(parent=render2dp, image=imagepath) # Load an image object 
        base.cam2dp.node().getDisplayRegion(0).setSort(-20) # Force the rendering to render the background image first (so that it will be put to the bottom of the scene since other models will be necessarily drawn on top) 
        
