'''
Created on Dec 10, 2012

@author: compy
'''
from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from direct.gui.DirectGui import *
from pandac.PandaModules import *
from direct.gui.OnscreenText import OnscreenText,TextNode
from video.uielements import Menu
from direct.interval.IntervalGlobal import *
from panda3d.core import Vec3, DirectionalLight, VBase4, AmbientLight, Vec4, PerspectiveLens, Spotlight, TexGenAttrib, TextureStage
import os, sys, random
class GameScreen(object):
    '''
    The GameScreen object is the base of all screens in the game. Panda3d offers no support for screen
    management as everything is done within the context of a 'World' object in 3d space.
    
    Panda3d draws in a tree structure:
    render2d
    -- render
       -- modal node (designed by us to show modal screens on top of everything else)
          -- screen nodes
    '''

    hidden = False
    models = []
    
    
    
    def __init__(self,screen_manager,screen_name):
        '''
        Each GameScreen object takes in a screen manager and the screen's text name
        The Screen's text name is useful for titles or inherited screens like the
        service menu where you would want the inherited screen to display a unique title
        at the top of the screen.
        '''
        self.screen_manager = screen_manager
        self.name = screen_name
        
        """
        In each screen, we have a 2d node and a 3d node. The render tree renders 2d and 3d objects
        using separate branches, so all 2d objects must be parented to a 2d node. All 3d objects
        must be parented to a 3d node.
        
        Here we set up a 2d node for drawing 2d objects on our screen. We also set up a 3d node
        that is responsible for drawing 3d objects. Both are parented to our screen manager
        so the screen manager can easily remove these nodes from the tree in order to hide the screen.
        """
        self.node2d = self.screen_manager.get2dNode().attachNewNode(PandaNode(screen_name + "2d"))
        self.node = self.screen_manager.getNode().attachNewNode(PandaNode(screen_name + "3d"))
        
        self.object = DirectObject()
        
        """
        Each major playfield location can have stacks of objects. Objects that are placed using
        place_model() with pos set to a keyword location (left_ramp, left_loop, center_ramp, side_ramp, right_ramp,
        or right_loop) then the model is placed on top of the stack for that location.
        
        When models are removed, the stacks move down
        """
        
        self.stack = {}
        self.stack['left_ramp'] = []
        self.stack['left_loop'] = []
        self.stack['center_ramp'] = []
        self.stack['side_ramp'] = []
        self.stack['right_ramp'] = []
        self.stack['right_loop'] = []
        
        self.last_removed_model = {}
        self.last_removed_model['left_ramp'] = ""
        self.last_removed_model['left_loop'] = ""
        self.last_removed_model['center_ramp'] = ""
        self.last_removed_model['side_ramp'] = ""
        self.last_removed_model['right_ramp'] = ""
        self.last_removed_model['right_loop'] = ""
        
        self.lowest_position = {}
        self.lowest_position['center_ramp'] = (1.5,120,-11)
        self.lowest_position['side_ramp'] = (20, 120, -30)
        self.lowest_position['right_ramp'] = (33.5, 120, -11)
        self.lowest_position['left_ramp'] =  (-13, 120, -23.5)
        self.lowest_position['right_loop'] = (0,0,0)
        self.lowest_position['left_loop'] = (0,0,0)
        
        
    def destroy(self):
        for model in self.models:
            model['model'].destroy()
            model['light'].destroy()
            
        self.models = []
        
    def hide(self):
        self.hidden = True
        self.node2d.detachNode()
        self.node.detachNode()
        self.object.ignoreAll()
    
    def show(self):
        self.hidden = False
        self.node2d.reparentTo(self.screen_manager.get2dNode())
        self.node.reparentTo(self.screen_manager.getNode())
        
    def is_hidden(self):
        return self.hidden
    
    def place_model(self, model_name, scale, pos, rotate = False, rotspeed = 4, h = 0, p = 0, r = 0, reference = "", mode = ""):
        model = base.loader.loadModel("assets/models/" + model_name)
        
        if reference == "":
            reference = "model" + str(random.random())
        
        if type(pos) is tuple:
            model.setPos(pos)
        elif type(pos) is str:
            self.stack[pos].append(reference)
            lowest_pos = self.lowest_position[pos]
            model.setPos((lowest_pos[0],lowest_pos[1],lowest_pos[2] + (10 * (len(self.stack[pos]) - 1))))
        model.setScale(scale)
        if rotate:
            rotate_int = model.hprInterval( rotspeed, Vec3(360,p,r) ).loop()
            
        model.setHpr((h,p,r))
        
        
        if base.displayFlipped:
            model.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullCounterClockwise))
        
        model.reparentTo(self.node)
        
        dlight = DirectionalLight('my dlight')
        dlnp = render.attachNewNode(dlight)
        model.setLight(dlnp)
        
        
        
        result = {}
        result['light'] = dlnp
        result['model'] = model
        result['reference'] = reference
        result['name'] = model_name
        result['mode'] = mode
        
        self.models.append(result)
        
        return result
        
    def remove_bottom_model(self, location):
        if len(self.stack[location]) < 1: return
        lower_model_ref = self.stack[location][0]
        mObj = self.get_model(lower_model_ref)
        self.last_removed_model[location] = mObj['name'].split(".")[0]
        self.remove_model(lower_model_ref)
        self.shift_down(location)
        print "last removed models " + str(self.last_removed_model)
        
    def shift_down(self, location):
        if len(self.stack[location]) < 1: return
        lower_model_ref = self.stack[location][0]
        lowest_pos = self.lowest_position[location]
        first_model = True
        for mRef in self.stack[location]:
            model = self.get_model(mRef)
            if first_model:
                model['model'].posInterval(pos=lowest_pos,duration=1.2,blendType='easeIn').start()
                first_model = False
            else:
                m = model['model']
                model['model'].posInterval(pos=(m.getX(), m.getY(), m.getZ() - 10), duration=1.2, blendType='easeIn').start()
    
    def location_has_object(self, location, mode = ""):
        if len(self.stack[location]) == 0:
            return False
        
        if mode != "":
            lower_model_ref = self.stack[location][0]
            mObj = self.get_model(lower_model_ref)
            #print "Location_has_object " + location + " " + mode + " " + mObj['mode']
            if mObj['mode'] == mode:
                return True
            else:
                return False
        
        return len(self.stack[location]) > 0        
                                                     
    def remove_model(self, reference):
        mSize = (0,0,0)
        for model in self.models:
            if model['reference'] == reference:
                mSize = self.model_size(model['model'])
                model['light'].removeNode()
                model['model'].removeNode()
                self.models.remove(model)
                
        
        for location in self.stack:
            if reference in self.stack[location]:
                self.stack[location].remove(reference)
                print "Reference = " + reference
                print location + " Stack " + str(self.stack[location])
                
                for model in self.stack[location]:
                    m = self.get_model(model)
                    mObj = m['model']
                    x = mObj.getX()
                    y = mObj.getY()
                    z = mObj.getZ()
                
    def clear_stacks(self, location = "all"):
        referencesToRemove = []
        for loc_name in self.stack:
            if loc_name == location or location == "all":
                for model in self.stack[loc_name]:
                    referencesToRemove.append(model)
                    
        for model in referencesToRemove:
            self.remove_model(model)
            
    def get_model(self, reference):
        for model in self.models:
            if model['reference'] == reference:
                return model
        return None
    
    def model_size(self, model):
        min, max = model.getTightBounds()
        return max-min
    
    def set_stack_position(self, stack, position):
        lowest_pos = position
        i = 0
        for m in self.stack[stack]:
            mObj = self.get_model(m)
            model = mObj['model']
            model.setPos((lowest_pos[0],lowest_pos[1],lowest_pos[2] + (10 * i)))
            i += 1
            
    def get_last_removed_model(self, location):
        pass
    def clear_last_removed_model(self, location):
        pass
        
        