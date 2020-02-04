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
        drawables holds all the objects that will be placed on top of the tilemap
        collisions holds tuples of objects and their corresponding method call
        sprites is a sprite sheet
        terrain is the tilemap that will be loaded by update
        world_size is how many tiles the .lvl says it has times the size league.Settings says
            the tiles are. Currently only used to set the player boundary and is set once"""

        self.engine = g_engine
        self.user = user

        self.drawables = []
        self.collisions = []
        self.change_flag = True

        self.sprites = league.Spritesheet('./assets/base_chip_pipo.png', league.Settings.tile_size, 8)
        self.terrain = league.Tilemap('./assets/world.lvl', self.sprites, layer = 1)
        self.world_size = (self.terrain.wide*league.Settings.tile_size, self.terrain.high *league.Settings.tile_size)
        self.user.world_size = self.world_size
        self.set_screen1()

    def update(self, gameDeltaTime):
        """update clears the engine's versions of collisions and drawables and replaces them
            with their local versions set in set_screen methods"""
        if self.change_flag:
            "Allows resets only after a set_screen* is called not every frame"

            self.engine.collisions.clear()
            self.engine.drawables.empty()

            self.engine.drawables.add(self.terrain.passable.sprites())
            self.engine.drawables.add(self.user)
            for d in self.drawables:
                self.engine.drawables.add(d)
            for c in self.collisions:
                self.engine.collisions[c[0]] = (self.user, c[1])

            self.change_flag = False
            self.drawables.clear()
            self.collisions.clear()

    def set_screen1(self):
        self.terrain = league.Tilemap('./assets/world.lvl', self.sprites, layer=1)

        "This is a sample object to modify the player"
        hole = Trigger(1, 256, 256)
        hole.image = self.sprites.sprites[66].image
        self.drawables.append(hole)
        self.collisions.append((hole, self.user.reset_loc))

        "Test object to change screens"
        testOb = Trigger(1, 500, 500)
        testOb.image = self.sprites.sprites[70].image
        self.drawables.append(testOb)
        self.collisions.append((testOb, self.set_screen2))

        self.change_flag = True

    def set_screen2(self):
        """This is a test screen"""
        self.terrain = league.Tilemap('./assets/world.lvl', self.sprites, layer = 1)

        testObj = Trigger(1, 600, 300)
        testObj.image = self.sprites.sprites[67].image
        self.drawables.append(testObj)
        self.collisions.append((testObj, self.set_screen3))

        self.change_flag = True

    def set_screen3(self):
        """This is a test screen"""
        self.terrain = league.Tilemap('./assets/background.lvl', self.sprites, layer = 1)

        hole = Trigger(1, 256, 500)
        hole.image = self.sprites.sprites[66].image
        self.drawables.append(hole)
        self.collisions.append((hole, self.set_screen1))

        "Test to move an object but should be its own DUobject type not a trigger"
        testOb = Trigger(1, 500, 500)
        testOb.image = self.sprites.sprites[70].image
        self.drawables.append(testOb)
        self.collisions.append((testOb, testOb.move_right))

        self.change_flag = True
