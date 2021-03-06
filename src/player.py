#!/usr/bin/env python3

import pygame
import sys
from melee_weapon import Melee_Weapon
from arrow import Arrow
sys.path.append('..')
from league import *

class Player(Character):
    """This is a sample class for a player object.  A player
    is a character, is a drawable, and an updateable object.
    This class should handle everything a player does, such as
    moving, throwing/shooting, collisions, etc.  It was hastily
    written as a demo but should direction.
    """
    def __init__(self, engine, z=0, x=0, y=0):
        super().__init__(z, x, y)

        # Reference to the engine
        self.engine = engine

        # This unit's health
        self.health = 100
        # Last time I was hit
        self.last_hit = pygame.time.get_ticks()
        # A unit-less value.  Bigger is faster.
        self.delta = 256
        # Where the player is positioned
        self.x = x
        self.y = y

        # What state the object is in
        self.state = State.MOVE

        # The current direction the object is facing
        self.direction = Direction.SOUTH

        # What frame the object is in
        self.current_frame = 0

        # The objects melee weapon
        self.sword = Melee_Weapon(6,0,0, engine, self)

        self.arrow_image = pygame.image.load('../assets/arrow.png').convert_alpha()

        # Contains list of fired arrows in this scene
        self.arrows = []

        self.state_time = 0

        engine.key_events[pygame.K_a] = self.move_left
        engine.key_events[pygame.K_d] = self.move_right
        engine.key_events[pygame.K_w] = self.move_up
        engine.key_events[pygame.K_s] = self.move_down
        engine.key_events[pygame.K_s] = self.move_down
        engine.key_events[pygame.K_o] = self.melee
        engine.key_events[pygame.K_p] = self.range

        ## Walk sprites
        self.walk_length = 9
        raw_walk_sprites = Spritesheet('../assets/plate_walk.png', 64, self.walk_length)
        walk_north = self.get_sprite_set(raw_walk_sprites, 64, self.walk_length, offset=0)
        walk_west = self.get_sprite_set(raw_walk_sprites, 64, self.walk_length, offset=1)
        walk_south = self.get_sprite_set(raw_walk_sprites, 64, self.walk_length, offset=2)
        walk_east = self.get_sprite_set(raw_walk_sprites, 64, self.walk_length, offset=3)
        walk_sprites = [walk_north, walk_south, walk_east, walk_west] 

        ## Melee sprites
        self.melee_length = 6
        raw_melee_sprites = Spritesheet('../assets/plate_attack.png', 64, self.melee_length)
        attack_north = self.get_sprite_set(raw_melee_sprites, 64, self.melee_length, offset=0)
        attack_west = self.get_sprite_set(raw_melee_sprites, 64, self.melee_length, offset=1)
        attack_south = self.get_sprite_set(raw_melee_sprites, 64, self.melee_length, offset=2)
        attack_east = self.get_sprite_set(raw_melee_sprites, 64, self.melee_length, offset=3)    
        melee_sprites = [attack_north, attack_south, attack_east, attack_west]

        ## Ranged sprites
        self.ranged_length = 13
        raw_ranged_sprites = Spritesheet('../assets/plate_bow.png', 64, self.ranged_length)
        ranged_north = self.get_sprite_set(raw_ranged_sprites, 64, self.ranged_length, offset=0)
        ranged_west = self.get_sprite_set(raw_ranged_sprites, 64, self.ranged_length, offset=1)
        ranged_south = self.get_sprite_set(raw_ranged_sprites, 64, self.ranged_length, offset=2)
        ranged_east = self.get_sprite_set(raw_ranged_sprites, 64, self.ranged_length, offset=3) 
        ranged_sprites = [ranged_north, ranged_south, ranged_east, ranged_west]

        self.state_sprites = [walk_sprites, melee_sprites, ranged_sprites]

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
        self.collide_function = pygame.sprite.collide_rect
        self.collisions = []
        # For collision detection, we need to compare our sprite
        # with collideable sprites.  However, we have to remap
        # the collideable sprites coordinates since they change.
        # For performance reasons I created this sprite so we
        # don't have to create more memory each iteration of
        # collision detection.
        self.collider = Drawable()
        self.collider.image = pygame.Surface([12,12])
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

    def melee(self, time):
        self.sword.x = self.x - 64
        self.sword.y = self.y - 64
        self.sword.direction = self.direction
        self.sword.attack_update()
        if not self.setState(State.MELEE):
            self.current_frame = (self.current_frame + 1) % (self.melee_length)
            self.sword.current_frame = self.current_frame
            self.sword.attack_update()
        else:
            #self.engine.objects.append(self.sword)
            self.engine.drawables.add(self.sword)
        pass

        if (self.current_frame is 5):
            #arrow_noise = pygame.mixer.Sound("../assets/attack_noise.wav")
            #arrow_noise.play()
            pass


    def range(self, time):
        if not self.setState(State.RANGE):
            self.current_frame = (self.current_frame + 1) % (self.ranged_length)

            if (self.current_frame is 9):
                arrow = Arrow(self.arrow_image, self.direction, self.engine, 3,self.x + 31,self.y + 31)
                #arrow_noise = pygame.mixer.Sound("../assets/attack_noise.wav")
                #arrow_noise.play()

                self.arrows.append(arrow)

            if (self.current_frame is 12):
                self.current_frame = 3
        pass

    def update(self, time):
        self.state_time = self.state_time + 1
        self.reset_frame()
        self.rect.x = self.x
        self.rect.y = self.y
        self.collisions = []
        self.current_sprite_set = self.state_sprites[self.state.value][self.direction.value]
        self.image = self.current_sprite_set[self.current_frame].image.convert_alpha()
        self.image = pygame.transform.scale(self.image, (64, 64))

        #divide fps by delta and state to step to next frame

        for sprite in self.blocks:
            self.collider.rect.x= sprite.x
            self.collider.rect.y = sprite.y - 32
            if pygame.sprite.collide_rect(self, self.collider):
                self.collisions.append(sprite)
    def reset_frame(self):
        #time = pygame.time.get_ticks()
        if (self.state_time > 4):       
            self.current_frame = 0
            if (self.state == State.MELEE):
                self.sword.current_frame = 0
                self.sword.attack_update()

    def ouch(self):
        now = pygame.time.get_ticks()
        if now - self.last_hit > 1000:
            self.health = self.health - 10
            self.last_hit = now

    def setState(self, state):
        self.state_time = 0
        if (state is not State.MELEE and self.state is State.MELEE):
            #self.engine.objects.remove(self.sword)
            self.engine.drawables.remove(self.sword)

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

