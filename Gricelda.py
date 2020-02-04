#!/usr/bin/env python3

import pygame
import sys
import league
from player import Player
from screen import Screen
sys.path.append('..')




def main():
    """Just used to set up the engine and screen"""

    league.Settings.width = 928
    league.Settings.height = 600
    "Sets the size of the window"

    engine = league.Engine("Gricelda")
    engine.init_pygame()

    user = Player(2)
    engine.objects.append(user)

    screen = Screen(user, engine)
    "Screen is passed the player to allow them to be changed by the world"
    "   and engine to allow all world updates"
    engine.objects.append(screen)

    #pygame.time.set_timer(pygame.USEREVENT + 1, 1000 // league.Settings.gameTimeFactor)
    engine.key_events[pygame.K_a] = user.move_left
    engine.key_events[pygame.K_d] = user.move_right
    engine.key_events[pygame.K_w] = user.move_up
    engine.key_events[pygame.K_s] = user.move_down
    engine.events[pygame.QUIT] = engine.stop
    engine.run()


if __name__ == '__main__':
    main()

