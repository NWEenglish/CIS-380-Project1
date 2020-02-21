#!/usr/bin/env python3

import pygame
import sys
sys.path.append('..')
from league import *

class Enemy(Character):
    """This is a sample class for a player object.  A player
    is a character, is a drawable, and an updateable object.
    This class should handle everything a player does, such as
    moving, throwing/shooting, collisions, etc.  It was hastily
    written as a demo but should direction.
    """
    def __init__(self, engine, walk_img, attack_img, health, z=0, x=0, y=0):
        super().__init__(z, x, y)

        # Reference to the engine
        self.engine = engine

        # This unit's health
        self.health = health
        # Last time I was hit
        self.last_hit = pygame.time.get_ticks()
        # A unit-less value.  Bigger is faster.
        self.delta = 256
        # Where the player is positioned
        self.x = x
        self.y = y
        self._layer = z

        # What state the object is in
        self.state = State.MOVE

        # The current direction the object is facing
        self.direction = Direction.SOUTH

        # What frame the object is in
        self.current_frame = 0

        # The objects melee weapon
        # self.sword = Melee_Weapon(6,0,0, engine, self)

        # self.arrow_image = pygame.image.load(walk_img).convert_alpha()

        ## Walk sprites
        self.walk_length = 4
        raw_walk_sprites = Spritesheet(walk_img, 64, self.walk_length)
        walk_south = self.get_sprite_set(raw_walk_sprites, 64, self.walk_length, offset=0)
        walk_north = self.get_sprite_set(raw_walk_sprites, 64, self.walk_length, offset=1)
        walk_east = self.get_sprite_set(raw_walk_sprites, 64, self.walk_length, offset=2)
        walk_west = self.get_sprite_set(raw_walk_sprites, 64, self.walk_length, offset=3)
        walk_sprites = [walk_north, walk_south, walk_east, walk_west]

        ## Attack sprites
        self.attack_length = 4
        raw_attack_sprites = Spritesheet(attack_img, 64, self.attack_length)
        attack_north = self.get_sprite_set(raw_attack_sprites, 64, self.attack_length, offset=0)
        attack_west = self.get_sprite_set(raw_attack_sprites, 64, self.attack_length, offset=1)
        attack_south = self.get_sprite_set(raw_attack_sprites, 64, self.attack_length, offset=2)
        attack_east = self.get_sprite_set(raw_attack_sprites, 64, self.attack_length, offset=3)
        attack_sprites = [attack_north, attack_south, attack_east, attack_west]

        self.state_sprites = [walk_sprites, attack_sprites]

        self.current_sprite_set = self.state_sprites[self.state.value][self.direction.value]

        # The image to use.  This will change frequently
        # in an animated Player class.
        self.image = self.current_sprite_set[0].image.convert_alpha()

        self.image = pygame.transform.scale(self.image, (64, 64))
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
        # Overlay
        self.font = pygame.font.Font('freesansbold.ttf',32)
        self.overlay = self.font.render(str(self.health) + "        4 lives", True, (0,0,0))

    def move_left(self, time):
        if not self.setState(State.MOVE):
            if (self.direction == Direction.WEST):
                self.current_frame = (self.current_frame) % (self.walk_length - 1) + 1
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
            else:
                self.direction = Direction.WEST
                self.current_frame = 0

    def move_right(self, time):
        if not self.setState(State.MOVE):
            if (self.direction == Direction.EAST):
                self.current_frame = (self.current_frame) % (self.walk_length - 1) + 1
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
            else:
                self.direction = Direction.EAST
                self.current_frame = 0

    def move_up(self, time):
        if not self.setState(State.MOVE):
            if (self.direction == Direction.NORTH):
                self.current_frame = (self.current_frame) % (self.walk_length - 1) + 1
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
            else:
                self.direction = Direction.NORTH
                self.current_frame = 0

    def move_down(self, time):
        if not self.setState(State.MOVE):
            if (self.direction == Direction.SOUTH):
                self.current_frame = (self.current_frame) % (self.walk_length - 1) + 1
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
            else:
                self.direction = Direction.SOUTH
                self.current_frame = 0

    def move_idle(self, time):
        if not self.setState(State.MOVE):
            if (self.direction == Direction.SOUTH):
                self.current_frame = self.current_frame
                self.collisions = []
                amount = 0
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
            else:
                self.direction = Direction.SOUTH
                self.current_frame = 0

    # def attack(self, time):
    #     self.sword.x = self.x - 64
    #     self.sword.y = self.y - 64
    #     self.sword.direction = self.direction
    #     self.sword.attack_update()
    #     if not self.setState(State.ATTACK):
    #         self.current_frame = (self.current_frame + 1) % (self.attack_length)
    #         self.sword.current_frame = self.current_frame
    #         self.sword.attack_update()
    #     else:
    #         #self.engine.objects.append(self.sword)
    #         self.engine.drawables.add(self.sword)
    #     pass

    # def range(self, time):
    #     if not self.setState(State.RANGE):
    #         self.current_frame = (self.current_frame + 1) % (self.ranged_length)
    #
    #         if (self.current_frame is 9):
    #             arrow = Arrow(self.arrow_image, self.direction, self.engine, 3,self.x + 31,self.y + 31)
    #             print('length of engine objects is: ')
    #             print(len(self.engine.objects))
    #             print()
    #
    #         if (self.current_frame is 12):
    #             self.current_frame = 3
    #     pass

    def update(self, time):
        self.rect.x = self.x
        self.rect.y = self.y
        self.collisions = []
        self.current_sprite_set = self.state_sprites[self.state.value][self.direction.value]
        self.image = self.current_sprite_set[self.current_frame].image.convert_alpha()
        self.image = pygame.transform.scale(self.image, (64, 64))

        #divide fps by delta and state to step to next frame

        for sprite in self.blocks:
            self.collider.rect.x= sprite.x
            self.collider.rect.y = sprite.y
            if pygame.sprite.collide_rect(self, self.collider):
                self.collisions.append(sprite)

    def ouch(self):
        now = pygame.time.get_ticks()
        if now - self.last_hit > 1000:
            self.health = self.health - 10
            self.last_hit = now

    def setState(self, state):
        # if (state is not State.ATTACK and self.state is State.ATTACK):
            #self.engine.objects.remove(self.sword)
            # self.engine.drawables.remove(self.sword)

        if (self.state is not state):
            self.current_frame = 0
            self.state = state
            return True
        return False

    # Helper function to get a specific row of a spritesheet (offset)
    def get_sprite_set(self, sprite_source, tile_size, per_row, offset=0):
        rtn = []

        for i in range(per_row):
            rtn.append(sprite_source.sprites[offset*per_row + i])

        return rtn

    def reset_loc(self):
        self.x = 200
        self.y = 200































