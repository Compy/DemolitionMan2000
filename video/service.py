'''
Created on Dec 20, 2012

@author: compy
'''
import sys
from direct.gui.DirectGui import *
from panda3d.core import *
from gamescreen import GameScreen
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText, TextNode
from uielements import Menu, NameValueList

class ServiceScreenBase(GameScreen):
    '''
    classdocs
    '''

    def loadBackground(self, imagepath): 
        ''' Load a background image behind the models ''' 

        # We use a special trick of Panda3D: by default we have two 2D renderers: render2d and render2dp, the two being equivalent. We can then use render2d for front rendering (like modelName), and render2dp for background rendering. 
        self.background = OnscreenImage(parent=render2dp, image=imagepath) # Load an image object 
        base.cam2dp.node().getDisplayRegion(0).setSort(-20) # Force the rendering to render the background image first (so that it will be put to the bottom of the scene since other models will be necessarily drawn on top) 

    def __init__(self, screen_manager, screen_name):
        '''
        Constructor
        '''
        self.loadBackground("assets/images/service_bg.jpg")
        super(ServiceScreenBase, self).__init__(screen_manager, screen_name)
        self.title_text=OnscreenText(self.name,
                                       1,
                                       fg=(1,1,1,1),
                                       pos=(-1.3,0.90),
                                       align=TextNode.ALeft,
                                       scale=.12,
                                       mayChange=True,
                                       # font = base.fontLoader.load('Arial Bold.ttf'),
                                       parent=self.node2d)
        
        self.uiitems = []
        self.ui_selection_idx = 0
        self.selection_mode = 'view'
        self._menuSelectionEvents = {}
        
    def hide(self):
        self.background.hide()
        super(ServiceScreenBase, self).hide()
    
    def show(self):
        self.background.show()
        super(ServiceScreenBase, self).show()
        
    ##################################################################
    ## BUTTON HANDLING LOGIC
    ##
    ## The logic here is divided into two modes. 'view' and 'edit'.
    ## In 'view' mode, hitting the down/up buttons scrolls through the
    ## focus of the UI elements on the screen (only ones that can 
    ## accept input). Hitting 'enter' when an item is in focus will
    ## change the state to 'edit' mode.
    ##
    ## In 'edit' mode, hitting the down/up buttons will scroll through
    ## the values of that particular item. Hitting exit will change
    ## the screen back into view mode so scrolling from item to item
    ## works again. Hitting 'enter' will save the current value of the
    ## item and change the screen back into 'view' mode.
    ##################################################################
        
    def down(self):
        if len(self.uiitems) < 1: return

        # If we're in view mode, toggle to the next ui display item
        if self.selection_mode == 'view':
            if self.ui_selection_idx == len(self.uiitems) - 1:
                self.ui_selection_idx = 0
            else:
                self.ui_selection_idx += 1
                
            self.uiitems[self.ui_selection_idx].focus()
        # If we're in edit mode, forward the event to the selected UI item
        else:
            self.uiitems[self.ui_selection_idx].down()
        
    def up(self):
        if len(self.uiitems) < 1: return
        # If we're in view mode, toggle to the next ui display item
        if self.selection_mode == 'view':
            if self.ui_selection_idx == 0:
                self.ui_selection_idx = len(self.uiitems) - 1
            else:
                self.ui_selection_idx -= 1
                
            self.uiitems[self.ui_selection_idx].focus()
        # If we're in edit mode, forward the event to the selected UI item
        else:
            self.uiitems[self.ui_selection_idx].up()
        
    def enter(self):
        if len(self.uiitems) < 1: return
        # If we're currently in view mode, switch to edit mode
        if self.selection_mode == 'view':
            self.selection_mode = 'edit'
        else:
            self.selection_mode = 'view'
        self.uiitems[self.ui_selection_idx].enter()
        
    def exit(self):
        if len(self.uiitems) < 1: return
        # If we're currently in edit mode, switch back to view mode
        if self.selection_mode == 'edit':
            self.selection_mode = 'view'
            self.uiitems[self.ui_selection_idx].exit()
        
    def addMenuSelectionHandler(self, menu_item, callback):
        if menu_item in self._menuSelectionEvents.keys():
            self._menuSelectionEvents[menu_item].append(callback)
        else:
            self._menuSelectionEvents[menu_item] = [callback]
        
    def _menuSelectionMade(self, menu_item):
        if menu_item in self._menuSelectionEvents.keys():
            callback_list = self._menuSelectionEvents[menu_item]
            for callback in callback_list:
                callback()
                
    def set_title(self, title):
        pass

    def set_instruction(self, instruction):
        pass
    
    def set_value(self, value):
        pass
    
    def set_item(self, value):
        pass

