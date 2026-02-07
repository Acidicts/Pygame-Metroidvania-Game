import json

import pygame

from Game.Sprites.NPCs.Interactable import Interactive
from Game.utils.utils import load_image, make_generic_surface

class Shop(Interactive):
    def __init__(self, pos, game, path, tilemap):
        self.pos = pos
        self.game = game
        self.image = make_generic_surface((16,16), (0, 0, 255))

        self.path = path
        self.data = self.load_data()

        super().__init__(self.image, self.pos, self.game, tilemap)

    def load_data(self):
        with open(self.path, "r") as f:
            data = json.load(f)
        return data

    def display_items(self):
        print(f"Welcome to {self.name}!")
        print("Here are the items available for purchase:")
        for item in self.items:
            print(f"- {item}")

    def interact(self, player):
        self.interacted = True
        self.player = player
        return False

    def draw(self, screen, offset):
        super().draw(screen, offset)

    def update(self, dt):
        super().update(dt)

        if self.interacted:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                self.interacted = False
                self.player.attributes["movable"] = True
