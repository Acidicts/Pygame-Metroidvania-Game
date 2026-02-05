import pygame
from Game.Sprites.NPC import NPC

class Interactive(NPC):
    def __init__(self, img, position, game, tilemap):
        super().__init__(img, position, game, tilemap)
        self.interacted = False
        self.player = None
        self.sprite_group = None

    def interact(self, player):
        self.interacted = True
        self.player = player
        return False

    def update(self, dt):
        super().update(dt)

        if self.interacted:
            print("hi")

            self.player.attributes["movable"] = True
            self.interacted = False
