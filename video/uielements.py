'''
Created on Dec 18, 2012

@author: compy
'''

import logging

from direct.gui.OnscreenText import OnscreenText,TextNode

__all__=["Menu"]
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import DirectFrame,DirectButton,DGG
from direct.gui.OnscreenText import OnscreenText
from pandac.PandaModules import Vec3, TransparencyAttrib, NodePath, PNMImageHeader, PNMImage, Filename, CardMaker, TextureStage, Texture 
from direct.interval.IntervalGlobal import *
from direct.task import Task
from types import *

from math import log, modf 
import os.path

from panda3d.core import CardMaker, PandaNode, NodePath, BillboardEffect, DirectionalLight, CullFaceAttrib

class UIItem(DirectObject):
    def up(self):
        pass
    
    def down(self):
        pass
    
    def enter(self):
        pass
    
    def exit(self):
        pass
    
    def focus(self):
        pass
  
class Menu(UIItem):
    def __init__(self,list=[]):
        self.__menuContainer=DirectFrame(
                                         #text_pos=(0,1),
                                         pos=(0,0,0),
                                         text_scale=1.5,
                                         text_fg=(0,0,0,0),
                                         relief=DGG.FLAT,
                                         frameColor=(1,1,1,0.5)
                                         )
        self.__menuContainer.hide()
        self.__menuItems=[]
        self.selectedItem=0
        self.addItems(list)
        
        
    def addItem(self,text,action):
        self.__menuItems.append(
                                DirectButton(
                                             text=text,
                                             command=self.pressEnter,
                                             extraArgs=[len(self.__menuItems)],
                                             text_align=TextNode.ALeft,
                                             scale=0.1,
                                             #left/right, forward/back, up/down
                                             pos=Vec3(-0.38,0,0.5-(len(self.__menuItems) * 0.15)),
                                             text_fg=(1,1,1,1),
                                             rolloverSound=None,
                                             clickSound=None,
                                             pressEffect=0,
                                             relief=None,
                                             textMayChange=True
                                             #text_font=base.fontLoader.load('Arial Bold.ttf')
                                             )
                                )
        self.__menuItems[-1].reparentTo(self.__menuContainer)
        self.__menuItems[-1].setPythonTag('action',action)
        self.__menuItems[-1].setPythonTag('text',text)
        
    def addItems(self,list):
        for k,v in list:
            self.addItem(k,v)
            
            
    def hasItem(self,text):
        for i in self.__menuItems:
            if(i['text']==text): return True
        return False
    
    
    def __del__(self):
        self.ignoreAll()
        
        
    def pressEnter(self,item=None):
        if(item!=None):
            self.selectedItem=item
            
        logging.info("pressEnter:: selectedItem = %s" % str(self.selectedItem))
            
        action=self.__menuItems[self.selectedItem].getPythonTag('action')
        text=self.__menuItems[self.selectedItem].getPythonTag('text')
        
        logging.info("pressEnter:: action = %s" % str(action))
        
        if(action != None): #function
            #self.hide()
            action(text) #call the function in 'action'


    def enter(self):
        """ Press the enter key to select the current menu item. """
        self.pressEnter()
        UIItem.enter(self)

    def up(self):
        """Move one item up in the menu."""
        newItem=self.selectedItem-1
        if(newItem<0):
            newItem=len(self.__menuItems)-1
        self.select(newItem)

        UIItem.up(self)
        
        
    def down(self):
        """Move one item down in the menu."""
        newItem=self.selectedItem+1
        if(newItem>=len(self.__menuItems)):
            newItem=0
        self.select(newItem)
        
        UIItem.down(self)
        
        
    def select(self,item):
        self.__menuItems[self.selectedItem]['text_fg']=(1,1,1,1)
        self.__menuItems[self.selectedItem]['text_bg']=(0,0,0,0)
        self.selectedItem=item
        self.__menuItems[self.selectedItem]['text_fg']=(0,0,0.5,1)
        self.__menuItems[self.selectedItem]['text_bg']=(1,1,1,1)
        
        
    def show(self):
        assert len(self.__menuItems)>0
        self.select(0) #make the first item selected
        if(self.__menuContainer.isHidden()):
            Sequence(Func(self.__menuContainer.setAlphaScale,0.0),Func(self.__menuContainer.show),LerpFunctionInterval(self.__menuContainer.setAlphaScale,toData=1.0,fromData=0.0,duration=1.0)).start()
        
        
    def hide(self):
        self.ignoreAll()
        if(not self.__menuContainer.isHidden()):
            Sequence(LerpFunctionInterval(self.__menuContainer.setAlphaScale,toData=0.0,fromData=1.0,duration=1.0),Func(self.__menuContainer.hide),Func(self.__menuContainer.setAlphaScale,1.0)).start()
        #now, hide all dialogs referred to:
        for i in self.__menuItems:
            a=i.getPythonTag('action')
            if(isinstance(a,Menu)):
                a.hide()
        
    def setParent(self, parent):
        self.__menuContainer.reparentTo(parent)
        
    def setPos(self,x,y,z):
        self.__menuContainer.setPos(x,y,z)
        
