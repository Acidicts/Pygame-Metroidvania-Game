import pygame
from Game.Sprites.NPCs.Interactable import Interactive


class SimpleSpeaker(Interactive):
    def __init__(self, img, position, game, tilemap, text):
        super().__init__(img, position, game, tilemap)
        self.interacted = False
        self.player = None
        self.sprite_group = None
        self.text = text

    def interact(self, player):
        self.interacted = True
        self.player = player
        return False

    def update(self, dt):
        super().update(dt)

        if self.interacted:
            self.game.hud.text_overlay = self.text
            self.game.hud.text_overlay_show = True
            self.interacted = self.game.hud.text_overlay_box.handle_input()
