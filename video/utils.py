'''
Created on Dec 19, 2012

@author: compy
'''
import os
import pinproc
import logging
class FontLoader(object):
    '''
    classdocs
    '''


    def __init__(self, font_paths):
        '''
        Constructor
        '''
        self.FONT_PATHS = font_paths
        self.font_cache = {}
        
    def load(self, font_file):
        if font_file in self.font_cache.keys():
            return self.font_cache[font_file]
        for path in self.FONT_PATHS:
            if os.path.isfile(path + font_file):
                self.font_cache[font_file] = base.loader.loadFont(path + font_file)
                self.font_cache[font_file].setPixelsPerUnit(60)
                return self.font_cache[font_file]
            
        return False
        
class PandaKeyboard(object):
    def __init__(self):
        self.key_events = []
        self.keys = {}
        self.pressed_keys = []
        self.keys['a'] = False
        self.keys['b'] = False
        self.keys['c'] = False
        self.keys['d'] = False
        self.keys['e'] = False
        self.keys['f'] = False
        self.keys['g'] = False
        self.keys['h'] = False
        self.keys['i'] = False
        self.keys['j'] = False
        self.keys['k'] = False
        self.keys['l'] = False
        self.keys['m'] = False
        self.keys['n'] = False
        self.keys['o'] = False
        self.keys['p'] = False
        self.keys['q'] = False
        self.keys['r'] = False
        self.keys['s'] = False
        self.keys['t'] = False
        self.keys['u'] = False
        self.keys['v'] = False
        self.keys['w'] = False
        self.keys['x'] = False
        self.keys['y'] = False
        self.keys['z'] = False
        self.keys['0'] = False
        self.keys['1'] = False
        self.keys['2'] = False
        self.keys['3'] = False
        self.keys['4'] = False
        self.keys['5'] = False
        self.keys['6'] = False
        self.keys['7'] = False
        self.keys['8'] = False
        self.keys['9'] = False
        self.keys['/'] = False
        self.keys['.'] = False
        self.keys[','] = False
        self.keys[']'] = False
        self.keys['['] = False
        self.keys[';'] = False
        self.keys['\''] = False
        self.keys['enter'] = False
        self.register_keys()
        
        self.key_map = {}
        self.events = []
        
    def get_keyboard_events(self):
        if len(self.events) < 1:
            return []
        event_queue = list(self.events)
        self.events = []
        return event_queue
        
    def register_keys(self):
        for key in self.keys:
            base.accept(key[0], self._key_pressed, [key[0]])
            base.accept(key[0] + "-up", self._key_up, [key[0]])
            
    def is_pressed(self, key):
        return self.keys[key]
            
    def add_key_map(self, key, switch_number):
        """Maps the given *key* to *switch_number*, where *key* is one of the key constants in :mod:`pygame.locals`."""
        self.key_map[key] = switch_number
        logging.info("Adding key map for key %s to switch %s" % (key, str(switch_number)))
    
    def clear_key_map(self):
        """Empties the key map."""
        self.key_map = {}
            
    def _key_pressed(self, key):
        self.keys[key] = True
        self.pressed_keys.append(key)
        if key in self.key_map.keys():
            event = {}
            event['type'] = pinproc.EventTypeSwitchClosedDebounced
            event['value'] = self.key_map[key]
            self.events.append(event)
        
    def _key_up(self, key):
        self.keys[key] = False
        self.pressed_keys.remove(key)
        if key in self.key_map.keys():
            event = {}
            event['type'] = pinproc.EventTypeSwitchOpenDebounced
            event['value'] = self.key_map[key]
            self.events.append(event)