class TestMainMenu(ServiceScreenBase):
    def __init__(self, screen_manager):
        super(TestMainMenu, self).__init__(screen_manager, "Service Menu")
        self.instruction_text=OnscreenText("",
                                       1,
                                       fg=(1,1,1,1),
                                       pos=(-1.3,.40),
                                       align=TextNode.ALeft,
                                       scale=.07,
                                       mayChange=True,
                                       # font = base.fontLoader.load('Arial Bold.ttf'),
                                       parent=self.node2d)
        
        self.item_text=OnscreenText("",
                                       1,
                                       fg=(1,1,1,1),
                                       pos=(-1.3,.10),
                                       align=TextNode.ALeft,
                                       scale=.07,
                                       mayChange=True,
                                       # font = base.fontLoader.load('Arial Bold.ttf'),
                                       parent=self.node2d)
        
        self.value_text=OnscreenText("",
                                       1,
                                       fg=(1,1,1,1),
                                       pos=(-1.3,-.20),
                                       align=TextNode.ALeft,
                                       scale=.07,
                                       mayChange=True,
                                       # font = base.fontLoader.load('Arial Bold.ttf'),
                                       parent=self.node2d)
        
        self.menu = NameValueList([
                                   ('Replay Enabled', ['Yes','No'], 0),
                                   ('Other Value', ['Yes','No'], 0),
                                   ('Extra Ball Enabled', ['Yes','No'], 0),
                                   ('Ball Save Timer', ['Yes','No'], 0),
                                   ('Buy In Enabled', ['Yes','No'], 0),
                                   ('Maximum Extra Balls', ['Yes','No'], 0),
                                   ('Maximum Extra Balls 2', ['Yes','No'], 1)
                                  ])
        self.menu.setParent(self.node2d)
        self.menu.select(0)
        self.menu.toggleEdit()
        
        self.menu.setPos(-0.85,0,0.3)
        
        self.menu.down()
        
    def hide(self):
        self.menu.hide()
        super(TestMainMenu, self).hide()
    
    def show(self):
        self.menu.show()
        super(TestMainMenu, self).hide()
        
    def down(self):
        pass
    
    def up(self):
        pass
    
    def enter(self):
        pass
    
    def exit(self):
        pass
    
    
    # Title Layer (self.title_text)
    # Instruction Layer (self.instruction_text)
    # Item Layer (self.item_text)
    # Value Layer (self.value_text)
    def set_title(self, title):
        #self.title_text.setText(title)
        pass
        
    def set_instruction(self, instruction):
        #self.instruction_text.setText(instruction)
        pass
        
    def set_item(self, item):
        #self.item_text.setText(item)
        pass
        
    def set_value(self, strvalue):
        #self.value_text.setText(strvalue)
        pass
    

class MainMenu(ServiceScreenBase):
    def __init__(self, screen_manager):
        super(MainMenu, self).__init__(screen_manager, "Service Menu")
        
        

        
        self.menu = Menu()
        self.menu.setParent(self.node2d)
        self.menu.addItem("Diagnostics", self._menuSelectionMade)
        self.menu.addItem("Reporting", self._menuSelectionMade)
        self.menu.addItem("3D Placement", self._menuSelectionMade)
        self.menu.addItem("Update Code", self._menuSelectionMade)
        self.menu.addItem("Restart", self._menuSelectionMade)
        self.menu.setPos(-0.92,0,0)
        self.menu.show()
        self.uiitems.append(self.menu)
        

