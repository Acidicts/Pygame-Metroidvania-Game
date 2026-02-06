import pygame


class Screen:
    def __init__(self, game, bound_sprite=None):
        self.game = game
        self.screen = game.screen
        self.bound_sprite = bound_sprite

    def handle_input(self):
        pass

    def update(self, dt):
        pass

    def draw(self):
        if self.bound_sprite and self.bound_sprite.interacted:
            surf = pygame.surface.Surface(self.screen.get_size(), pygame.SRCALPHA)
            surf.fill((0, 0, 0, 150))
            self.game.screen.blit(surf, (0, 0))