class NameValueList(UIItem):
    """
    A NameValueList is a list of name and value pairs. This is commonly used in the settings screen
    where the user has a list of items and can edit them at any point in time.
    This is just a generic UI element to keep all of the data and logic within the game subsystem
    """
    def __init__(self, items = [], lines_to_show = 5):
        # items is a tuple consisting of (text name of item, selection values, current selection)
        self._items = []
        self._lines_to_show = lines_to_show
        
        self.__menuContainer=DirectFrame(
                                         #text_pos=(0,1),
                                         pos=(-0.6,0,0.3),
                                         text_scale=1.5,
                                         text_align=TextNode.ALeft,
                                         text_fg=(0,0,0,0),
                                         relief=DGG.FLAT,
                                         frameColor=(1,1,1,0),
                                         #left,right,bottom,top
                                         frameSize=(-0.5,0.5,-0.5,0.5)
                                         )
        self.__menuContainer.hide()
        
        self.selectedItem = 0
        
        self.editing = False
        self.blink = False
        self.blinkTask = None
        
        for item in items:
            self.addItem(item[0], item[1], item[2])
            
    def setPos(self, x, y, z):
        self.__menuContainer.setPos(x,y,z)
        
    
    def addItem(self, text_name, selection_values, current_selection_idx = -1):
        """
        Adds an item to the list display.
        text_name - The string representation of the list item
        selection_values - A list of available values for selection in this field
        current_selection - The currently selected item
        """

        pos_name = Vec3(-0.47,0,0.4-(len(self._items) * 0.15))
        pos_value = Vec3(1.0,0,0.4-(len(self._items) * 0.15))
        
        length = len(self._items)
        
        selection_text = ""
        if current_selection_idx != -1:
            selection_text = str(selection_values[current_selection_idx])
        
        name_display = DirectButton(
                     text=text_name,
                     command=None,
                     extraArgs=[len(self._items)],
                     text_align=TextNode.ALeft,
                     scale=0.1,
                     #left/right, forward/back, up/down
                     pos=pos_name,
                     text_fg=(1,1,1,1),
                     rolloverSound=None,
                     clickSound=None,
                     pressEffect=0,
                     relief=None,
                     textMayChange=True
                     #text_font=base.fontLoader.load('Arial Bold.ttf')
                     )
        name_display.reparentTo(self.__menuContainer)
        
        value_display = DirectButton(
                     text=str(selection_text),
                     command=None,
                     extraArgs=[len(self._items)],
                     text_align=TextNode.ALeft,
                     scale=0.1,
                     #left/right, forward/back, up/down
                     pos=pos_value,
                     text_fg=(1,1,1,1),
                     rolloverSound=None,
                     clickSound=None,
                     pressEffect=0,
                     relief=None,
                     textMayChange=True
                     #text_font=base.fontLoader.load('Arial Bold.ttf')
                     )
        
        
        value_display.reparentTo(self.__menuContainer)
        
        v = {}
        v['name'] = text_name
        v['name_display'] = name_display
        v['value_display'] = value_display
        v['selection_values'] = selection_values
        v['current_selection_idx'] = current_selection_idx
        self._items.append(v)
        
    def up(self):
        """Move one item up in the menu."""
        
        if self.editing:
            current_item = self._items[self.selectedItem];
            current_item['current_selection_idx'] = (current_item['current_selection_idx'] + 1) % len(current_item['selection_values'])
            current_item['value_display']['text'] = current_item['selection_values'][current_item['current_selection_idx']]
        else:
        
            newItem=self.selectedItem-1
            if(newItem<0):
                newItem=len(self._items)-1
            self.select(newItem)

        UIItem.up(self)
        
        
    def down(self):
        """Move one item down in the menu."""
        if self.editing:
            current_item = self._items[self.selectedItem]
            current_item['current_selection_idx'] = (current_item['current_selection_idx'] - 1) % len(current_item['selection_values'])
            current_item['value_display']['text'] = current_item['selection_values'][current_item['current_selection_idx']]
        else:
        
            newItem=self.selectedItem+1
            if(newItem>=len(self._items)):
                newItem=0
            self.select(newItem)
        
        UIItem.down(self)
        
    def show(self):
        if(self.__menuContainer.isHidden()):
            Sequence(Func(self.__menuContainer.setAlphaScale,0.0),Func(self.__menuContainer.show),LerpFunctionInterval(self.__menuContainer.setAlphaScale,toData=1.0,fromData=0.0,duration=1.0)).start()
        
        
    def hide(self):
        self.ignoreAll()
        if(not self.__menuContainer.isHidden()):
            Sequence(LerpFunctionInterval(self.__menuContainer.setAlphaScale,toData=0.0,fromData=1.0,duration=1.0),Func(self.__menuContainer.hide),Func(self.__menuContainer.setAlphaScale,1.0)).start()
        
    def setParent(self, parent):
        self.__menuContainer.reparentTo(parent)
    
    def select(self,item):
        self._items[self.selectedItem]['name_display']['text_fg']=(1,1,1,1)
        self._items[self.selectedItem]['name_display']['text_bg']=(0,0,0,0)
        self._items[self.selectedItem]['value_display']['text_fg']=(1,1,1,1)
        self._items[self.selectedItem]['value_display']['text_bg']=(0,0,0,0)
        self.selectedItem=item
        self._items[self.selectedItem]['name_display']['text_fg']=(0,0,0.5,1)
        self._items[self.selectedItem]['name_display']['text_bg']=(1,1,1,1)
        self._items[self.selectedItem]['value_display']['text_fg']=(0,0,0.5,1)
        self._items[self.selectedItem]['value_display']['text_bg']=(1,1,1,1)
        
    def toggleEdit(self):
        self.editing = not self.editing
        if self.editing:
            # Start blinking
            self.blinkTask = base.taskMgr.doMethodLater(0.4, self._doBlink, 'nvBlinkTask')
        else:
            # Stop blinking
            if self.blinkTask != None:
                base.taskMgr.remove(self.blinkTask)
    
    def _doBlink(self, task):
        self.blink = not self.blink
        if self.blink:
            self._items[self.selectedItem]['value_display']['text_fg']=(0,0,0,1)
            self._items[self.selectedItem]['value_display']['text_bg']=(1,1,1,1)
        else:
            self._items[self.selectedItem]['value_display']['text_fg']=(1,1,1,1)
            self._items[self.selectedItem]['value_display']['text_bg']=(0,0,0,0)
        return Task.again
        
