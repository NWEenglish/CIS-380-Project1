#!/usr/bin/env python3

import pygame
import sys
import math
from player import Player
from screen import Screen
from enemy import Enemy
sys.path.append('..')
import league

def distance(x1, y1, x2, y2):
    return math.sqrt( abs( math.pow(y2 - y1, 2) + math.pow(x2 - x1, 2) ) )

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
    enemy = Enemy(engine, "../assets/imp - walk - vanilla.png", "../assets/imp - attack - vanilla.png", 100, 20, 20)
    enemy.reset_loc()
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

    # Moves the enemy
    # enemy.move_right

    #pygame.time.set_timer(pygame.USEREVENT + 1, 1000 // league.Settings.gameTimeFactor)
    engine.key_events[pygame.K_a] = user.move_left
    engine.key_events[pygame.K_d] = user.move_right
    engine.key_events[pygame.K_w] = user.move_up
    engine.key_events[pygame.K_s] = user.move_down
    engine.key_events[pygame.K_s] = user.move_down
    engine.key_events[pygame.K_o] = user.melee
    engine.key_events[pygame.K_p] = user.range

    # Used for enemy events
    move_enemy_right = pygame.USEREVENT + 1
    move_enemy_left = pygame.USEREVENT + 2
    move_enemy_up = pygame.USEREVENT + 3
    move_enemy_down = pygame.USEREVENT + 4
    move_enemy_idle = pygame.USEREVENT + 5

    engine.events[move_enemy_right] = enemy.move_right
    engine.events[move_enemy_left] = enemy.move_left
    engine.events[move_enemy_up] = enemy.move_up
    engine.events[move_enemy_down] = enemy.move_down
    engine.events[move_enemy_idle] = enemy.move_idle

    engine.events[pygame.QUIT] = engine.stop

    # engine.run()


    # Update enemy location
    while True:

        engine.run()
        # engine.stop(pygame.time)

        # If player is within range to begin chase
        if distance(enemy.x, enemy.y, user.x, user.y) < 2000:

            # Move along the y-axis
            if enemy.x - 20 <= user.x <= enemy.x + 20:

                # Move down
                if enemy.y < user.y:
                    pygame.time.set_timer(move_enemy_up, 0)
                    pygame.time.set_timer(move_enemy_right, 0)
                    pygame.time.set_timer(move_enemy_left, 0)
                    pygame.time.set_timer(move_enemy_idle, 0)

                    pygame.time.set_timer(move_enemy_down, 100)

                    print("move down")

                # Move up
                elif user.y < enemy.y:
                    pygame.time.set_timer(move_enemy_down, 0)
                    pygame.time.set_timer(move_enemy_right, 0)
                    pygame.time.set_timer(move_enemy_left, 0)
                    pygame.time.set_timer(move_enemy_idle, 0)

                    pygame.time.set_timer(move_enemy_up, 100)

                    print("move up")

            else: #user.x < enemy.x - 200 or user.x > enemy.x + 200:

                # If enemy is to the left of user, move right
                if enemy.x - 200 < user.x < enemy.x:
                    pygame.time.set_timer(move_enemy_up, 0)
                    pygame.time.set_timer(move_enemy_down, 0)
                    pygame.time.set_timer(move_enemy_right, 0)
                    pygame.time.set_timer(move_enemy_idle, 0)

                    pygame.time.set_timer(move_enemy_left, 100)

                    print("move left")

                # If enemy is to the right of user, move left
                elif enemy.x < user.x < enemy.x + 200:
                    pygame.time.set_timer(move_enemy_up, 0)
                    pygame.time.set_timer(move_enemy_down, 0)
                    pygame.time.set_timer(move_enemy_left, 0)
                    pygame.time.set_timer(move_enemy_idle, 0)

                    pygame.time.set_timer(move_enemy_right, 100)

                    print("move right")

            # Idle
            # elif user.y - 20 <= enemy.y <= user.y + 20:
            #     pygame.time.set_timer(move_enemy_down, 0)
            #     pygame.time.set_timer(move_enemy_right, 0)
            #     pygame.time.set_timer(move_enemy_left, 0)
            #     pygame.time.set_timer(move_enemy_up, 0)
            #
            #     pygame.time.set_timer(move_enemy_idle, 100)

        # engine.run()
        engine.stop(pygame.time)


if __name__ == '__main__':
    main()

