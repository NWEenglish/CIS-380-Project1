#!/usr/bin/env python3

import pygame
import sys
from player import Player
from screen import Screen
from enemy import Enemy
sys.path.append('..')
import league


def main():
    """Just used to set up the engine and screen"""

    league.Settings.width = 800
    league.Settings.height = 640
    "Sets the size of the window. 800 x 640 is 25 x 20 32bit sprites"

    engine = league.Engine("Gricelda")
    engine.init_pygame()

    user = Player(engine,5,10)
    engine.objects.append(user)

    # Add an enemy
    enemy = Enemy(engine, "../assets/imp - walk - vanilla.png", "../assets/imp - attack - vanilla.png", 5, 10)
    engine.objects.append(enemy)
    # screen = Screen(enemy, engine)
    # engine.objects.append(screen)

    # itemList = [user]
    # itemList.append(enemy)

    # Make enemy into enemyList
    screen = Screen(user, enemy, engine)

    # screen = Screen(user, engine)
    "Screen is passed the player to allow them to be changed by the world"
    "   and engine to allow all world updates"
    engine.objects.append(screen)

    #pygame.time.set_timer(pygame.USEREVENT + 1, 1000 // league.Settings.gameTimeFactor)
    engine.key_events[pygame.K_a] = user.move_left
    engine.key_events[pygame.K_d] = user.move_right
    engine.key_events[pygame.K_w] = user.move_up
    engine.key_events[pygame.K_s] = user.move_down
    engine.key_events[pygame.K_s] = user.move_down
    engine.key_events[pygame.K_o] = user.melee
    engine.key_events[pygame.K_p] = user.range
    engine.events[pygame.QUIT] = engine.stop
    engine.run()


if __name__ == '__main__':
    main()

