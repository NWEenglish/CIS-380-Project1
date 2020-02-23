import pygame
import sys
sys.path.append('..')
from league import *

class Melee_Weapon(Character):
    def __init__(self, z=0, x=0, y=0, engine=None, player=None):
        super().__init__(z, x, y)
        ## Melee sprites
        self.melee_sprites = []
        self.melee_length = 6
        self.attack_north = []
        self.attack_south = []
        self.attack_east = []
        self.attack_west = []

        self.direction = Direction.SOUTH

        self.image = None

        self.engine = engine

        self.player = player

        self.current_frame = 0

        raw_melee_sprites = Spritesheet('../assets/sword_slash.png', 192, self.melee_length)

        for i in range(self.melee_length):
            self.attack_north.append(raw_melee_sprites.sprites[i])
            self.attack_south.append(raw_melee_sprites.sprites[self.melee_length*2 + i])
            self.attack_east.append(raw_melee_sprites.sprites[self.melee_length*3 + i])
            self.attack_west.append(raw_melee_sprites.sprites[self.melee_length*1 + i])

        self.melee_sprites = [self.attack_north, self.attack_south, self.attack_east, self.attack_west]

        self.image = self.melee_sprites[1][self.direction.value].image.convert_alpha()
        self.image = pygame.transform.scale(self.image, (192,192))
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
        # self.collider = Drawable()
        # self.collider.image = pygame.Surface([Settings.tile_size, Settings.tile_size])
        # self.collider.rect = self.collider.image.get_rect()
        self.engine.collisions[self] = (self.engine.objects[1], self.enemy_take_damage)

    pass

    def update(self, time):
        pass
    def attack_update(self):
        self.rect.x = self.x
        self.rect.y = self.y
        self.collisions = []
        self.current_sprite_set = self.melee_sprites[self.direction.value]
        self.image = self.current_sprite_set[self.current_frame].image.convert_alpha()
        self.image = pygame.transform.scale(self.image, (192,192))
        for sprite in self.blocks:
            self.collider.rect.x= sprite.x
            self.collider.rect.y = sprite.y
            if pygame.sprite.collide_rect(self, self.collider):
                self.collisions.append(sprite)
                print(self.collisions)

    # Helper function to get a specific row of a spritesheet (offset)
    def get_sprite_set(self, sprite_source, tile_size, per_row, offset=0):
        rtn = []

        for i in range(per_row):
            rtn.append(sprite_source.sprites[offset*per_row + i])

        return rtn  

    def enemy_take_damage(self):
        print("enemy took damage")
        self.engine.objects[1].take_damage()
