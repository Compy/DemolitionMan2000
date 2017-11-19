'''
Created on Dec 16, 2012

@author: compy
'''

import procgame
import pinproc
from procgame import *

class DMPlayer(game.Player):
    '''
    classdocs
    '''


    def __init__(self, name):
        '''
        Constructor
        '''
        super(DMPlayer, self).__init__(name)
        self.player_achievements = []
        self.player_stats = {}
        self.player_stats['bonus_x'] = 1
        self.player_stats['combos'] = 1
        self.player_stats['car_crashes'] = 0
        self.player_stats['retina_scans'] = 0
        self.player_stats['completed_skillshots'] = 0
        self.computer_lit = False
        self.multiball_lit = False
        self.extraball_lit = False
        self.mlit = False
        self.tlit = False
        self.llit = False
        self.standup1 = False
        self.standup2 = False
        self.standup3 = False
        self.standup4 = False
        self.standup5 = False
        self.retina_scan_ready = False
        self.quick_freeze = False
        self.access_claw_lit = False
        self.claw_lit = False
        self.timer = 0
        self.explosions = 0
        self.top_popper_shots = 0
        self.bonus_x = 1
        self.sanangeles_in_progress = False
        self.call_for_backup = False
        self.cfb_in_progress = False
        self.super_jets = False
        self.super_jets_left = 25
        
        self.freeze1 = True
        self.freeze2 = True
        self.freeze3 = True
        self.freeze4 = False
        self.retina_value = 5000000
        self.retina_scans = 0
        
        # Check modes that have already been played
        
        '''
        Acmag mode is activated in the pop bumpers with each hit incrementing an overall percentage
        up to 100%. Once 100% power is reached, acmag starts and the whole game darkens and the LED
        strip illuminates red.
        
        This is a simple frenzy where you shoot objects up the middle with combos awarding higher shots
        '''
        self.acmag = False
        self.acmag_percentage = 40
        
        '''
        Explode hurryup is a mode started by daisy chaining a 4 way combo
        Each explode shot awards 5 million points
        '''
        self.explode_hurryup = False
        self.explode_hurryup_ready = False
        
        '''
        Car chase mode is awarded by hitting the car crash 3 times. You build the car chase mode values by hitting
        the car chase ramps (left and right) repeatedly in a 3 way + combo
        '''
        self.car_chase = False
        self.car_crashes = 0
        
        '''
        Fortress multiball is a 2 ball multiball activated by freezing the balls. Balls can be frozen by landing in
        the right inlane when 'light quick freeze' is lit and shooting the left ramp within 5 seconds.
        
        'light quick freeze' is lit either by a random computer award or completing the yellow standups
        
        Fortress multiball has a 3D warehouse at the center of the playfield surrounded by helicopters. The objective
        is to shoot random perpetrators with the ball. Missing decreases flipper strength.
        
        '''
        self.fortress_multiball = False
        self.fortress_multiball_lit = False
        
        '''
        Museum multiball is a 3 ball multiball activated by freezing the balls. Balls can be frozen the same way.
        
        Museum multiball has random objects that you can collect around the museum to add power-ups
        '''
        self.museum_multiball = False
        self.museum_multiball_lit = False
        
        '''
        Wasteland multiball is a 4 ball multiball activated by freezing the balls in the same way.
        
        Wasteland multiball is littered with random Denis Leary quotes and rat burgers
        
        Jackpots are lit every 'x' combos
        '''
        self.wasteland_multiball = False
        self.wasteland_multiball_lit = False
        
        '''
        Cryoprison multiball has multiple jackpots lit. A jackpot shot moves between shots every 5 seconds. Randomly freeze targets
        are placed at various shots. If hit, a side of the playfield will freeze for a configurable amount of time (2-3 seconds)
        
        Various collectibles are also placed in 'ice cubes' at random parts of the playfield. When hit with the ball,
        the ice cube breaks and you are awarded the internal value
        '''
        self.cryoprison_multiball = False
        self.cryoprison_multiball_lit = False
        
        self.arrow_left_loop = False
        self.arrow_left_ramp = False
        self.arrow_acmag = False
        self.arrow_subway = False
        self.arrow_side_ramp = False
        self.arrow_right_ramp = False
        self.arrow_right_loop = False
        self.light_arrows = False
        self.wtsa = False
        
        self.explode_leftloop = False
        self.explode_leftramp = False
        self.explode_rightramp = False
        self.explode_rightloop = False
        
        self.tilt_warnings = 0
        self.tilted = False
        