class DiagnosticsMenu(ServiceScreenBase):
    def __init__(self, screen_manager):
        super(DiagnosticsMenu, self).__init__(screen_manager, "Diagnostics")
        
        self.menu = Menu()
        self.menu.setParent(self.node2d)
        self.menu.addItem("Coil Tests", self._menuSelectionMade)
        self.menu.addItem("Switch Tests", self._menuSelectionMade)
        self.menu.addItem("Flasher Tests", self._menuSelectionMade)
        self.menu.addItem("Lamp Tests", self._menuSelectionMade)
        self.menu.addItem("View Log", self._menuSelectionMade)
        ## DM SPECIFIC ##
        self.menu.addItem("Claw Tests", self._menuSelectionMade)
        self.menu.setPos(-0.92,0,0)
        self.menu.show()
        
        self.uiitems.append(self.menu)


class ThreeDPlacement(ServiceScreenBase):
    def __init__(self, screen_manager):
        super(ThreeDPlacement, self).__init__(screen_manager, "3D Placement")
        
        self.background.hide()
        self.title_text.hide()
        
        self.place_model(model_name = "police_car.bam",
                         scale = (0.05, 0.05, 0.05),
                         pos = "right_ramp",
                         rotate = True,
                         rotspeed = 4)
        
        self.place_model(model_name = "scanner.egg",
                         scale = (0.6, 0.6, 0.6),
                         pos = "left_ramp",
                         rotate = True,
                         rotspeed = 4)
        
        self.place_model(model_name = "first_aid.bam",
                         scale = (0.02, 0.02, 0.02),
                         pos = "left_ramp",
                         rotate = True,
                         rotspeed = 3)
        
        self.place_model(model_name = "bonus_x.bam",
                         scale = (0.7, 0.7, 0.7),
                         pos = "right_ramp",
                         rotate = True,
                         rotspeed = 3)
        
        self.place_model(model_name = "barrel.bam",
                         scale = (0.2, 0.2, 0.2),
                         pos = "center_ramp",
                         rotate = True,
                         rotspeed = 2,
                         p = 10)
        
        self.place_model(model_name = "barrel.bam",
                         scale = (0.2, 0.2, 0.2),
                         pos = "center_ramp",
                         rotate = True,
                         rotspeed = 2,
                         p = 10)
        
        self.current_selection = 0
        self.current_pos = (0,0,0)
        
        self.left_increment = 0.5
        self.right_increment = 0.5
        self.up_increment = 0.5
        self.down_increment = 0.5
        
        self.selected_stack=OnscreenText(self.stack.keys()[0],
                                       1,
                                       fg=(1,1,1,1),
                                       pos=(-1.3,0.90),
                                       align=TextNode.ALeft,
                                       scale=.10,
                                       mayChange=True,
                                       # font = base.fontLoader.load('Arial Bold.ttf'),
                                       parent=self.node2d)
        
        self.pos_text=OnscreenText("(0,0,0)",
                                       1,
                                       fg=(1,1,1,1),
                                       pos=(-1.3,0.80),
                                       align=TextNode.ALeft,
                                       scale=.08,
                                       mayChange=True,
                                       # font = base.fontLoader.load('Arial Bold.ttf'),
                                       parent=self.node2d)
        self.current_pos = self.lowest_position[self.stack.keys()[self.current_selection]]
        self.pos_text.setText(str(self.current_pos))
        
    def show(self):
        super(ThreeDPlacement, self).show()
        self.background.hide()
        self.title_text.hide()
    
    def down(self):
        self.change_selection()
        
    def up(self):
        self.change_selection()
        
    def move_left(self):
        current_key = self.stack.keys()[self.current_selection]
        new_pos = (self.current_pos[0] - self.left_increment,self.current_pos[1], self.current_pos[2])
        
        self.current_pos = new_pos
        self.set_stack_position(current_key, new_pos)
        self.pos_text.setText(str(self.current_pos))
        
    def move_right(self):
        current_key = self.stack.keys()[self.current_selection]
        new_pos = (self.current_pos[0] + self.right_increment,self.current_pos[1], self.current_pos[2])
        
        self.current_pos = new_pos
        self.set_stack_position(current_key, new_pos)
        self.pos_text.setText(str(self.current_pos))
        
    def move_up(self):
        current_key = self.stack.keys()[self.current_selection]
        new_pos = (self.current_pos[0],self.current_pos[1], self.current_pos[2] + self.up_increment)
        self.current_pos = new_pos
        self.set_stack_position(current_key, new_pos)
        self.pos_text.setText(str(self.current_pos))
        
    def move_down(self):
        current_key = self.stack.keys()[self.current_selection]
        new_pos = (self.current_pos[0],self.current_pos[1], self.current_pos[2] - self.down_increment)
        
        self.current_pos = new_pos
        self.set_stack_position(current_key, new_pos)
        self.pos_text.setText(str(self.current_pos))
        
    def change_selection(self):
        self.current_selection += 1
        self.current_selection = (self.current_selection % (len(self.stack.keys())))
        self.selected_stack.setText(self.stack.keys()[self.current_selection])
        self.current_pos = self.lowest_position[self.stack.keys()[self.current_selection]]
        self.pos_text.setText(str(self.current_pos))
        
    def enter(self):
        pass
        
    def exit(self):
        pass
        
