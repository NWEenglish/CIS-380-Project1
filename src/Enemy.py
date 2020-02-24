#!/usr/bin/env python3

import pygame
import time
import math
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
    def __init__(self, engine, user, walk_img, attack_img, health, z=0, x=0, y=0):
        super().__init__(z, x, y)

        self.user = user
        self.m_e_d = False
        self.m_e_u = False
        self.m_e_r = False
        self.m_e_l = False
        self.m_e_i = False
        self.move_enemy_right = pygame.USEREVENT + 0
        self.move_enemy_left = pygame.USEREVENT + 1
        self.move_enemy_up = pygame.USEREVENT + 2
        self.move_enemy_down = pygame.USEREVENT + 3
        self.attack_enemy_north = pygame.USEREVENT + 4
        self.attack_enemy_south = pygame.USEREVENT + 5
        self.attack_enemy_east = pygame.USEREVENT + 6
        self.attack_enemy_west = pygame.USEREVENT + 7

        engine.events[self.move_enemy_right] = self.move_right
        engine.events[self.move_enemy_left] = self.move_left
        engine.events[self.move_enemy_up] = self.move_up
        engine.events[self.move_enemy_down] = self.move_down
        engine.events[self.attack_enemy_north] = self.attack_north
        engine.events[self.attack_enemy_south] = self.attack_south
        engine.events[self.attack_enemy_east] = self.attack_east
        engine.events[self.attack_enemy_west] = self.attack_west

        # First sprite sheet
        self.first_spritesheet = walk_img

        # Second sprite sheet
        self.second_spritesheet = attack_img

        # Reference to the engine
        self.engine = engine

        # This unit's health
        self.health = health
        # Last time I was hit
        self.last_hit = pygame.time.get_ticks()

        # Last time enemy attacked.
        self.last_attack = time.time()

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

        self.update_spritesheet(self.first_spritesheet)


    def update_spritesheet(self, spritesheet_image):
        # Walk sprites
        self.walk_length = 4
        raw_walk_sprites = Spritesheet(spritesheet_image, 64, self.walk_length)
        walk_south = self.get_sprite_set(raw_walk_sprites, 64, self.walk_length, offset=0)
        walk_north = self.get_sprite_set(raw_walk_sprites, 64, self.walk_length, offset=1)
        walk_east = self.get_sprite_set(raw_walk_sprites, 64, self.walk_length, offset=2)
        walk_west = self.get_sprite_set(raw_walk_sprites, 64, self.walk_length, offset=3)
        walk_sprites = [walk_north, walk_south, walk_east, walk_west]

        self.state_sprites = [walk_sprites]

        self.current_sprite_set = self.state_sprites[self.state.value][self.direction.value]

        self.image = self.current_sprite_set[0].image.convert_alpha()

        self.image = pygame.transform.scale(self.image, (64, 64))


    def move_left(self, time):
        if not self.setState(State.MOVE):

            self.update_spritesheet(self.first_spritesheet)

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

            self.update_spritesheet(self.first_spritesheet)

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

            self.update_spritesheet(self.first_spritesheet)

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

            self.update_spritesheet(self.first_spritesheet)

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

            self.update_spritesheet(self.first_spritesheet)

            if (self.direction == Direction.SOUTH):
                self.current_frame = self.current_frame
                self.collisions = []
                amount = 0
                try:
                    if self.y + amount > self.world_size[1] - Settings.tile_size:
                        raise OffScreenBottomException
                    else:
                        self.update(0)
                        if len(self.collisions) != 0:
                            self.update(0)
                            self.collisions = []
                except:
                    pass
            else:
                self.direction = Direction.SOUTH
                self.current_frame = 0

    def attack_south(self, time):
        if not self.setState(State.MOVE):

            self.update_spritesheet(self.second_spritesheet)

            if (self.direction == Direction.SOUTH):
                self.current_frame = (self.current_frame) % (self.walk_length - 1) + 1
                self.collisions = []
                amount = self.delta * time
                try:
                    if self.y + amount > self.world_size[1] - Settings.tile_size:
                        raise OffScreenBottomException
                    else:
                        self.update(0)
                except:
                    pass
            else:
                self.direction = Direction.SOUTH
                self.current_frame = 0

    def attack_north(self, time):
        if not self.setState(State.MOVE):

            self.update_spritesheet(self.second_spritesheet)

            if (self.direction == Direction.NORTH):
                self.current_frame = (self.current_frame) % (self.walk_length - 1) + 1
                self.collisions = []
                amount = self.delta * time
                try:
                    if self.y + amount > self.world_size[1] - Settings.tile_size:
                        raise OffScreenBottomException
                    else:
                        self.update(0)
                except:
                    pass
            else:
                self.direction = Direction.NORTH
                self.current_frame = 0

    def attack_east(self, time):
        if not self.setState(State.MOVE):

            self.update_spritesheet(self.second_spritesheet)

            if (self.direction == Direction.EAST):
                self.current_frame = (self.current_frame) % (self.walk_length - 1) + 1
                self.collisions = []
                amount = self.delta * time
                try:
                    if self.y + amount > self.world_size[1] - Settings.tile_size:
                        raise OffScreenBottomException
                    else:
                        self.update(0)
                except:
                    pass
            else:
                self.direction = Direction.EAST
                self.current_frame = 0

    def attack_west(self, time):
        if not self.setState(State.MOVE):

            self.update_spritesheet(self.second_spritesheet)

            if (self.direction == Direction.WEST):
                self.current_frame = (self.current_frame) % (self.walk_length - 1) + 1
                self.collisions = []
                amount = self.delta * time
                try:
                    if self.y + amount > self.world_size[1] - Settings.tile_size:
                        raise OffScreenBottomException
                    else:
                        self.update(0)
                except:
                    pass
            else:
                self.direction = Direction.WEST
                self.current_frame = 0

    def distance(self, x1, y1, x2, y2):
        return math.sqrt(abs(math.pow(y2 - y1, 2) + math.pow(x2 - x1, 2)))

    def knockback(self):
        print("knockback")
        # if self.m_e_d:
        #     self.y = self.y - 50
        #     self.update(0)
        #     if len(self.collisions) != 0:
        #         self.y = self.y + 50
        #         self.update(0)
        #         self.collisions.clear()
        # if self.m_e_u:
        #     self.y = self.y + 50
        #     self.update(0)
        #     if len(self.collisions) != 0:
        #         self.y = self.y - 50
        #         self.update(0)
        #         self.collisions.clear()
        # if self.m_e_r:
        #     self.x = self.x - 50
        #     self.update(0)
        #     if len(self.collisions) != 0:
        #         self.x = self.x + 50
        #         self.update(0)
        #         self.collisions.clear()
        # if self.m_e_l:
        #     self.x = self.x + 50
        #     self.update(0)
        #     if len(self.collisions) != 0:
        #         self.x = self.x - 50
        #         self.update(0)
        #         self.collisions.clear()

    def update(self, time1):
        self.rect.x = self.x
        self.rect.y = self.y
        self.collisions = []
        self.current_sprite_set = self.state_sprites[self.state.value][self.direction.value]
        self.image = self.current_sprite_set[self.current_frame].image.convert_alpha()
        self.image = pygame.transform.scale(self.image, (64, 64))

        #divide fps by delta and state to step to next frame

        for sprite in self.blocks:
            self.collider.rect.x = sprite.x
            self.collider.rect.y = sprite.y
            if pygame.sprite.collide_rect(self, self.collider):
                self.collisions.append(sprite)

            # If player is within range to begin chase
            if self.distance(self.x, self.y, self.user.x, self.user.y) < 400:

                # Attack player
                if self.distance(self.x, self.y, self.user.x, self.user.y) < 25:

                    # Enemy can attack every 30 seconds
                    if (time.time() - self.last_attack) > .5:

                        self.last_attack = time.time()

                        self.m_e_d = False
                        self.m_e_u = False
                        self.m_e_r = False
                        self.m_e_l = False
                        self.m_e_i = False

                        pygame.time.set_timer(self.move_enemy_down, 0)
                        pygame.time.set_timer(self.move_enemy_right, 0)
                        pygame.time.set_timer(self.move_enemy_left, 0)
                        pygame.time.set_timer(self.move_enemy_up, 0)

                        # Attack left
                        if self.user.x < self.x:
                            pygame.time.set_timer(self.attack_enemy_east, 0)
                            pygame.time.set_timer(self.attack_enemy_north, 0)
                            pygame.time.set_timer(self.attack_enemy_south, 0)

                            pygame.time.set_timer(self.attack_enemy_west, 200)

                        # Attack down
                        elif self.user.y > self.y:
                            pygame.time.set_timer(self.attack_enemy_east, 0)
                            pygame.time.set_timer(self.attack_enemy_north, 0)
                            pygame.time.set_timer(self.attack_enemy_west, 0)

                            pygame.time.set_timer(self.attack_enemy_south, 200)

                        # Attack right
                        elif self.x < self.user.x:
                            pygame.time.set_timer(self.attack_enemy_west, 0)
                            pygame.time.set_timer(self.attack_enemy_south, 0)
                            pygame.time.set_timer(self.attack_enemy_north, 0)

                            pygame.time.set_timer(self.attack_enemy_east, 200)

                        # Attack up
                        else:
                            pygame.time.set_timer(self.attack_enemy_east, 0)
                            pygame.time.set_timer(self.attack_enemy_west, 0)
                            pygame.time.set_timer(self.attack_enemy_south, 0)

                            pygame.time.set_timer(self.attack_enemy_north, 200)

                        self.user.ouch()

                        if self.user.health <= 0:
                            self.user.x = -10000
                            self.user.y = -10000

                # Move along the y-axis
                elif self.x - 20 <= self.user.x <= self.x + 20:

                    # Move down
                    if self.y < self.user.y and not self.m_e_d:
                        pygame.time.set_timer(self.move_enemy_up, 0)
                        pygame.time.set_timer(self.move_enemy_right, 0)
                        pygame.time.set_timer(self.move_enemy_left, 0)
                        pygame.time.set_timer(self.attack_enemy_east, 0)
                        pygame.time.set_timer(self.attack_enemy_west, 0)
                        pygame.time.set_timer(self.attack_enemy_north, 0)
                        pygame.time.set_timer(self.attack_enemy_south, 0)

                        pygame.time.set_timer(self.move_enemy_down, 100)

                        self.m_e_d = True
                        self.m_e_u = False
                        self.m_e_r = False
                        self.m_e_l = False
                        self.m_e_i = False

                    # Move up
                    elif self.user.y < self.y and not self.m_e_u:
                        pygame.time.set_timer(self.move_enemy_down, 0)
                        pygame.time.set_timer(self.move_enemy_right, 0)
                        pygame.time.set_timer(self.move_enemy_left, 0)
                        pygame.time.set_timer(self.attack_enemy_east, 0)
                        pygame.time.set_timer(self.attack_enemy_west, 0)
                        pygame.time.set_timer(self.attack_enemy_north, 0)
                        pygame.time.set_timer(self.attack_enemy_south, 0)

                        pygame.time.set_timer(self.move_enemy_up, 100)

                        self.m_e_d = False
                        self.m_e_u = True
                        self.m_e_r = False
                        self.m_e_l = False
                        self.m_e_i = False

                else:
                    # If enemy is to the left of user, move right
                    if self.x - 200 < self.user.x < self.x and not self.m_e_l:
                        pygame.time.set_timer(self.move_enemy_up, 0)
                        pygame.time.set_timer(self.move_enemy_down, 0)
                        pygame.time.set_timer(self.move_enemy_right, 0)
                        pygame.time.set_timer(self.attack_enemy_east, 0)
                        pygame.time.set_timer(self.attack_enemy_west, 0)
                        pygame.time.set_timer(self.attack_enemy_north, 0)
                        pygame.time.set_timer(self.attack_enemy_south, 0)

                        pygame.time.set_timer(self.move_enemy_left, 100)

                        self.m_e_d = False
                        self.m_e_u = False
                        self.m_e_r = False
                        self.m_e_l = True
                        self.m_e_i = False

                    # If enemy is to the right of user, move left
                    elif self.x < self.user.x < self.x + 200 and not self.m_e_r:
                        pygame.time.set_timer(self.move_enemy_up, 0)
                        pygame.time.set_timer(self.move_enemy_down, 0)
                        pygame.time.set_timer(self.move_enemy_left, 0)
                        pygame.time.set_timer(self.attack_enemy_east, 0)
                        pygame.time.set_timer(self.attack_enemy_west, 0)
                        pygame.time.set_timer(self.attack_enemy_north, 0)
                        pygame.time.set_timer(self.attack_enemy_south, 0)

                        pygame.time.set_timer(self.move_enemy_right, 100)

                        self.m_e_d = False
                        self.m_e_u = False
                        self.m_e_r = True
                        self.m_e_l = False
                        self.m_e_i = False

            # Idle
            else:

                self.m_e_d = False
                self.m_e_u = False
                self.m_e_r = False
                self.m_e_l = False

                if not self.m_e_i:
                    pygame.time.set_timer(self.move_enemy_down, 0)
                    pygame.time.set_timer(self.move_enemy_right, 0)
                    pygame.time.set_timer(self.move_enemy_left, 0)
                    pygame.time.set_timer(self.move_enemy_up, 0)
                    pygame.time.set_timer(self.attack_enemy_east, 0)
                    pygame.time.set_timer(self.attack_enemy_west, 0)
                    pygame.time.set_timer(self.attack_enemy_north, 0)
                    pygame.time.set_timer(self.attack_enemy_south, 0)

                    self.move_idle(pygame.time)

                    self.m_e_i = True

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
