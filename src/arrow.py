import pygame
import sys
sys.path.append('..')
from league import *

class Arrow(Character):
    def __init__(self, image, time, direction, engine, z, x, y):
        super().__init__(z, x, y)
        self.delta = 800

        self.x = x
        self.y = y
        self.z = z

        self.engine = engine

        #self.update_direction_func = None

        #if (direction is State.North):
        #self.update_direction_func = self.move_up(time)
        #if (direction is State.South):
        #    self.update_direction_func = self.move_down
        #if (direction is State.East):
        #    self.update_direction_func = self.move_right
        #if (direction is State.West):
        #    self.update_direction_func = self.move_left


        self.image = pygame.transform.scale(image, (31,5))
        self.rect = self.image.get_rect()
        # How big the world is, so we can check for boundries
        self.world_size = (Settings.width, Settings.height)
        # What sprites am I not allowd to cross?
        self.blocks = pygame.sprite.Group()
        # Which collision detection function?
        self.collide_function = pygame.sprite.collide_circle
        self.collisions = []
        # For collision detection, we need to compare our sprite
        # with collideable sprites.  However, we have to remap
        # the collideable sprites coordinates since they change.
        # For performance reasons I created this sprite so we
        # don't have to create more memory each iteration of
        # collision detection.
        self.collider = Drawable()
        self.collider.image = pygame.Surface([Settings.tile_size, Settings.tile_size])
        self.collider.rect = self.collider.image.get_rect()

        self.engine.objects.append(self)
        self.engine.drawables.add(self)
        self.update(0)
    
    def get_instance():
        pass

    def move_left(self, time):
        self.collisions = []
        amount = self.delta * time
        try:
            if self.x - amount < 0:
                raise OffScreenLeftException
            else:
                self.x = self.x - amount
                self.update(0)
                while(len(self.collisions) != 0):
                    self.x = self.x + amount
                    self.update(0)
        except:
            pass

    def move_right(self, time):
        self.collisions = []
        amount = self.delta * time
        try:
            if self.x + amount > self.world_size[0] - Settings.tile_size:
                raise OffScreenRightException
            else:
                self.x = self.x + amount
                self.update(0)
                while(len(self.collisions) != 0):
                    self.x = self.x - amount
                    self.update(0)
        except:
            pass
    def move_up(self, time):
        self.collisions = []
        amount = self.delta * time
        try:
            if self.y - amount < 0:
                raise OffScreenTopException
            else:
                self.y = self.y - amount
                self.update(0)
                if len(self.collisions) != 0:
                    self.y = self.y + amount
                    self.update(0)
                    self.collisions = []
        except:
            pass

    def move_down(self, time):
        self.collisions = []
        amount = self.delta * time
        try:
            if self.y + amount > self.world_size[1] - Settings.tile_size:
                raise OffScreenBottomException
            else:
                self.y = self.y + amount
                self.update(0)
                if len(self.collisions) != 0:
                    self.y = self.y - amount
                    self.update(0)
                    self.collisions = []
        except:
            pass


    def update(self, time):
        self.move_right(time)
        self.rect.x = self.x
        self.rect.y = self.y
        self.collisions = []
        for sprite in self.blocks:
            self.collider.rect.x= sprite.x
            self.collider.rect.y = sprite.y
            if pygame.sprite.collide_rect(self, self.collider):
                self.collisions.append(sprite)