class Flashers(ServiceScreenBase):
    def __init__(self, screen_manager):
        super(Flashers, self).__init__(screen_manager, "Flasher Test")
        
        self.current_flasher=OnscreenText("",
                                       1,
                                       fg=(1,1,1,1),
                                       pos=(-1.3,0.60),
                                       align=TextNode.ALeft,
                                       scale=.10,
                                       mayChange=True,
                                       # font = base.fontLoader.load('Arial Bold.ttf'),
                                       parent=self.node2d)
        
    def set_flasher(self, text):
        self.current_flasher.setText(text)

class Log(ServiceScreenBase):
    def __init__(self, screen_manager):
        super(Log, self).__init__(screen_manager, "System Log")
        
        self.log_view=OnscreenText("",
                                       1,
                                       fg=(1,1,1,1),
                                       pos=(-1.3,0.80),
                                       align=TextNode.ALeft,
                                       scale=.05,
                                       mayChange=True,
                                       parent=self.node2d)
        
    def set_log_text(self, text):
        self.log_view.setText(text)
        
class Switches(ServiceScreenBase):
    def __init__(self, screen_manager):
        super(Switches, self).__init__(screen_manager, "Switch Test")
        
        self.current_switch=OnscreenText("",
                                       1,
                                       fg=(1,1,1,1),
                                       pos=(-1.3,0.60),
                                       align=TextNode.ALeft,
                                       scale=.10,
                                       mayChange=True,
                                       # font = base.fontLoader.load('Arial Bold.ttf'),
                                       parent=self.node2d)
        self.switches = OnscreenImage(parent=self.node2d, 
                                      image="assets/images/switch_matrix.jpg",
                                      scale = (1,1,0.8))
        # Size
        # (0.15, 0, 0.174)
        self.switch_active = OnscreenImage(parent=self.node2d,
                                           image="assets/images/switch_active.png",
                                           scale = (0.075,0.1,0.087),
                                           pos=(-0.456,0,0.52156))
        self.switch_active.setTransparency(TransparencyAttrib.MAlpha)
    
    def set_active(self, swnum):
        swnum = swnum - 11
        base_pos = (-0.456,0,0.52156)
        pos = (base_pos[0],0,base_pos[2] - (swnum * 0.174) + 0.005)
        self.switch_active.setPos(pos)
    
    def img_size(self, model):
        min, max = model.getTightBounds()
        return max-min
        
    def set_switch(self, text):
        self.current_switch.setText(text)
        
    def show(self):
        super(Switches, self).show()
        self.switches.show()
        self.switch_active.show()
        
    def hide(self):
        super(Switches, self).hide()
        self.switches.hide()
        self.switch_active.hide()
        
class UpdateCode(ServiceScreenBase):
    def __init__(self, screen_manager):
        super(UpdateCode, self).__init__(screen_manager, "Update Code")
        
        self.progress_text=OnscreenText("Please insert USB update stick...",
                                       1,
                                       fg=(1,1,1,1),
                                       pos=(-1.3,0.50),
                                       align=TextNode.ALeft,
                                       scale=.10,
                                       mayChange=True,
                                       # font = base.fontLoader.load('Arial Bold.ttf'),
                                       parent=self.node2d)
        
    def set_progress(self, text):
        self.progress_text.setText(text)
        