class NameValueListItem(UIItem):
    def __init__(self, text_name, selection_items, default_selection = 0):
        name_display = DirectButton(
                     text=text_name,
                     command=None,
                     extraArgs=[len(self._items)],
                     text_align=TextNode.ALeft,
                     scale=0.1,
                     #left/right, forward/back, up/down
                     pos=pos_name,
                     text_fg=(1,1,1,1),
                     rolloverSound=None,
                     clickSound=None,
                     pressEffect=0,
                     relief=None,
                     textMayChange=True
                     #text_font=base.fontLoader.load('Arial Bold.ttf')
                     )
        name_display.reparentTo(self.__menuContainer)
        
        value_display = DirectButton(
                     text=str(selection_text),
                     command=None,
                     extraArgs=[len(self._items)],
                     text_align=TextNode.ALeft,
                     scale=0.1,
                     #left/right, forward/back, up/down
                     pos=pos_value,
                     text_fg=(1,1,1,1),
                     rolloverSound=None,
                     clickSound=None,
                     pressEffect=0,
                     relief=None,
                     textMayChange=True
                     #text_font=base.fontLoader.load('Arial Bold.ttf')
                     )

class DMDSpriteFont(object):
    def __init__(self, fontPath, parent, sX = 1, sY = 1, sZ = 1):
        self.__container=DirectFrame(
                                         #text_pos=(0,1),
                                         pos=(0,0,0),
                                         relief=DGG.FLAT,
                                         frameColor=(1,1,1,0.5)
                                         )
        self.__container.hide()
        self.__container.reparentTo(parent)
        self._planes = []
        self.char_width = sX - 0.06
        self.sX = sX
        self.sY = sY
        self.sZ = sZ
        self.x = 0
        self.y = 0
        self.z = 0
        self.fontPath = fontPath
        
        self.textures = {}
        self.char_translation_map = {
                                     "%": "percent"
                                     }
        
        for c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890%":
            if c in self.char_translation_map:
                char = self.char_translation_map[c]
            else:
                char = c
            if os.path.exists(os.path.join(self.fontPath, char + ".png")):
                logging.info("Loading font texture " + str(char))
                self.textures[c] = base.loader.loadTexture(os.path.join(self.fontPath, char + ".png"))
        
        
    def _addPlane(self):
        plane = base.loader.loadModel('assets/models/plane')
        plane.setPos(self.x + ((len(self._planes) - 1) * self.char_width),self.y,self.z)         #set its position
        plane.setScale(self.sX,self.sY,self.sZ)
        plane.reparentTo(self.__container)       #reparent to render
        plane.setTransparency(1)
        plane.node().setEffect(BillboardEffect.makePointEye())
        self._planes.append(plane)
        return plane
        
    def clear(self):
        for p in self._planes:
            p.removeNode()
        self._planes = []
            
    def setText(self, str_text):
        self.clear()
        for c in str_text:
            if c in self.textures:
                plane = self._addPlane()
                plane.setTexture(self.textures[c],1)
                
    def setPos(self, position):
        self.x = position[0]
        self.y = position[1]
        self.z = position[2]
                
    def hide(self):
        self.__container.hide()
        
    def show(self):
        self.__container.show()
            
            
