'''
Created on Dec 28, 2012

@author: compy
'''

import logging
import random
from panda3d.core import *
from direct.task import Task

class SoundController(object):
    '''
    classdocs
    '''
    
    def __init__(self):
        self.logger = logging.getLogger("p3dsound")
        self.sfxTrack = base.sfxManagerList[0]
        self.musicTrack = base.musicManager
        
        self.currentMusic = None
        
        self.sounds = {}
        self.music = {}
        self.voices = {}
        
        self.master_volume = 0.8
        self.music_volume_diff = -0.3
        self.sound_volume_diff = 0
        self.voice_volume_diff = 0
        
        self.lower_music()
        self.boost_music()
        self.current_music_key = ""


    def play_music(self, key, loops, start_time):
        if key == self.current_music_key: return
        self.current_music_key = key
        self.stop_music()
        self.logger.info("Play Music %s %s %s" % (str(key), str(loops), str(start_time)))
        sound_file = None
        if key in self.music:
            if len(self.music[key]) > 0:
                random.shuffle(self.music[key])
                sound_file = self.music[key][0]
            else:
                sound_file = self.music[key]
            
            if (loops > 0):
                sound_file.setLoopCount(loops)
            elif (loops == -1):
                sound_file.setLoopCount(0)
            sound_file.setTime(start_time)
            sound_file.play()
            self.currentMusic = sound_file
    
    def stop_music(self):
        self.logger.info("Stop music")
        if self.currentMusic != None:
            self.currentMusic.stop()
        
    def fadeout_music(self, time_ms):
        self.logger.info("Fade out music for %s ms" % str(time_ms))
        self.stop_music()
    
    def load_music(self, key):
        self.logger.info("Load music %s" % key)
        
    def register_sound(self, key, sound_file):
        self.logger.info("Register sound key %s file %s" % (key, sound_file))
        new_sound = base.loader.loadSfx(sound_file)
        new_sound.setVolume(self.master_volume + self.sound_volume_diff)
        if key in self.sounds:
            self.sounds[key].append(new_sound)
        else:
            self.sounds[key] = [new_sound]
        
    def register_music(self, key, music_file):
        self.logger.info("Register music key %s file %s" % (key, music_file))
        new_sound = base.loader.loadMusic(music_file)
        new_sound.setVolume(self.master_volume + self.music_volume_diff)
        if key in self.music:
            self.music[key].append(new_sound)
        else:
            self.music[key] = [new_sound]
            
        self.boost_music()
        
    def play(self, key, loops, max_time, fade_ms, fade_music):
        self.logger.info("Play sound %s loops %s max_time %s fade_ms %s" % (key, str(loops), str(max_time), str(fade_ms)))
        
        base.enableAllAudio()
        if key in self.sounds:
            if len(self.sounds[key]) > 0:
                random.shuffle(self.sounds[key])
            if (loops > 0):
                self.sounds[key][0].setLoopCount(loops)
            elif (loops == -1):
                self.sounds[key][0].setLoopCount(0)
            
            if fade_music:
                self.lower_music()
                base.taskMgr.doMethodLater(self.sounds[key][0].length(), self.boost_music, "music_boost", extraArgs = [])
                
            self.sounds[key][0].play()
        
    def play_voice(self, key, loops, max_time, fade_ms, fade_music):
        self.logger.info("Play voice %s loops %s max_time %s fade_ms %s" % (key, str(loops), str(max_time), str(fade_ms)))
        base.enableAllAudio()
        if key in self.voices:
            if len(self.voices[key]) > 0:
                random.shuffle(self.voices[key])
            if (loops > 0):
                self.voices[key][0].setLoopCount(loops)
            elif (loops == -1):
                self.voices[key][0].setLoopCount(0)
                
            if fade_music:
                self.lower_music()
                base.taskMgr.doMethodLater(self.voices[key][0].length(), self.boost_music, "music_boost", extraArgs = [])
                
            self.voices[key][0].play()
        
    def lower_music(self):
        self.set_music_volume((self.master_volume + self.music_volume_diff) - 0.3)
    def boost_music(self):
        self.set_music_volume((self.master_volume + self.music_volume_diff) + 0.3)
        
    def stop(self, key, loops, max_time, fade_ms):
        self.logger.info("Stop sound %s loops %s max_time %s fade_ms %s" % (key, str(loops), str(max_time), str(fade_ms)))
        if key in self.sounds:
            self.sounds[key][0].stop()
        
    def volume_up(self):
        self.logger.info("Volume up")
        if self.master_volume < 1.0:
            self.set_volume(self.master_volume + 0.1)
            
        return self.master_volume * 10
        
    def volume_down(self):
        self.logger.info("Volume down")
        if self.master_volume > 0:
            self.set_volume(self.master_volume - 0.1)
            
        return self.master_volume * 10
        
    def set_volume(self, level):
        logging.info("Set volume to level %s" % str(level))
        self.master_volume = level
        for key in self.sounds:
            self.sounds[key].setVolume((self.master_volume + self.sound_volume_diff))
        
        for key in self.music:
            self.music[key].setVolume((self.master_volume + self.music_volume_diff))
            
        for key in self.voices:
            self.voices[key].setVolume((self.master_volume + self.voice_volume_diff))
            
    def set_music_volume(self, level):
        for key in self.music:
            for mfile in self.music[key]:
                mfile.setVolume(level)
            
    sound_iterations_left = {}
            
    def play_delayed(self, key, loops, delay, callback = None):
        base.taskMgr.remove('snd_loop_' + key)
        self.sound_iterations_left[key] = loops
        base.taskMgr.doMethodLater(delay, self._task_play_delayed, 'snd_loop_' + key, extraArgs = [key,loops,callback])
        
    def stop_delayed(self, key):
        self.sound_iterations_left[key] = 0
        
    def _task_play_delayed(self, key, iterations_left, callback):
        if key in self.sounds:
            if len(self.sounds[key]) > 0:
                random.shuffle(self.sounds[key])

            self.sounds[key][0].play()
            
            if callback != None:
                callback()
            
            self.sound_iterations_left[key] -= 1
            if self.sound_iterations_left[key] > 0:
                return Task.again
            
        del self.sound_iterations_left[key]
        return Task.done
        