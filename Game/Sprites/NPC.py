import pygame
from Game.Sprites.Player import PhysicsSprite

class NPC(PhysicsSprite):
    def __init__(self, image, position, game, tilemap):
        super().__init__(image, position, game)
        self.game = game
        self.tilemap = tilemap
        self.dialogue = []
        self.current_dialogue_index = 0
        self.font = pygame.font.SysFont("Arial", 14)
        self.is_talking = False

    def update(self, dt):
        super().update(dt)

    def draw(self, surface, offset):
        super().draw(surface, offset)