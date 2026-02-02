import pygame
from Game.Sprites.Player import PhysicsSprite

class NPC(PhysicsSprite):
    def __init__(self, image: pygame.Surface, position: pygame.Vector2, game, tilemap):
        super().__init__(image, position, game, tilemap)
        self.game = game
        self.tilemap = tilemap
        self.dialogue = []
        self.current_dialogue_index = 0
        self.font = pygame.font.SysFont("Arial", 14)
        self.is_talking = False

    def update(self):
        super().update()

    def draw(self):
        super().draw()
        if self.is_talking and self.current_dialogue_index < len(self.dialogue):
            self._draw_dialogue()