from .game_objects import DUGameObject
import pygame

class OffScreenException(Exception):
    pass

class OffScreenLeftException(OffScreenException):
    pass

class OffScreenRightException(OffScreenException):
    pass

class OffScreenTopException(OffScreenException):
    pass

class OffScreenBottomException(OffScreenException):
    pass

class Character(DUGameObject):
    """Represents an updateable, drawable sprite object that
    can respond to collisions and events.  For collision events
    add the sprite and the function to call when the sprite
    and this object collide.
    """
    def __init__(self, z=0, x=0, y=0):
        super().__init__(z, x, y)
        self.events = {}

    def update(self, time):
        for group in self.groups():
            collisions = pygame.sprite.spritecollide(self, group)
            for sprite in collisions:
                if sprite in self.events.keys():
                    self.events[sprite]()
