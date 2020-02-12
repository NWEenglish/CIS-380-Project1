import pygame
import sys
sys.path.append('..')
import league
from trigger import Trigger
from league import *


class Screen(DUGameObject):
    """Creates all the world objects and passes them along with any collision methods
    to main to be drawn"""

    def __init__(self, user, g_engine):
        """Calls the first game screen and creates data structures to pass to update.
        user is the player class.
        g_engine is the league engine.
        door_x and door_y set the player position when moving between screens.
        drawables holds all the objects that will be placed on top of the tilemap.
        collisions holds tuples of objects and their corresponding method call
        blocking_object adds sprites to the player's block group.
        change_flag changes the screen in update() when true.
        add_flag adds sprites to overlay some added blocking sprite in update() (not being used).
        move_player_to_door moves the player to the last used door in update().
        last_drawables stores a list of objects draw from a screen to remove when changing.
        last_collisions stores a list of collision from a screen to remove when changing
        last_blocking_object list of blocking objects to remove
        now is the current time
        last_switch is the time the screen last changed
        sprites_utu is a sprite sheet from ProjectUtumno_full.png
        sprites_base is a sprite sheet from base_chip_pipo.png
        south_door_image is a flipped image used for all south doors
        background is a tilemap for covering white show through
        terrain is a tilemap for the basic terrain/full covering sprites
        detail is a tilemap for additional sprites that show whats under them
        world_size is how many tiles the .lvl says it has times the size league.Settings says
            the tiles are. Currently only used to set the player boundary and is set once
        set_screen_beach loads the first screen"""

        self.engine = g_engine
        self.user = user
        self.engine.drawables.add(self.user)

        self.door_x = 365
        self.door_y = 425

        self.drawables = []
        self.collisions = []
        self.blocking_object = pygame.sprite.Group()
        self.change_flag = True
        self.add_flag = False
        self.move_player_to_door = True

        self.last_drawables = []
        self.last_collisions = []
        self.last_blocking_objects = pygame.sprite.Group()

        self.now = pygame.time.get_ticks()
        self.last_switch = pygame.time.get_ticks() + 1000

        self.sprites_utu = league.Spritesheet('../assets/ProjectUtumno_full.png', league.Settings.tile_size, 64)
        self.sprites_base = league.Spritesheet('../assets/base_chip_pipo.png', league.Settings.tile_size, 8)
        self.south_door_image = pygame.transform.flip(self.sprites_utu.sprites[1094].image, 0, 1)
        self.background = league.Tilemap('../assets/blank.lvl', self.sprites_utu, layer=1)
        self.terrain = league.Tilemap('../assets/blank.lvl', self.sprites_utu, layer = 2)
        self.details = league.Tilemap('../assets/blank.lvl', self.sprites_utu, layer = 3)
        self.world_size = (self.terrain.wide*league.Settings.tile_size, self.terrain.high * league.Settings.tile_size)
        self.user.world_size = self.world_size
        self.set_screen_lost_woods_entrance()

    def make_north_door(self, next_screen):
        """Creates and places a trigger for the north door
         that loads the next screen at the connecting south door"""
        screen_trigger = Trigger(3, 352, 0)
        screen_trigger.image = self.sprites_utu.sprites[1094].image
        self.drawables.append(screen_trigger)
        self.collisions.append((screen_trigger, next_screen))

        screen_trigger = Trigger(3, 384, 0)
        screen_trigger.image = self.sprites_utu.sprites[1094].image
        self.drawables.append(screen_trigger)
        self.collisions.append((screen_trigger, next_screen))

    def make_south_door(self, next_screen):
        """Creates and places a trigger for the south door
         that loads the next screen at the connecting north door"""
        screen_trigger = Trigger(3, 352, 608)
        screen_trigger.image = self.south_door_image
        self.drawables.append(screen_trigger)
        self.collisions.append((screen_trigger, next_screen))

        screen_trigger = Trigger(3, 384, 608)
        screen_trigger.image = self.south_door_image
        self.drawables.append(screen_trigger)
        self.collisions.append((screen_trigger, next_screen))

    def make_east_door(self, next_screen):
        """Creates and places a trigger for the east door
            that loads the next screen at the connecting west door"""
        screen_trigger = Trigger(3, 768, 288)
        screen_trigger.image = self.sprites_utu.sprites[1086].image
        self.drawables.append(screen_trigger)
        self.collisions.append((screen_trigger, next_screen))

        screen_trigger = Trigger(3, 768, 320)
        screen_trigger.image = self.sprites_utu.sprites[1086].image
        self.drawables.append(screen_trigger)
        self.collisions.append((screen_trigger, next_screen))

    def make_west_door(self, next_screen):
        """Creates and places a trigger for the west door
            that loads the next screen at the connecting east door"""
        screen_trigger = Trigger(3, 0, 288)
        screen_trigger.image = self.sprites_utu.sprites[1096].image
        self.drawables.append(screen_trigger)
        self.collisions.append((screen_trigger, next_screen))

        screen_trigger = Trigger(3, 0, 320)
        screen_trigger.image = self.sprites_utu.sprites[1096].image
        self.drawables.append(screen_trigger)
        self.collisions.append((screen_trigger, next_screen))

    def use_door(self, x, y, screen):
        """Moves the player to the correct x and y for the new screen in update().
            screen is a method call to the next screen"""
        self.now = pygame.time.get_ticks()
        if self.now - self.last_switch > 1000:
            self.door_x = x
            self.door_y = y
            self.move_player_to_door = True
            self.last_switch = pygame.time.get_ticks()
            screen()

    def return_to_door(self):
        """Moves the player to the last entered door in update()"""
        self.move_player_to_door = True

    def update(self, gameDeltaTime):
        """Changes screens and adds or move objects while on a screen"""

        if self.change_flag:
            "Allows screen changes only after a set_screen() is called not every frame"
            for d in self.last_drawables:
                "Removes the last screen's drawables"
                self.engine.drawables.remove(d)
            for c in self.last_collisions:
                "Removes the last screen's collisions"
                self.engine.collisions.pop(c[0])
            
            self.user.blocks.empty()
            self.user.blocks.add(self.terrain.impassable)
            self.user.blocks.add(self.details.impassable)
            self.user.blocks.add(self.blocking_object)
            self.last_blocking_objects = self.blocking_object.copy()
            self.blocking_object.empty()

            for d in self.drawables:
                "Sets the current screen's drawables"
                self.engine.drawables.add(d)

            for c in self.collisions:
                "Sets the current screen's collisions"
                self.engine.collisions[c[0]] = (self.user, c[1])

            self.change_flag = False
            self.last_drawables = self.drawables.copy()
            self.drawables.clear()
            self.last_collisions = self.collisions.copy()
            self.collisions.clear()

        if self.add_flag:
            "Adds an object to allow passage"
            "ToDo add object to block passage"
            self.user.blocks.remove(self.last_blocking_objects)
            for d in self.drawables:
                self.engine.drawables.add(d)
                self.last_drawables.append(d)
            self.drawables.clear()

        if self.move_player_to_door:
            "Moves the player to the last used door"
            self.user.x = self.door_x
            self.user.y = self.door_y
            self.move_player_to_door = False




    def beach_door_north(self):
        "Creates the north entrance for beach"
        self.use_door(365, 40, self.set_screen_beach)

    def set_screen_beach(self):
        "Creates the beach screen"
        self.terrain = league.Tilemap('../assets/beach.lvl', self.sprites_utu, layer=1)
        self.details = league.Tilemap('../assets/beach_details.lvl', self.sprites_utu, layer=2)
        self.drawables.append(self.terrain.passable.sprites())
        self.drawables.append(self.details.passable.sprites())

        "Creates a trigger that loads 'hills' at the south door"
        self.make_north_door(self.grassland_door_south)

        "Sets update() to change screens"
        self.change_flag = True




    def grassland_door_north(self):
        "Creates the north entrance for grassland"
        self.use_door(365, 40, self.set_screen_grassland)

    def grassland_door_south(self):
        "creates the south entrance for grassland"
        self.use_door(365, 500, self.set_screen_grassland)

    def set_screen_grassland(self):
        """Creates 'grasslands' screen"""
        self.terrain = league.Tilemap('../assets/grassland.lvl', self.sprites_utu, layer=1)
        self.drawables.append(self.terrain.passable.sprites())

        "Loads north door sprites leading to 'cliffs' south door"
        self.make_north_door(self.cliffs_door_south)

        "Loads south door sprites leading to 'beach' north door"
        self.make_south_door(self.beach_door_north)

        "Sets update() to change screens"
        self.change_flag = True




    def cliffs_door_south(self):
        self.use_door(365, 500, self.set_screen_cliffs)

    def cliffs_door_north(self):
        self.use_door(365, 40, self.set_screen_cliffs)

    def make_bridge(self):
        "Creates the bridge once the player triggers it"
        self.now = pygame.time.get_ticks()
        if self.now - self.last_switch > 1000:
            self.add_flag = True
            bridge = []
            for i in range(3):
                for j in range(6):
                    bridge.append(league.DUGameObject)
                    bridge[i + j] = Trigger(3, 352 + (32 * i), 160 + (32 * j))
                    bridge[i + j].image = self.sprites_base.sprites[248].image
                    self.drawables.append(bridge[i+j])
            self.last_switch = pygame.time.get_ticks()

    def set_screen_cliffs(self):
        """Creates 'cliffs' screen"""
        self.background = league.Tilemap('../assets/cliffs_background.lvl', self.sprites_utu, layer=1)
        self.terrain = league.Tilemap('../assets/cliffs_terrain.lvl', self.sprites_base, layer=2)
        self.details = league.Tilemap('../assets/cliffs_details.lvl', self.sprites_utu, layer=3)
        self.drawables.append(self.background.passable.sprites())
        self.drawables.append(self.terrain.passable.sprites())
        self.drawables.append(self.details.passable.sprites())

        "Loads north door sprites leading to 'lost woods entrance' south door"
        self.make_north_door(self.lost_woods_entrance_door_south)

        "Loads south door sprites leading to 'hills' north door"
        self.make_south_door(self.grassland_door_north)

        "Loads the switch sprite for the bridge"
        bridge_switch = Trigger(3, 500, 480)
        bridge_switch.image = self.sprites_base.sprites[70].image
        self.drawables.append(bridge_switch)
        self.collisions.append((bridge_switch, self.make_bridge))

        bridge_switch = Trigger(3, 500, 50)
        bridge_switch.image = self.sprites_base.sprites[70].image
        self.drawables.append(bridge_switch)
        self.collisions.append((bridge_switch, self.make_bridge))

        "Makes the area where the bridge will be impassable. Removed by make_bridge to make passable"
        bridge_block = []
        for i in range(3):
            for j in range(6):
                bridge_block.append(league.DUGameObject)
                bridge_block[i + j] = Trigger(1, 352 + (32 * i), 160 + (32 * j))
                bridge_block[i + j].image = self.sprites_base.sprites[97].image
                self.drawables.append(bridge_block[i + j])
                self.collisions.append((bridge_block[i+j], self.return_to_door))

        "Sets update() to change screens"
        self.change_flag = True


    def lost_woods_entrance_door_north(self):
        self.use_door(365, 40, self.set_screen_lost_woods_entrance)

    def lost_woods_entrance_door_south(self):
        self.use_door(365, 500, self.set_screen_lost_woods_entrance)

    def lost_woods_entrance_door_east(self):
        self.use_door(718, 304, self.set_screen_lost_woods_entrance)

    def lost_woods_entrance_door_west(self):
        self.use_door(50, 304, self.set_screen_lost_woods_entrance)

    def set_screen_lost_woods_entrance(self):
        """Creates 'lost wood entrance screen"""
        self.terrain = league.Tilemap('../assets/lost_woods_terrain.lvl', self.sprites_base, layer=1)
        self.details = league.Tilemap('../assets/lost_woods_entrance_details.lvl', self.sprites_base, layer=2)
        self.drawables.append(self.terrain.passable.sprites())
        self.drawables.append(self.details.passable.sprites())

        self.make_north_door(self.lost_woods_entrance_door_south)
        self.make_east_door(self.lost_woods_2_door_west)
        self.make_west_door(self.lost_woods_entrance_door_east)
        self.make_south_door(self.cliffs_door_north)

        "Sets update() to change screens"
        self.change_flag = True



    def lost_woods_2_door_west(self):
        self.use_door(50, 304, self.set_screen_lost_woods_2)

    def set_screen_lost_woods_2(self):
        self.terrain = league.Tilemap('assets/lost_woods_terrain.lvl', self.sprites_base, layer=1)
        self.details = league.Tilemap('../assets/lost_woods_summer_details.lvl', self.sprites_base, layer=2)
        self.drawables.append(self.terrain.passable.sprites())
        self.drawables.append(self.details.passable.sprites())

        self.make_north_door(self.lost_woods_3_door_south)
        self.make_east_door(self.lost_woods_entrance_door_west)
        self.make_west_door(self.lost_woods_entrance_door_east)
        self.make_south_door(self.lost_woods_entrance_door_north)

        "Sets update() to change screens"
        self.change_flag = True



    def lost_woods_3_door_south(self):
        self.use_door(365, 500, self.set_screen_lost_woods_3)

    def set_screen_lost_woods_3(self):
        self.terrain = league.Tilemap('assets/lost_woods_terrain.lvl', self.sprites_base, layer=1)
        self.details = league.Tilemap('../assets/lost_woods_fall_details.lvl', self.sprites_base, layer=2)
        self.drawables.append(self.terrain.passable.sprites())
        self.drawables.append(self.details.passable.sprites())

        self.make_north_door(self.lost_woods_entrance_door_south)
        self.make_east_door(self.lost_woods_entrance_door_west)
        self.make_west_door(self.lost_woods_4_door_east)
        self.make_south_door(self.lost_woods_entrance_door_north)

        "Sets update() to change screens"
        self.change_flag = True


    def lost_woods_4_door_east(self):
        self.use_door(718, 340, self.set_screen_lost_woods_4)

    def set_screen_lost_woods_4(self):
        self.terrain = league.Tilemap('assets/lost_woods_terrain.lvl', self.sprites_base, layer=1)
        self.details = league.Tilemap('../assets/lost_woods_winter_details.lvl', self.sprites_base, layer=2)
        self.drawables.append(self.terrain.passable.sprites())
        self.drawables.append(self.details.passable.sprites())

        self.make_north_door(self.lost_woods_entrance_door_south)
        self.make_east_door(self.lost_woods_entrance_door_west)
        self.make_west_door(self.lost_woods_entrance_door_east)
        self.make_south_door(self.lost_woods_entrance_door_north)

        "Sets update() to change screens"
        self.change_flag = True