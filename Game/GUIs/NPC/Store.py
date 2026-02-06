import pygame

from Game.GUIs.Screen import Screen


class StoreScreen(Screen):
    def __init__(self, game, bound_sprite=None):
        super().__init__(game, bound_sprite)