class Sprite:
    def __init__(self, parent, file_name, file_type, num_frames, int_padding = 1, scale=(1,1,1), fps = 60):
        self.textures = self.loadTextureMovie(num_frames, file_name, file_type, int_padding)
        self.plane = base.loader.loadModel('assets/models/plane')
        self.plane.setPos(0,0,0)         #set its position
        self.plane.setScale(scale[0], scale[1], scale[2])
        self.plane.reparentTo(parent)       #reparent to render
        self.plane.setTransparency(1)
        self.fps = fps
        self.animation_task = None
        self.plane.node().setEffect(BillboardEffect.makePointEye())
        self.currentLoop = 0
        self.lastFrame = 0
        self.trash = False
        
        if base.displayFlipped:
            self.plane.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullCounterClockwise))
        
        #dlight = DirectionalLight('my dlight')
        #dlnp = render.attachNewNode(dlight)
        #self.plane.setLight(dlnp)
        #dlnp.lookAt(self.plane)
        base.sprites.append(self)
        
    def destroy(self):
        self.plane.removeNode()
        self.trash = True
        
    def setLight(self, nodepath):
        self.plane.setLight(nodepath)
        
    def setPos(self,x,y,z):
        self.plane.setPos(x,y,z)
        
    def setPosByTuple(self, tup):
        self.plane.setPos(tup)
        
    def reparentTo(self, node):
        self.plane.reparentTo(node)
        
    def play(self, loops = 1):
        self.loops = loops
        self.currentLoop = 0
        self.lastFrame = 0
        if self.animation_task != None:
            base.taskMgr.remove(self.animation_task)
        self.animation_task = base.taskMgr.add(self.advanceFrame, "anim_" + str(id(self)))
        
    def stop(self):
        if self.animation_task != None:
            base.taskMgr.remove(self.animation_task)
        self.animation_task = None
        
        
    #Our custom load function to load the textures needed for a movie into a
    #list. It assumes the the files are named
    #"path/name<serial number>.extention"
    #It takes the following arguments
    #Frames: The number of frames to load
    #name: The "path/name" part of the filename path
    #suffix: The "extention" part of the path
    #padding: The number of digit the serial number contians:
    #         e.g. if the serial number is 0001 then padding is 4
    def loadTextureMovie(self, frames, name, suffix, padding = 1):
        #The following line is very complicated but does a lot in one line
        #Here's the explanation from the inside out:
        #first, a string representing the filename is built an example is:
        #"path/name%04d.extention"
        #The % after the string is an operator that works like C's sprintf function
        #It tells python to put the next argument (i) in place of the %04d
        #For more string formatting information look in the python manual
        #That string is then passed to the loader.loadTexture function
        #The loader.loadTexture command gets done in a loop once for each frame,
        #And the result is returned as a list.
        #For more information on "list comprehensions" see the python manual
        return [base.loader.loadTexture((name+"%0"+str(padding)+"d."+suffix) % i) 
                for i in range(frames)]
        
    #This function is run every frame by our tasks to animate the textures
    def advanceFrame(self, task):
        #Here we calculate the current frame number by multiplying the current time
        #(in seconds) by the frames per second variable we set earlier
        currentFrame = int(task.time * self.fps)
        
        #print "Current Frame: " + str(currentFrame % len(self.textures)) + ", Last Frame " + str(self.lastFrame)
        
        if (currentFrame % len(self.textures)) < self.lastFrame and self.loops == 1:
            self.trash = True
            return Task.done
        
        self.lastFrame = currentFrame % len(self.textures)
        
        #Now we need to set the current texture on task.obj, which is the object
        #we specified earlier when we loaded the duck and explosion.
        #We will set its texture to one of the textures in the list we defined
        #earlier in task.textures.
        
        #Since we want the movie to loop, we need to reset the image index when it
        #reaches the end. We do this by performing a remainder operation (modulo,
        #"%" in python) on currentFrame with the number of frames, which is the
        #length of our frame list (len(task.textures)).
        #This is a common programming technique to achieve looping as it garuntees
        #a value in range of the list
        #print "AdvanceFrame"
        self.plane.setTexture(self.textures[currentFrame % len(self.textures)], 1)
        if self.loops > 0 and (currentFrame % len(self.textures)) == len(self.textures) - 1:
            self.currentLoop += 1
            if self.currentLoop >= self.loops:
                self.trash = True
                return Task.done
        return Task.cont          #Continue the task indefinitely

