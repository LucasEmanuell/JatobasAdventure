import math
import time

class AnimationSystem:
    
    @staticmethod
    def breathe(base_scale, amplitude=0.05, speed=5):
        oscillation = math.sin(time.time() * speed) * amplitude
        return base_scale + oscillation

    @staticmethod
    def swing(base_angle, amplitude=10, speed=10):
        return base_angle + math.sin(time.time() * speed) * amplitude

    @staticmethod
    def lerp(start_val, end_val, t):
        return start_val + (end_val - start_val) * t

class Animator:
    def __init__(self):
        self.start_time = time.time()
        
    def get_elapsed(self):
        return time.time() - self.start_time

    def get_walk_cycle(self, speed=10):
        return (time.time() * speed) % 1.0