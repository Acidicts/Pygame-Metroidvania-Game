import pygame
import random

from Game.utils.transisitions import Fadeout
from Game.utils.utils import load_image


class Hud:
    def __init__(self, game):
        self.game = game
        self.player = self.game.player
        self.assets = self.game.assets["hud"]

        self.hearts_assets = self.assets["heart"]
        self.heart_size = 32
        self.health = 0

        self.shine_interval = 3.0
        self.shine_duration = 1.0

        self.fadeout = Fadeout(duration=3, color=(0, 0, 0))

        self.crystal_icon = pygame.Surface((16, 16))
        self.crystal_icon.fill((0, 255, 255))  # Cyan color as placeholder
        pygame.draw.circle(self.crystal_icon, (255, 255, 255), (8, 8), 6, 2)  # White outline

        base_delay = 0.5
        self.hearts = {
            "1": {"pos": (20, 12), "state": "full", "animation_state": ("startup_empty", -int((base_delay + 0.1) * 60)), "rect": pygame.Rect(20, 20, self.heart_size, self.heart_size), "shine_timer": random.uniform(0, self.shine_interval)},
            "2": {"pos": (40, 12), "state": "full", "animation_state": ("startup_empty", -int((base_delay + 0.2) * 60)), "rect": pygame.Rect(60, 20, self.heart_size, self.heart_size), "shine_timer": random.uniform(0, self.shine_interval)},
            "3": {"pos": (60, 12), "state": "full", "animation_state": ("startup_empty", -int((base_delay + 0.3) * 60)), "rect": pygame.Rect(100, 20, self.heart_size, self.heart_size), "shine_timer": random.uniform(0, self.shine_interval)},
            "4": {"pos": (80, 12), "state": "hidden", "animation_state": ("startup_empty", -int((base_delay + 0.4) * 60)), "rect": pygame.Rect(140, 20, self.heart_size, self.heart_size), "shine_timer": random.uniform(0, self.shine_interval)},
            "5": {"pos": (100, 12), "state": "hidden", "animation_state": ("startup_empty", -int((base_delay + 0.5) * 60)), "rect": pygame.Rect(180, 20, self.heart_size, self.heart_size), "shine_timer": random.uniform(0, self.shine_interval)},
        }

    def update(self, dt):
        max_health = self.player.attributes["maxhealth"]
        current_health = self.player.attributes["health"]

        for i in range(1, 5):
            heart_key = str(i)
            if i <= max_health:
                if i <= current_health:
                    if self.hearts[heart_key]["state"] != "full":
                        self.hearts[heart_key]["state"] = "full"
                        self.hearts[heart_key]["animation_state"] = ("blink", 0)
                else:
                    self.hearts[heart_key]["state"] = "empty"
                    self.hearts[heart_key]["animation_state"] = ("full", 0)
            else:
                self.hearts[heart_key]["state"] = "hidden"
                self.hearts[heart_key]["animation_state"] = ("full", 0)

        for heart_data in self.hearts.values():
            if heart_data["state"] == "full":
                heart_data["shine_timer"] -= dt

                if heart_data["shine_timer"] <= 0 and heart_data["animation_state"][0] == "full":
                    heart_data["animation_state"] = ("shine", 0)
                    heart_data["shine_timer"] = self.shine_interval + random.uniform(-0.5, 0.5)

                elif heart_data["animation_state"][0] == "shine":
                    frame_count = len(self.hearts_assets["shine"].images)
                    total_shine_frames = frame_count * 5
                    if heart_data["animation_state"][1] >= total_shine_frames - 1:
                        heart_data["animation_state"] = ("full", 0)

    def update_heart_animations(self):
        for heart_data in self.hearts.values():
            if heart_data["state"] == "full":
                if heart_data["animation_state"][0] == "blink":
                    frame = heart_data["animation_state"][1] // 5
                    frame_count = len(self.hearts_assets["blink"].images)
                    heart_data["animation_state"] = ("blink", heart_data["animation_state"][1] + 1)

                    if frame >= frame_count:
                        heart_data["animation_state"] = ("full", 0)

                elif heart_data["animation_state"][0] == "startup_empty":
                    frame = heart_data["animation_state"][1] // 5
                    heart_data["animation_state"] = ("startup_empty", heart_data["animation_state"][1] + 1)

                    if frame >= 0:
                        heart_data["animation_state"] = ("startup_half", 0)

                elif heart_data["animation_state"][0] == "startup_half":
                    heart_data["animation_state"] = ("startup_half", heart_data["animation_state"][1] + 1)

                elif heart_data["animation_state"][0] == "shine":
                    frame_count = len(self.hearts_assets["shine"].images)
                    total_shine_frames = frame_count * 5
                    heart_data["animation_state"] = ("shine", heart_data["animation_state"][1] + 1)

                    if heart_data["animation_state"][1] >= total_shine_frames - 1:
                        heart_data["animation_state"] = ("full", 0)

    def draw(self, screen):
        if self.player.attributes["health"] > 0:
            self.draw_hud(screen)
        else:
            self.fadeout.draw(screen)
            if self.fadeout.opacity >= 255:
                text_surface = self.game.fonts["workbench"].render("You Died", True, (255, 255, 255))
                text_surface = pygame.transform.scale(text_surface, (text_surface.get_width() * 4, text_surface.get_height() * 4))
                text_rect = text_surface.get_rect(center=(self.game.screen.get_width() // 2, self.game.screen.get_height() // 2))
                screen.blit(text_surface, text_rect)

    def draw_hud(self, screen):
        self.update_heart_animations()

        if self.health > self.player.attributes["health"]:
            self.health = self.player.attributes["health"]
            for key, heart_data in enumerate(self.hearts.values()):
                if heart_data["state"] == "full":
                    heart_data["animation_state"] = ("blink", 0)
                if self.player.attributes["health"] == key + 1:
                    heart_data["animation_state"] = ("blink", 0)

        max_health = self.player.attributes["maxhealth"]

        last_heart_key = str(max_health)
        if (last_heart_key in self.hearts and
            self.hearts[last_heart_key]["animation_state"][0] == "startup_half" and
            self.hearts[last_heart_key]["animation_state"][1] // 5 >= 0):
            if self.hearts["1"]["animation_state"][0] == "startup_half":
                self.hearts["1"]["animation_state"] = ("blink", 0)

        for i in range(1, max_health):
            current_heart = str(i)
            next_heart = str(i + 1)

            if (current_heart in self.hearts and next_heart in self.hearts and
                self.hearts[current_heart]["animation_state"][0] == "full" and
                self.hearts[next_heart]["animation_state"][0] == "startup_half"):
                # Current heart is full, trigger next heart to blink
                self.hearts[next_heart]["animation_state"] = ("blink", 0)

        # Draw background for HUD
        if self.player.attributes["maxhealth"] >= 5:
            pygame.draw.rect(screen, (0, 0, 0), (15, 10, 130, 65), border_radius=8)
        else:
            pygame.draw.rect(screen, (0, 0, 0), (12, 10, 90, 65), border_radius=8)

        for heart in self.hearts:
            heart_data = self.hearts[heart]

            if heart_data["state"] != "hidden":

                if heart_data["state"] == "full":

                    if heart_data["animation_state"][0] == "full":
                        image = pygame.transform.scale(self.hearts_assets["full"], (self.heart_size, self.heart_size))
                        screen.blit(image, heart_data["pos"])

                    elif heart_data["animation_state"][0] == "shine":
                        frame = heart_data["animation_state"][1] // 5
                        frame_count = len(self.hearts_assets["shine"].images)
                        if frame < frame_count:
                            image = pygame.transform.scale(self.hearts_assets["shine"].images[list(self.hearts_assets["shine"].images.keys())[frame]], (self.heart_size, self.heart_size))
                            screen.blit(image, heart_data["pos"])

                    elif heart_data["animation_state"][0] == "startup_empty":
                        frame = heart_data["animation_state"][1] // 5
                        if frame < 0:
                            image = pygame.transform.scale(self.hearts_assets["empty"], (self.heart_size, self.heart_size))
                            screen.blit(image, heart_data["pos"])
                        else:
                            image = pygame.transform.scale(self.hearts_assets["half"], (self.heart_size, self.heart_size))
                            screen.blit(image, heart_data["pos"])

                    elif heart_data["animation_state"][0] == "startup_half":
                        image = pygame.transform.scale(self.hearts_assets["half"], (self.heart_size, self.heart_size))
                        screen.blit(image, heart_data["pos"])

                    elif heart_data["animation_state"][0] == "blink":
                        frame = heart_data["animation_state"][1] // 5
                        frame_count = len(self.hearts_assets["blink"].images)
                        if frame_count > frame >= 0:
                            image = pygame.transform.scale(self.hearts_assets["blink"].images[list(self.hearts_assets["blink"].images.keys())[frame]], (self.heart_size, self.heart_size))
                            screen.blit(image, heart_data["pos"])
                        elif frame < 0:
                            image = pygame.transform.scale(self.hearts_assets["full"], (self.heart_size, self.heart_size))
                            screen.blit(image, heart_data["pos"])

                elif heart_data["state"] == "empty":
                    image = pygame.transform.scale(self.hearts_assets["empty"], (self.heart_size, self.heart_size))
                    screen.blit(image, heart_data["pos"])

        screen.blit(load_image("miscellaneous/crystal.png", size=(16, 16)), (20, 47))
        text_surface = self.game.fonts["Arial"].render(str(self.player.crystals), True, (255, 255, 255))
        screen.blit(text_surface, (40, 45))


