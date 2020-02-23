#!/usr/bin/env python3
import league
import pygame
import sys
import math
from player import Player
from screen import Screen
sys.path.append('..')


def main():
    """Just used to set up the engine and screen"""

    league.Settings.width = 800
    league.Settings.height = 640
    "Sets the size of the window. 800 x 640 is 25 x 20 32bit sprites"

    engine = league.Engine("Gricelda")
    engine.init_pygame()

    user = Player(engine, 5, 10)
    engine.objects.append(user)

    screen = Screen(user, engine)

    "Screen is passed the player to allow them to be changed by the world"
    "   and engine to allow all world updates"
    engine.objects.append(screen)

    pygame.mixer.init()
    background_track = pygame.mixer.Sound("../assets/track6.ogg")
    background_track.play(-1)
    
    engine.drawables.remove(user)
    showTitleScreen(screen, engine)
    engine.drawables.add(user)

    engine.events[pygame.QUIT] = engine.stop
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

