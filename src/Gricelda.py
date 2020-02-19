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
    engine.drawables.remove(user)
    engine.drawables.remove(enemy)
    showTitleScreen(screen, engine)
    engine.drawables.add(user)
    engine.drawables.add(enemy)
    engine.run()

def showTitleScreen(screen, engine):
    """
    This method is adapted from: http://inventwithpython.com/pygame/chapter6.html
    We just wanted a 'cute' start screen for our game since we needed another feature
    """
    titleScreenFont = pygame.font.SysFont("comicsansms", 120)
    titleNameSurface = titleScreenFont.render("Gricelda", True, (255, 215, 0))
    titleScreenFont = pygame.font.SysFont("comicsansms", 25)
    titlePressStartSurface = titleScreenFont.render("Press any key to continue", True, (255, 215, 0))
    screen.drawables.append(titleNameSurface)
    screen.drawables.append(titlePressStartSurface)
    inTitleScreen = True
    while inTitleScreen: 
        engine.screen.fill((0, 0, 0))
        engine.screen.blit(titleNameSurface, (150, 80))
        engine.screen.blit(titlePressStartSurface, (220, 400))
        engine.drawables.draw(engine.screen)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                inTitleScreen = False
    screen.drawables.remove(titleNameSurface)
    screen.drawables.remove(titlePressStartSurface)



if __name__ == '__main__':
    main()

