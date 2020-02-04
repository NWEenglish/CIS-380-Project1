from league import *
import pygame

class Trigger(DGameObject):
    """Currently just a drawable game object"""
    def __init__(self, z=0, x=0, y=0):
        super().__init__(z, x, y)
        self.rect.x = x
        self.rect.y = y
        self._layer = z

    def move_right(self):
        """Test"""
        self.rect.x += 25

    def set_location(self, z, x, y):
        self._layer = z
        self.x = x
        self.y = y