# """ ----------------------------------------------------------------------------------------------------------------
#     This file is used for creating the enemy objects. Current supported enemies are easy_enemy (melee type) and a
#     med_enemy (range type).
#
#     Project 1 - 2D Game
#     Team Psi Phi Labs
#     ---------------------------------------------------------------------------------------------------------------- """
#
# import os
# import pygame
# import sys
# sys.path.append('..')
# from league import *
#
#
# class Enemy(pygame.sprite.Sprite):
#
#     def __init__(self, engine, health, x, y, img):
#         # pygame.sprite.Sprite.__init__(self)
#         # self.image = pygame.image.load(os.path.join('../assets', img))
#         # self.image.convert_alpha()
#         #
#         # self.image.set_colorkey(ALPHA)
#
#
#
#         self.engine = engine
#         # self.rect = self.image.get_rect()
#         self.img = img
#         self.health = health
#         self.delta = 256
#         self.x = x
#         self.y = y
#
#         # What sprites am I not allowd to cross?
#         self.blocks = pygame.sprite.Group()
#
#
#         self.image = pygame.image.load(img).convert_alpha()
#         self.image = pygame.transform.scale(self.image, (64, 64))
#         self.rect = self.image.get_rect()
#
#         self.current_frame = 0
#
#         self.walk_length = 4
#         raw_walk_sprites = Spritesheet(self.img, 64, self.walk_length)
#         walk_south = self.get_sprite_set(raw_walk_sprites, 64, self.walk_length, offset=0)
#         walk_north = self.get_sprite_set(raw_walk_sprites, 64, self.walk_length, offset=1)
#         walk_east = self.get_sprite_set(raw_walk_sprites, 64, self.walk_length, offset=2)
#         walk_west = self.get_sprite_set(raw_walk_sprites, 64, self.walk_length, offset=3)
#         walk_sprites = [walk_north, walk_south, walk_east, walk_west]
#
#         self.state_sprites = [walk_sprites]
#
#         self.state = walk_south
#         # self.state.value = 0
#         self.direction = Direction.SOUTH
#
#         self.current_sprite_set = self.state_sprites[self.state.value][self.direction.value]
#
#         ################################################
#
#         # The image to use.  This will change frequently
#         # in an animated Player class.
#
#         self.image = self.current_sprite_set[0].image.convert_alpha()
#
#         self.image = pygame.transform.scale(self.image, (64, 64))
#         # How big the world is, so we can check for boundries
#         self.world_size = (Settings.width, Settings.height)
#         # What sprites am I not allowd to cross?
#         self.blocks = pygame.sprite.Group()
#         # Which collision detection function?
#         self.collide_function = pygame.sprite.collide_circle
#         self.collisions = []
#         # For collision detection, we need to compare our sprite
#         # with collideable sprites.  However, we have to remap
#         # the collideable sprites coordinates since they change.
#         # For performance reasons I created this sprite so we
#         # don't have to create more memory each iteration of
#         # collision detection.
#         self.collider = Drawable()
#         self.collider.image = pygame.Surface([Settings.tile_size, Settings.tile_size])
#         self.collider.rect = self.collider.image.get_rect()
#
#         # Overlay
#         # self.font = pygame.font.Font('freesansbold.ttf',32)
#         # self.overlay = self.font.render(str(self.health) + "        4 lives", True, (0,0,0))
#
#
#
#     def setState(self, state):
#         # if (state is not State.MELEE and self.state is State.MELEE):
#         #     #self.engine.objects.remove(self.sword)
#         #     self.engine.drawables.remove(self.sword)
#
#         if (self.state is not state):
#             self.current_frame = 0
#             self.state = state
#             return True
#         return False
#
#
#
#     # Borrowed from player.py
#     # Helper function to get a specific row of a spritesheet (offset)
#     def get_sprite_set(self, sprite_source, tile_size, per_row, offset=0):
#         rtn = []
#
#         for i in range(per_row):
#             rtn.append(sprite_source.sprites[offset * per_row + i])
#
#         return rtn
#
#     # Borrowed from player.py
#     def update(self, time):
#         self.rect.x = self.x
#         self.rect.y = self.y
#         self.collisions = []
#         self.current_sprite_set = self.state_sprites[self.state.value][self.direction.value]
#         self.image = self.current_sprite_set[self.current_frame].image.convert_alpha()
#         self.image = pygame.transform.scale(self.image, (64, 64))
#
#         for sprite in self.blocks:
#             self.collider.rect.x= sprite.x
#             self.collider.rect.y = sprite.y
#             if pygame.sprite.collide_rect(self, self.collider):
#                 self.collisions.append(sprite)