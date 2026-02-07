import pygame
import random

from Game.utils.transisitions import Fadeout
from Game.utils.utils import load_image
from Game.utils.textbox_overlay import TextOverlay


class Hud:
    def __init__(self, game):
        self.game = game
        self.player = self.game.player
        self.assets = self.game.assets["hud"]

        self.font = pygame.font.SysFont("Arial", 16) # High-res font
        self.hearts_assets = self.assets["heart"]
        self.base_heart_size = 32 # High-res heart size
        self.health = self.player.attributes["health"]

        self.shine_interval = 3.0
        self.shine_duration = 1.0

        self.fadeout = Fadeout(duration=3, color=(0, 0, 0))

        self.text_overlay = ""
        self.text_overlay_show = True

        self.crystal_icon_res = load_image("miscellaneous/crystal.png", size=(24, 24))

        # We will track animations per heart index in a dynamic list
        self.hearts_state = []
        self._last_max_health = 0

        self.text_overlay_box = TextOverlay(game)

    def _ensure_hearts_count(self, count):
        """Ensure the hearts_state list has the correct number of entries."""
        while len(self.hearts_state) < count:
            self.hearts_state.append({
                "animation_state": ("full", 0),
                "shine_timer": random.uniform(0, self.shine_interval)
            })
        if len(self.hearts_state) > count:
            self.hearts_state = self.hearts_state[:count]

    def update(self, dt):
        current_max = int(self.player.attributes["current_max_health"])
        self._ensure_hearts_count(current_max)

        current_health = self.player.attributes["health"]

        # Handle damage blink trigger
        if self.health > current_health:
            self.health = current_health
            for heart_data in self.hearts_state:
                heart_data["animation_state"] = ("blink", 0)
        elif self.health < current_health:
            self.health = current_health

        for i, heart_data in enumerate(self.hearts_state):
            # Shine logic for full hearts
            if i + 1 <= current_health:
                heart_data["shine_timer"] -= dt
                if heart_data["shine_timer"] <= 0 and heart_data["animation_state"][0] == "full":
                    heart_data["animation_state"] = ("shine", 0)
                    heart_data["shine_timer"] = self.shine_interval + random.uniform(-0.5, 0.5)

            # Advance animations
            anim_type, frames = heart_data["animation_state"]
            if anim_type == "shine":
                frame_count = len(self.hearts_assets["shine"].images)
                if frames >= frame_count * 5 - 1:
                    heart_data["animation_state"] = ("full", 0)
                else:
                    heart_data["animation_state"] = (anim_type, frames + 1)
            elif anim_type == "blink":
                frame_count = len(self.hearts_assets["blink"].images)
                if frames >= frame_count * 5 - 1:
                    heart_data["animation_state"] = ("full", 0)
                else:
                    heart_data["animation_state"] = (anim_type, frames + 1)

        self.text_overlay_box.update(dt)

    def draw(self, screen):
        if self.player.attributes["health"] > 0:
            self.draw_hud(screen)
        else:
            self.fadeout.draw(screen)
            if self.fadeout.opacity >= 255:
                text_surface = pygame.Font(self.game.fonts["workbench"], 24).render("You Died", True, (255, 255, 255))
                text_surface = pygame.transform.scale(text_surface, (text_surface.get_width() * 4, text_surface.get_height() * 4))
                text_rect = text_surface.get_rect(center=(self.game.screen.get_width() // 2, self.game.screen.get_height() // 2))
                screen.blit(text_surface, text_rect)

    def draw_hud(self, screen):
        current_max = int(self.player.attributes["current_max_health"])
        current_health = self.player.attributes["health"]

        # Scale heart size based on max health to fit in a reasonable area
        # If we have more than 5 hearts, start shrinking them
        heart_size = self.base_heart_size
        if current_max > 5:
            # Gradually shrink from 64 down to 32
            shrink_factor = 5 / current_max
            heart_size = int(max(32, self.base_heart_size * shrink_factor))

        # Determine background box width
        # Padding + (count * heart_size) + Padding
        padding = 20
        box_width = padding * 2 + (current_max * heart_size)
        box_height = heart_size + 60 # Extra height for currency

        pygame.draw.rect(screen, (0, 0, 0, 180), (20, 20, box_width, box_height), border_radius=16)
        pygame.draw.rect(screen, (100, 100, 100), (20, 20, box_width, box_height), 2, border_radius=16)

        for i in range(current_max):
            heart_data = self.hearts_state[i]
            pos = (padding + 20 + i * heart_size, padding + 20)

            # Decide which image to use
            if i + 1 <= current_health:
                # Full or animated
                anim_type, frames = heart_data["animation_state"]
                if anim_type == "shine":
                    frame = frames // 5
                    images = self.hearts_assets["shine"].get_images_list()
                    img = images[min(frame, len(images)-1)]
                elif anim_type == "blink":
                    frame = frames // 5
                    images = self.hearts_assets["blink"].get_images_list()
                    img = images[min(frame, len(images)-1)]
                else:
                    img = self.hearts_assets["full"]
            elif i < current_health < i + 1:
                img = self.hearts_assets["half"]
            else:
                img = self.hearts_assets["empty"]

            scaled_img = pygame.transform.scale(img, (heart_size, heart_size))
            screen.blit(scaled_img, pos)

        # Currency
        currency_y = padding + 20 + heart_size + 10
        screen.blit(self.crystal_icon_res, (padding + 20, currency_y))
        text_surface = self.font.render(str(self.player.currency), True, (255, 255, 255))
        screen.blit(text_surface, (padding + 20 + 40, currency_y - 5))

        # Text Overlay
        if (hasattr(self.text_overlay_box, 'set_text') and
            self.text_overlay != getattr(self, '_last_text_overlay', '') and
            (not hasattr(self.text_overlay_box, 'typewriter_finished') or self.text_overlay_box.typewriter_finished)):
            self.text_overlay_box.set_text(self.text_overlay)
            self._last_text_overlay = self.text_overlay
        self.text_overlay_box.draw(screen, self.text_overlay_show)
