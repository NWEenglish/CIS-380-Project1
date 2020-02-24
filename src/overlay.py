import pygame
import sys
sys.path.append('..')
from league import *

class Overlay(DUGameObject):
    def __init__(self, player):
        super().__init__(self)
        self._layer = 1000
        self.player = player
        self.font = pygame.font.Font('freesansbold.ttf',32)
        self.image = pygame.Surface([120, 40])
        self.image.fill((0,0,0))
        self.text = self.font.render("", True, (0,0,0))
        self.image.blit(self.text, (0, 0))
        self.rect = self.image.get_rect()
        self.x = 0
        self.y = 0
        self.rect.x = 000
        self.rect.y = 0
        self.static = True

    def update(self, deltaTime):
        self.image.fill((127, 127, 127))
        self.text = self.font.render("HP: " + str(self.player.health), True, (0,0,0))
        self.image.blit(self.text, (0, 0))