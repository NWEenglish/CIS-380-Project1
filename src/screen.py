import pygame
import sys
sys.path.append('..')
import league
from trigger import Trigger
from league import *
from Enemy import Enemy


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

        self.door_x = 300
        self.door_y = 255

        self.drawables = []
        self.collisions = []
        self.objects = []
        self.blocking_object = pygame.sprite.Group()
        self.change_flag = True
        self.add_flag = False
        self.move_player_to_door = True
        self.terrain_switch_flag = False
        self.boss_door_east_flag = False
        self.boss_door_west_flag = False

        self.last_drawables = []
        self.last_collisions = []
        self.last_objects = []
        self.last_blocking_objects = pygame.sprite.Group()
        self.switching_objects = []
        self.switching_collision_list = []
        self.last_switching_collision_list = []
        self.enemy_list = []

        self.now = pygame.time.get_ticks()
        self.last_switch = pygame.time.get_ticks() + 1000
        self.next_terrain_switch_time = 0
        self.switch_interval = 0
        self.path_count = 0
        self.current_path = 0
        self.last_path = -1

        self.sprites_utu = league.Spritesheet('../assets/ProjectUtumno_full.png', league.Settings.tile_size, 64)
        self.sprites_base = league.Spritesheet('../assets/base_chip_pipo.png', league.Settings.tile_size, 8)
        self.south_door_image = pygame.transform.flip(self.sprites_utu.sprites[1094].image, 0, 1)
        self.background = league.Tilemap('../assets/blank.lvl', self.sprites_utu, layer=1)
        self.terrain = league.Tilemap('../assets/blank.lvl', self.sprites_utu, layer = 2)
        self.details = league.Tilemap('../assets/blank.lvl', self.sprites_utu, layer = 3)
        self.world_size = (self.terrain.wide*league.Settings.tile_size, self.terrain.high * league.Settings.tile_size)
        self.user.world_size = self.world_size
        self.set_screen_beach()

    def make_door_custom(self, x, y, image, next_screen):
        screen_trigger = Trigger(3, x, y)
        screen_trigger.image = image
        self.drawables.append(screen_trigger)
        self.collisions.append((screen_trigger, next_screen))

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
        if self.now - self.last_switch > 100:
            self.door_x = x
            self.door_y = y
            self.move_player_to_door = True
            self.last_switch = pygame.time.get_ticks()
            self.terrain_switch_flag = False
            screen()

    def start_switching(self):
        self.now = pygame.time.get_ticks()
        if self.now - self.last_switch > 100:
            self.terrain_switch_flag = True
            self.last_switch = pygame.time.get_ticks()


    def return_to_door(self):
        """Moves the player to the last entered door in update()"""
        self.move_player_to_door = True
        self.user.ouch()

    def make_collision(self, image, starting_x, x_copies, starting_y, y_copies, function):
        for x in range(x_copies):
            for y in range(y_copies):
                collision = Trigger(3, (starting_x*32) + (32*x), (starting_y*32) + (32*y))
                collision.image = image
                self.drawables.append(collision)
                self.collisions.append((collision, function))

    def make_switch_collision(self, switch_group, image, starting_x, x_copies, starting_y, y_copies, function):
        for x in range(x_copies):
            for y in range(y_copies):
                path_piece = Trigger(4, (starting_x*32) + (x*32), (starting_y*32) +(y*32))
                path_piece.image = image
                switch_group[0].add(path_piece)
                switch_group[1].append((path_piece, function))

    def update(self, gameDeltaTime):
        """Changes screens and adds or move objects while on a screen"""

        if self.change_flag:
            "Allows screen changes only after a set_screen*() is called not every frame"
            self.update_screen()

        if self.add_flag:
            "Adds an object to allow passage"
            "ToDo add object to block passage"
            self.user.blocks.remove(self.last_blocking_objects)
            for d in self.drawables:
                self.engine.drawables.add(d)
                self.last_drawables.append(d)
            self.drawables.clear()
            self.add_flag = False

        if self.move_player_to_door:
            "Moves the player to the set door"
            self.user.x = self.door_x
            self.user.y = self.door_y
            self.move_player_to_door = False

        if self.terrain_switch_flag:
            if self.next_terrain_switch_time > self.switch_interval:
                self.terrain_switching()
                self.next_terrain_switch_time = 0
            self.next_terrain_switch_time = self.next_terrain_switch_time + gameDeltaTime

        if self.user.health <= 0:
            self.engine.events[pygame.QUIT](0)

    def update_screen(self):
        self.last_drawables.append(self.user.arrows)
        for d in self.last_drawables:
            "Removes the last screen's drawables"
            self.engine.drawables.remove(d)
        for c in self.last_collisions:
            "Removes the last screen's collisions"
            self.engine.collisions.pop(c[0])
        for o in self.last_objects:
            "Removes the last screen's objects"
            self.engine.objects.remove(o)

        self.user.blocks.empty()
        for e in self.enemy_list:
            e.blocks.add(self.terrain.impassable)
            e.blocks.add(self.details.impassable)
            e.blocks.add(self.blocking_object)
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

        for o in self.objects:
            self.engine.objects.append(o)

        self.change_flag = False
        self.last_drawables = self.drawables.copy()
        self.drawables.clear()
        self.last_collisions = self.collisions.copy()
        self.collisions.clear()
        self.last_objects = self.objects.copy()
        self.objects.clear()
        self.enemy_list.clear()

    def terrain_switching(self):
        if self.last_path >= 0:
            self.engine.drawables.remove(self.switching_objects[self.last_path])
            self.last_drawables.remove(self.switching_objects[self.last_path])

        self.current_path = self.path_count % len(self.switching_objects)
        self.path_count = self.path_count + 1
        self.last_path = self.current_path

        for c in self.last_switching_collision_list:
            self.engine.collisions.pop(c[0])
            self.last_collisions.remove(c)

        self.engine.drawables.add(self.switching_objects[self.current_path])
        self.last_drawables.append(self.switching_objects[self.current_path])
        for c in self.switching_collision_list[self.current_path]:
            self.engine.collisions[c[0]] = (self.user, c[1])
            self.last_collisions.append(c)

        self.last_switching_collision_list = self.switching_collision_list[self.current_path].copy()

    def terrain_switching_clean_up(self):
        self.switching_objects.clear()
        self.switching_collision_list.clear()
        self.last_switching_collision_list.clear()
        self.path_count = 0
        self.last_path = -1
        self.current_path = 0

    def beach_door_north(self):
        "Creates the north entrance for beach"
        self.use_door(365, 40, self.set_screen_beach)

    def set_screen_beach(self):
        "Creates the beach screen"
        self.terrain = league.Tilemap('../assets/beach_terrain.lvl', self.sprites_utu, layer=1)
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
        self.terrain = league.Tilemap('../assets/grassland_terrain.lvl', self.sprites_utu, layer=1)
        self.details = league.Tilemap('../assets/blank.lvl', self.sprites_utu, layer=2)
        self.drawables.append(self.terrain.passable.sprites())

        "Loads north door sprites leading to 'cliffs' south door"
        self.make_north_door(self.cliffs_door_south)

        "Loads south door sprites leading to 'beach' north door"
        self.make_south_door(self.beach_door_north)

        enemy = Enemy(self.engine, self.user, "../assets/imp - walk - vanilla.png",
                      "../assets/imp - attack - vanilla.png", 100, 10, 200, 200)
        self.enemy_list.append(enemy)
        self.objects.append(enemy)
        self.drawables.append(enemy)
        self.collisions.append((enemy, enemy.knockback))

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
            for j in range(7):
                bridge_block.append(league.DUGameObject)
                bridge_block[i + j] = Trigger(1, 352 + (32 * i), 128 + (32 * j))
                bridge_block[i + j].image = self.sprites_base.sprites[97].image
                self.drawables.append(bridge_block[i + j])
                self.blocking_object.add(bridge_block[i+j])
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

        enemy = Enemy(self.engine, self.user, "../assets/imp - walk - vanilla.png",
                      "../assets/imp - attack - vanilla.png", 100, 10, 200, 200)
        self.enemy_list.append(enemy)
        self.objects.append(enemy)
        self.drawables.append(enemy)
        self.collisions.append((enemy, enemy.knockback))

        "Sets update() to change screens"
        self.change_flag = True



    def lost_woods_2_door_west(self):
        self.use_door(50, 304, self.set_screen_lost_woods_2)

    def set_screen_lost_woods_2(self):
        self.terrain = league.Tilemap('../assets/lost_woods_terrain.lvl', self.sprites_base, layer=1)
        self.details = league.Tilemap('../assets/lost_woods_summer_details.lvl', self.sprites_base, layer=2)
        self.drawables.append(self.terrain.passable.sprites())
        self.drawables.append(self.details.passable.sprites())

        self.make_north_door(self.lost_woods_3_door_south)
        self.make_east_door(self.lost_woods_entrance_door_west)
        self.make_west_door(self.lost_woods_entrance_door_east)
        self.make_south_door(self.lost_woods_entrance_door_north)

        enemy = Enemy(self.engine, self.user, "../assets/imp - walk - vanilla.png",
                      "../assets/imp - attack - vanilla.png", 100, 10, 200, 200)
        self.enemy_list.append(enemy)
        self.objects.append(enemy)
        self.drawables.append(enemy)
        self.collisions.append((enemy, enemy.knockback))

        "Sets update() to change screens"
        self.change_flag = True



    def lost_woods_3_door_south(self):
        self.use_door(365, 500, self.set_screen_lost_woods_3)

    def set_screen_lost_woods_3(self):
        self.terrain = league.Tilemap('../assets/lost_woods_terrain.lvl', self.sprites_base, layer=1)
        self.details = league.Tilemap('../assets/lost_woods_fall_details.lvl', self.sprites_base, layer=2)
        self.drawables.append(self.terrain.passable.sprites())
        self.drawables.append(self.details.passable.sprites())

        self.make_north_door(self.lost_woods_entrance_door_south)
        self.make_east_door(self.lost_woods_entrance_door_west)
        self.make_west_door(self.lost_woods_4_door_east)
        self.make_south_door(self.lost_woods_entrance_door_north)

        enemy = Enemy(self.engine, self.user, "../assets/imp - walk - vanilla.png",
                      "../assets/imp - attack - vanilla.png", 100, 10, 200, 200)
        self.enemy_list.append(enemy)
        self.objects.append(enemy)
        self.drawables.append(enemy)
        self.collisions.append((enemy, enemy.knockback))

        "Sets update() to change screens"
        self.change_flag = True


    def lost_woods_4_door_east(self):
        self.use_door(718, 340, self.set_screen_lost_woods_4)

    def set_screen_lost_woods_4(self):
        self.terrain = league.Tilemap('../assets/lost_woods_terrain.lvl', self.sprites_base, layer=1)
        self.details = league.Tilemap('../assets/lost_woods_summer_details.lvl', self.sprites_base, layer=2)
        self.drawables.append(self.terrain.passable.sprites())
        self.drawables.append(self.details.passable.sprites())

        self.make_north_door(self.lost_woods_5_door_south)
        self.make_east_door(self.lost_woods_entrance_door_west)
        self.make_west_door(self.lost_woods_entrance_door_east)
        self.make_south_door(self.lost_woods_entrance_door_north)

        enemy = Enemy(self.engine, self.user, "../assets/imp - walk - vanilla.png",
                      "../assets/imp - attack - vanilla.png", 100, 10, 200, 200)
        self.enemy_list.append(enemy)
        self.objects.append(enemy)
        self.drawables.append(enemy)
        self.collisions.append((enemy, enemy.knockback))

        "Sets update() to change screens"
        self.change_flag = True

    def lost_woods_5_door_south(self):
        self.use_door(365, 500, self.set_screen_lost_woods_5)

    def set_screen_lost_woods_5(self):
        self.terrain = league.Tilemap('../assets/lost_woods_terrain.lvl', self.sprites_base, layer=1)
        self.details = league.Tilemap('../assets/lost_woods_fall_details.lvl', self.sprites_base, layer=2)
        self.drawables.append(self.terrain.passable.sprites())
        self.drawables.append(self.details.passable.sprites())

        self.make_north_door(self.lost_woods_entrance_door_south)
        self.make_east_door(self.lost_woods_entrance_door_west)
        self.make_west_door(self.lost_woods_6_door_east)
        self.make_south_door(self.lost_woods_entrance_door_north)

        enemy = Enemy(self.engine, self.user, "../assets/imp - walk - vanilla.png",
                      "../assets/imp - attack - vanilla.png", 100, 10, 200, 200)
        self.enemy_list.append(enemy)
        self.objects.append(enemy)
        self.drawables.append(enemy)
        self.collisions.append((enemy, enemy.knockback))

        self.change_flag = True

    def lost_woods_6_door_east(self):
        self.use_door(718, 340, self.set_screen_lost_woods_6)

    def set_screen_lost_woods_6(self):
        self.terrain = league.Tilemap('../assets/lost_woods_terrain.lvl', self.sprites_base, layer=1)
        self.details = league.Tilemap('../assets/lost_woods_winter_details.lvl', self.sprites_base, layer=2)
        self.drawables.append(self.terrain.passable.sprites())
        self.drawables.append(self.details.passable.sprites())

        self.make_north_door(self.lost_woods_entrance_door_south)
        self.make_east_door(self.lost_woods_entrance_door_west)
        self.make_west_door(self.lost_woods_entrance_door_east)
        self.make_south_door(self.lost_woods_7_door_north)

        enemy = Enemy(self.engine, self.user, "../assets/imp - walk - vanilla.png",
                      "../assets/imp - attack - vanilla.png", 100, 10, 200, 200)
        self.enemy_list.append(enemy)
        self.objects.append(enemy)
        self.drawables.append(enemy)
        self.collisions.append((enemy, enemy.knockback))

        self.change_flag = True

    def lost_woods_7_door_north(self):
        self.use_door(365, 40, self.set_screen_lost_woods_7)

    def set_screen_lost_woods_7(self):
        self.terrain = league.Tilemap('../assets/lost_woods_terrain.lvl', self.sprites_base, layer=1)
        self.details = league.Tilemap('../assets/lost_woods_winter_details.lvl', self.sprites_base, layer=2)
        self.drawables.append(self.terrain.passable.sprites())
        self.drawables.append(self.details.passable.sprites())

        self.make_north_door(self.lost_woods_entrance_door_south)
        self.make_east_door(self.lost_woods_entrance_door_west)
        self.make_west_door(self.lost_woods_entrance_door_east)
        self.make_south_door(self.lost_woods_8_door_north)

        enemy = Enemy(self.engine, self.user, "../assets/imp - walk - vanilla.png",
                      "../assets/imp - attack - vanilla.png", 100, 10, 200, 200)
        self.enemy_list.append(enemy)
        self.objects.append(enemy)
        self.drawables.append(enemy)
        self.collisions.append((enemy, enemy.knockback))

        self.change_flag = True

    def lost_woods_8_door_north(self):
        self.use_door(365, 40, self.set_screen_lost_woods_8)

    def set_screen_lost_woods_8(self):
        self.terrain = league.Tilemap('../assets/lost_woods_terrain.lvl', self.sprites_base, layer=1)
        self.details = league.Tilemap('../assets/lost_woods_spring_details.lvl', self.sprites_base, layer=2)
        self.drawables.append(self.terrain.passable.sprites())
        self.drawables.append(self.details.passable.sprites())

        self.make_north_door(self.lost_woods_entrance_door_south)
        self.make_east_door(self.lost_woods_9_door_west)
        self.make_west_door(self.lost_woods_entrance_door_east)
        self.make_south_door(self.lost_woods_entrance_door_north)

        enemy = Enemy(self.engine, self.user, "../assets/imp - walk - vanilla.png",
                      "../assets/imp - attack - vanilla.png", 100, 10, 200, 200)
        self.enemy_list.append(enemy)
        self.objects.append(enemy)
        self.drawables.append(enemy)
        self.collisions.append((enemy, enemy.knockback))

        self.change_flag = True

    def lost_woods_9_door_west(self):
        self.use_door(50, 304, self.set_screen_lost_woods_9)

    def set_screen_lost_woods_9(self):
        self.terrain = league.Tilemap('../assets/lost_woods_terrain.lvl', self.sprites_base, layer=1)
        self.details = league.Tilemap('../assets/lost_woods_summer_details.lvl', self.sprites_base, layer=2)
        self.drawables.append(self.terrain.passable.sprites())
        self.drawables.append(self.details.passable.sprites())

        self.make_north_door(self.castle_exterior_door_south)
        self.make_east_door(self.lost_woods_entrance_door_west)
        self.make_west_door(self.lost_woods_entrance_door_east)
        self.make_south_door(self.lost_woods_entrance_door_north)

        enemy = Enemy(self.engine, self.user, "../assets/imp - walk - vanilla.png",
                      "../assets/imp - attack - vanilla.png", 100, 10, 200, 200)
        self.enemy_list.append(enemy)
        self.objects.append(enemy)
        self.drawables.append(enemy)
        self.collisions.append((enemy, enemy.knockback))

        self.change_flag = True


    def castle_exterior_door_south(self):
        self.use_door(365, 500, self.set_screen_castle_exterior)

    def set_screen_castle_exterior(self):
        self.terrain = league.Tilemap('../assets/castle_exterior_terrain.lvl', self.sprites_utu, layer=1)
        self.details = league.Tilemap('../assets/castle_exterior_details.lvl', self.sprites_utu, layer=2)
        self.drawables.append(self.terrain.passable.sprites())
        self.drawables.append(self.details.passable.sprites())

        self.make_door_custom(352, 384, self.south_door_image, self.castle_entrance_door_south)
        self.make_south_door(self.lost_woods_entrance_door_north)

        self.change_flag = True

    def castle_entrance_door_south(self):
        self.use_door(365, 500, self.set_screen_castle_entrance)

    def castle_entrance_door_north(self):
        self.use_door(365, 40, self.set_screen_castle_entrance)

    def set_screen_castle_entrance(self):
        self.terrain_switching_clean_up()
        self.terrain = league.Tilemap('../assets/castle_entrance_terrain.lvl', self.sprites_utu, layer=1)
        self.details = league.Tilemap('../assets/castle_entrance_details.lvl', self.sprites_utu, layer=2)
        self.drawables.append(self.terrain.passable.sprites())
        self.drawables.append(self.details.passable.sprites())
        self.next_terrain_switch_time = 1
        self.switch_interval = 2

        self.make_south_door(self.castle_exterior_door_south)
        self.make_north_door(self.castle_fork_door_south)

        self.make_collision(self.sprites_utu.sprites[384].image, 0, 3, 0, 14, self.return_to_door)
        self.make_collision(self.sprites_utu.sprites[384].image, 22, 3, 0, 14, self.return_to_door)
        self.make_collision(self.sprites_utu.sprites[918].image, 3, 19, 13, 1, self.start_switching)

        switch_sprites_1 = pygame.sprite.Group()
        switch_collision_1 = []
        spear_flip = pygame.transform.flip(self.sprites_utu.sprites[5751].image, 1, 0)
        self.make_switch_collision((switch_sprites_1, switch_collision_1), self.sprites_utu.sprites[5751].image,
                                   3, 19, 0, 3, self.return_to_door)
        self.make_switch_collision((switch_sprites_1, switch_collision_1), spear_flip,
                                   3, 19, 0, 3, self.return_to_door)
        self.switching_objects.append(switch_sprites_1)
        self.switching_collision_list.append(switch_collision_1)

        switch_sprites_2 = pygame.sprite.Group()
        switch_collision_2 = []
        self.make_switch_collision((switch_sprites_2, switch_collision_2), self.sprites_utu.sprites[5751].image,
                                   3, 19, 3, 3, self.return_to_door)
        self.make_switch_collision((switch_sprites_2, switch_collision_2), spear_flip,
                                   3, 19, 3, 3, self.return_to_door)
        self.switching_objects.append(switch_sprites_2)
        self.switching_collision_list.append(switch_collision_2)

        switch_sprites_3 = pygame.sprite.Group()
        switch_collision_3 = []
        self.make_switch_collision((switch_sprites_3, switch_collision_3), self.sprites_utu.sprites[5751].image,
                                   3, 19, 9, 3, self.return_to_door)
        self.make_switch_collision((switch_sprites_3, switch_collision_3), spear_flip,
                                   3, 19, 9, 3, self.return_to_door)
        self.switching_objects.append(switch_sprites_3)
        self.switching_collision_list.append(switch_collision_3)

        self.change_flag = True

    def castle_fork_door_south(self):
        self.use_door(365, 500, self.set_screen_castle_fork)

    def castle_fork_door_east(self):
        self.use_door(718, 300, self.set_screen_castle_fork)

    def castle_fork_door_west(self):
        self.use_door(50, 300, self.set_screen_castle_fork)


    def set_screen_castle_fork(self):
        self.terrain_switching_clean_up()
        self.terrain = league.Tilemap('../assets/castle_terrain.lvl', self.sprites_utu, layer=1)
        self.details = league.Tilemap('../assets/castle_fork_details.lvl', self.sprites_utu, layer=2)
        self.drawables.append(self.terrain.passable.sprites())
        self.drawables.append(self.details.passable.sprites())
        self.next_terrain_switch_time = 3
        self.switch_interval = 3
        self.terrain_switch_flag = True

        self.make_south_door(self.castle_entrance_door_north)
        self.make_east_door(self.castle_east_wing_door_west)
        self.make_west_door(self.castle_west_wing_door_east)

        if self.boss_door_west_flag:
            lit_torch = Trigger(5, 256, 0)
            lit_torch.image = self.sprites_utu.sprites[47].image
            torch_base = Trigger(4, 256, 0)
            torch_base.image = self.sprites_utu.sprites[1203].image
            self.drawables.append(torch_base)
            self.drawables.append(lit_torch)
        else:
            unlit_torch = Trigger(5, 256, 0)
            unlit_torch.image = self.sprites_utu.sprites[21].image
            torch_base = Trigger(4, 256, 0)
            torch_base.image = self.sprites_utu.sprites[1203].image
            self.drawables.append(torch_base)
            self.drawables.append(unlit_torch)

        if self.boss_door_east_flag:
            lit_torch = Trigger(5, 512, 0)
            lit_torch.image = self.sprites_utu.sprites[47].image
            torch_base = Trigger(4, 512, 0)
            torch_base.image = self.sprites_utu.sprites[1203].image
            self.drawables.append(torch_base)
            self.drawables.append(lit_torch)
        else:
            unlit_torch = Trigger(5, 512, 0)
            unlit_torch.image = self.sprites_utu.sprites[21].image
            torch_base = Trigger(4, 512, 0)
            torch_base.image = self.sprites_utu.sprites[1203].image
            self.drawables.append(torch_base)
            self.drawables.append(unlit_torch)

        if self.boss_door_east_flag and self.boss_door_west_flag:
            self.make_north_door(self.castle_boss_room_south_door)
            door_left = Trigger(4, 352, 0)
            door_left.image = self.sprites_utu.sprites[106].image
            self.drawables.append(door_left)
            door_right = Trigger(4, 384, 0)
            door_right.image = self.sprites_utu.sprites[108].image
            self.drawables.append(door_right)
        else:
            door_left = Trigger(3, 352, 0)
            door_left.image = self.sprites_utu.sprites[103].image
            self.drawables.append(door_left)
            self.blocking_object.add(door_left)
            door_right = Trigger(3, 384, 0)
            door_right.image = self.sprites_utu.sprites[105].image
            self.drawables.append(door_right)
            self.blocking_object.add(door_right)

        self.make_collision(self.sprites_utu.sprites[384].image, 0, 10, 0, 7, self.return_to_door)
        self.make_collision(self.sprites_utu.sprites[384].image, 15, 10, 0, 7, self.return_to_door)
        self.make_collision(self.sprites_utu.sprites[384].image, 0, 10, 13, 10, self.return_to_door)
        self.make_collision(self.sprites_utu.sprites[384].image, 15, 10, 13, 10, self.return_to_door)

        left_top_right_sprite = pygame.sprite.Group()
        left_top_right_collisions = []
        self.make_switch_collision((left_top_right_sprite, left_top_right_collisions),
                                   self.sprites_utu.sprites[384].image, 4, 3, 3, 11, self.return_to_door)

        self.make_switch_collision((left_top_right_sprite, left_top_right_collisions),
                                   self.sprites_utu.sprites[384].image, 3, 19, 3, 3, self.return_to_door)

        self.make_switch_collision((left_top_right_sprite, left_top_right_collisions),
                                   self.sprites_utu.sprites[384].image, 15, 3, 7, 7, self.return_to_door)
        self.switching_objects.append(left_top_right_sprite)
        self.switching_collision_list.append(left_top_right_collisions)

        top_right_left_sprite = pygame.sprite.Group()
        top_right_left_collisions = []
        self.make_switch_collision((top_right_left_sprite, top_right_left_collisions),
                                   self.sprites_utu.sprites[384].image, 3, 19, 3, 3, self.return_to_door)

        self.make_switch_collision((top_right_left_sprite, top_right_left_collisions),
                                   self.sprites_utu.sprites[384].image, 18, 3, 3, 11, self.return_to_door)

        self.make_switch_collision((top_right_left_sprite, top_right_left_collisions),
                                   self.sprites_utu.sprites[384].image, 7, 3, 7, 7, self.return_to_door)
        self.switching_objects.append(top_right_left_sprite)
        self.switching_collision_list.append(top_right_left_collisions)

        left_right_right_sprite = pygame.sprite.Group()
        left_right_right_collisions = []
        self.make_switch_collision((left_right_right_sprite, left_right_right_collisions),
                                   self.sprites_utu.sprites[384].image, 4, 3, 3, 11, self.return_to_door)

        self.make_switch_collision((left_right_right_sprite, left_right_right_collisions),
                                   self.sprites_utu.sprites[384].image, 18, 3, 3, 11, self.return_to_door)

        self.make_switch_collision((left_right_right_sprite, left_right_right_collisions),
                                   self.sprites_utu.sprites[384].image, 15, 3, 7, 7, self.return_to_door)
        self.switching_objects.append(left_right_right_sprite)
        self.switching_collision_list.append(left_right_right_collisions)

        left_top_left_sprite = pygame.sprite.Group()
        left_top_left_collisions = []
        self.make_switch_collision((left_top_left_sprite, left_top_left_collisions),
                                   self.sprites_utu.sprites[384].image, 4, 3, 3, 11, self.return_to_door)

        self.make_switch_collision((left_top_left_sprite, left_top_left_collisions),
                                   self.sprites_utu.sprites[384].image, 3, 19, 3, 3, self.return_to_door)

        self.make_switch_collision((left_top_left_sprite, left_top_left_collisions),
                                   self.sprites_utu.sprites[384].image, 7, 3, 7, 7, self.return_to_door)
        self.switching_objects.append(left_top_left_sprite)
        self.switching_collision_list.append(left_top_left_collisions)

        right_top_right_sprite = pygame.sprite.Group()
        right_top_right_collisions = []
        self.make_switch_collision((right_top_right_sprite, right_top_right_collisions),
                                   self.sprites_utu.sprites[384].image, 18, 3, 3, 11, self.return_to_door)

        self.make_switch_collision((right_top_right_sprite, right_top_right_collisions),
                                   self.sprites_utu.sprites[384].image, 3, 19, 3, 3, self.return_to_door)

        self.make_switch_collision((right_top_right_sprite, right_top_right_collisions),
                                   self.sprites_utu.sprites[384].image, 15, 3, 7, 7, self.return_to_door)
        self.switching_objects.append(right_top_right_sprite)
        self.switching_collision_list.append(right_top_right_collisions)

        left_right_left_sprite = pygame.sprite.Group()
        left_right_left_collisions = []
        self.make_switch_collision((left_right_left_sprite, left_right_left_collisions),
                                   self.sprites_utu.sprites[384].image, 4, 3, 3, 11, self.return_to_door)

        self.make_switch_collision((left_right_left_sprite, left_right_left_collisions),
                                   self.sprites_utu.sprites[384].image, 18, 3, 3, 11, self.return_to_door)

        self.make_switch_collision((left_right_left_sprite, left_right_left_collisions),
                                   self.sprites_utu.sprites[384].image, 7, 3, 7, 7, self.return_to_door)
        self.switching_objects.append(left_right_left_sprite)
        self.switching_collision_list.append(left_right_left_collisions)

        self.change_flag = True

    def castle_east_wing_door_west(self):
        self.use_door(50, 304, self.set_screen_castle_east_wing)

    def unlock_boss_door_east(self):
        self.now = pygame.time.get_ticks()
        if self.now - self.last_switch > 1000:
            self.boss_door_east_flag = True
            self.next_terrain_switch_time = 4
            self.switch_interval = 0.185
            self.start_switching()
            self.last_switch = pygame.time.get_ticks()

    def set_screen_castle_east_wing(self):
        self.terrain_switching_clean_up()
        self.terrain = league.Tilemap('../assets/castle_terrain.lvl', self.sprites_utu, layer=1)
        self.details = league.Tilemap('../assets/blank.lvl', self.sprites_utu, layer=2)
        self.drawables.append(self.terrain.passable.sprites())
        self.drawables.append(self.details.passable.sprites())

        self.make_west_door(self.castle_fork_door_east)

        self.make_collision(self.sprites_utu.sprites[835].image, 17, 1, 10, 1, self.unlock_boss_door_east)

        for i in range(25):
            lava_start_sprite = pygame.sprite.Group()
            lava_start_collision = []
            self.make_switch_collision((lava_start_sprite, lava_start_collision),
                                       self.sprites_utu.sprites[384].image, 24 - i, 5 + i, 0, 20, self.return_to_door)
            self.switching_objects.append(lava_start_sprite)
            self.switching_collision_list.append(lava_start_collision)

        self.change_flag = True


    def castle_west_wing_door_east(self):
        self.use_door(718, 340, self.set_screen_castle_west_wing)

    def unlock_boss_door_west(self):
        self.now = pygame.time.get_ticks()
        if self.now - self.last_switch > 1000:
            self.boss_door_west_flag = True
            self.next_terrain_switch_time = 4
            self.switch_interval = 0.185
            self.start_switching()
            self.last_switch = pygame.time.get_ticks()

    def set_screen_castle_west_wing(self):
        self.terrain_switching_clean_up()
        self.terrain = league.Tilemap('../assets/castle_terrain.lvl', self.sprites_utu, layer=1)
        self.details = league.Tilemap('../assets/blank.lvl', self.sprites_utu, layer=2)
        self.drawables.append(self.terrain.passable.sprites())
        self.drawables.append(self.details.passable.sprites())

        self.make_east_door(self.castle_fork_door_west)

        self.make_collision(self.sprites_utu.sprites[835].image, 8, 1, 9, 1, self.unlock_boss_door_west)

        for i in range(25):
            lava_start_sprite = pygame.sprite.Group()
            lava_start_collision = []
            self.make_switch_collision((lava_start_sprite, lava_start_collision),
                                       self.sprites_utu.sprites[384].image, 0, 1 + i, 0, 20, self.return_to_door)
            self.switching_objects.append(lava_start_sprite)
            self.switching_collision_list.append(lava_start_collision)

        self.change_flag = True


    def castle_boss_room_south_door(self):
        self.use_door(365, 500, self.set_screen_castle_boss_room)

    def set_screen_castle_boss_room(self):
        self.terrain_switching_clean_up()
        self.terrain = league.Tilemap('../assets/castle_terrain.lvl', self.sprites_utu, layer=1)
        self.details = league.Tilemap('../assets/blank.lvl', self.sprites_utu, layer=2)
        self.drawables.append(self.terrain.passable.sprites())
        self.drawables.append(self.details.passable.sprites())

        self.change_flag = True

