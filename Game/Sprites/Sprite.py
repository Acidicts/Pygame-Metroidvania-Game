import pygame

class Sprite:
    def __init__(self, image, position):
        self.image = image
        self.rect = self.image.get_rect(topleft=position)

    def draw(self, surf):
        surf.blit(self.image, self.rect)

    def update(self, dt):
        pass