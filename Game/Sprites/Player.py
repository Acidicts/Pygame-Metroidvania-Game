import pygame
from statistics import median

from Game.Sprites.PhysicsSprite import PhysicsSprite
from Game.utils.helpers import crop_to_content
from Game.utils.tilemaps import find_tilemap_for_rect
from Game.utils.utils import SpriteSheet


class Player(PhysicsSprite):
    def __init__(self, game, position):
        super().__init__(pygame.surface.Surface((32, 32)), position, game)
        self.attributes = {
            "max_speed": 200,
            "velocity": pygame.math.Vector2(0, 0),
            "acceleration": 1200,
            "friction": 800,
            "air_resistance": 200,
            "terminal_velocity": 800,
            "max_health": 10,
            "current_max_health": 5,
            "health": 5,
            "jump_velocity": -600,
            "jumps_left": 1,
            "max_jumps": 1
        }

        self.player_scale = 1

        self.tilemap_name = "cave"
        self.tilemap = game.tilemaps[self.tilemap_name]
        self.game = game

        self.animation = "idle"
        self.animation_base = "idle"
        self.animation_speed = 1
        self.animation_frame = 0
        self.animations = {}
        self.load_animations()

        self.on_ground = False
        self.facing_right = True

        self.acceleration.y = 2000

    def _resolve_animation_name(self, base_name):
        if base_name.startswith("left_") or base_name.startswith("right_"):
            return base_name

        if self.velocity.x < -0.01:
            direction = "left_"
        elif self.velocity.x > 0.01:
            direction = "right_"
        else:
            direction = "right_" if self.facing_right else "left_"

        candidate = f"{direction}{base_name}"
        return candidate if candidate in self.animations else base_name

    def set_animation(self, animation):
        if animation != self.animation_base:
            self.animation_base = animation
            self.animation = self._resolve_animation_name(animation)
            self.animation_frame = 0

    def _update_animation_direction(self):
        resolved = self._resolve_animation_name(self.animation_base)
        if resolved != self.animation:
            self.animation = resolved
            self.animation_frame = 0

    def run_animation(self, dt):
        anim = self.animations[self.animation]
        speed = anim[1]
        sheet = anim[0]
        images = sheet.get_images_list()
        loop = self.animations[self.animation][2]

        if not images:
            return
        if int(self.animation_frame) >= len(images):
            if loop:
                self.animation_frame = 0
            else:
                self.set_animation("idle")

        if not images:
            return

        self.animation_frame += speed * dt

        if not loop and self.animation_frame >= len(images):
            self.set_animation("idle")

    def load_animations(self):
        TILE_SCALE = 0.25
        self.animations = {
            "idle": (SpriteSheet("little_riven/Idle.png", tile_size=144, colorkey=None, scale=self.player_scale), 15, True),
            "death": (SpriteSheet("little_riven/Death.png", tile_size=144, colorkey=None, scale=self.player_scale), 10, False),
            "double_slash": (SpriteSheet("little_riven/Double Slash.png", tile_size=144, colorkey=None, scale=self.player_scale), 30,
                             False),
            "fall": (SpriteSheet("little_riven/Fall.png", tile_size=144, colorkey=None, scale=self.player_scale), 15, True),
            "hurt": (SpriteSheet("little_riven/Hurt.png", tile_size=144, colorkey=None, scale=self.player_scale), 15, False),
            "idle_break": (SpriteSheet("little_riven/Idle Break.png", tile_size=144, colorkey=None, scale=self.player_scale), 30, False),
            "jump": (SpriteSheet("little_riven/Jump.png", tile_size=144, colorkey=None, scale=self.player_scale), 5, True),
            "run": (SpriteSheet("little_riven/Run.png", tile_size=144, colorkey=None, scale=self.player_scale), 10, True),
            "slash": (SpriteSheet("little_riven/Slash.png", tile_size=144, colorkey=None, scale=self.player_scale), 30, False),
            "smoke_in": (SpriteSheet("little_riven/Smoke In.png", tile_size=144, colorkey=None, scale=self.player_scale), 10, False),
            "smoke_out": (SpriteSheet("little_riven/Smoke Out.png", tile_size=144, colorkey=None, scale=self.player_scale), 10, False),
            "special_skill": (SpriteSheet("little_riven/Special Skill.png", tile_size=144, colorkey=None, scale=self.player_scale), 10,
                              False),
        }

        for key in self.animations.keys():
            sheet = self.animations[key][0]
            for image_key, img in sheet.images.items():
                img = crop_to_content(img)
                sheet.images[image_key] = img

    def update(self, dt):
        self.controls(dt)
        super().update(dt)

        tilemap_name, tilemap = find_tilemap_for_rect(self.game.tilemaps, self.rect)
        if tilemap is not None:
            self.tilemap_name = tilemap_name
            self.tilemap = tilemap

        self.on_ground = any(self.collisions["bottom"])

        if self.on_ground:
            self.attributes["jumps_left"] = self.attributes["max_jumps"]

        if self.on_ground:
            if abs(self.velocity.x) > 1:
                self.set_animation("run")
            else:
                self.set_animation("idle")
        else:
            if self.velocity.y < -40:
                self.set_animation("jump")
            elif self.velocity.y > 40:
                self.set_animation("fall")

        self._update_animation_direction()
        self.run_animation(dt)

        # clamp terminal velocity
        if self.velocity.y > self.attributes["terminal_velocity"]:
            self.velocity.y = self.attributes["terminal_velocity"]

        self.velocity.x = median((-self.attributes["max_speed"], self.velocity.x, self.attributes["max_speed"]))

    def draw(self, surf, camera_offset=(0, 0)):
        sheet = self.animations[self.animation][0]
        images = sheet.get_images_list()
        if not images:
            return

        loop = self.animations[self.animation][2]
        if loop:
            index = int(self.animation_frame) % len(images)
        else:
            index = min(int(self.animation_frame), len(images) - 1)

        frame = images[index]
        if self.velocity.x < -0.01:
            self.facing_right = False
        elif self.velocity.x > 0.01:
            self.facing_right = True

        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)

        self.image = frame
        draw_rect = frame.get_rect(midbottom=self.rect.midbottom)
        surf.blit(frame, (draw_rect.x - camera_offset[0], draw_rect.y - camera_offset[1]))

    def controls(self, dt):
        keys = pygame.key.get_pressed()

        horizontal_input = 0
        if keys[pygame.K_LEFT]:
            horizontal_input -= 1
        if keys[pygame.K_RIGHT]:
            horizontal_input += 1

        if horizontal_input != 0:
            self.velocity.x += horizontal_input * self.attributes["acceleration"] * dt
        else:
            if self.velocity.x != 0:
                friction = self.attributes["friction"] if self.on_ground else self.attributes["air_resistance"]
                decel = friction * dt
                if self.velocity.x > 0:
                    self.velocity.x = max(0, self.velocity.x - decel)
                else:
                    self.velocity.x = min(0, self.velocity.x + decel)

        if keys[pygame.K_SPACE]:
            if self.on_ground:
                self.velocity.y = self.attributes["jump_velocity"]
                self.on_ground = False
                self.attributes["jumps_left"] = self.attributes["max_jumps"] - 1
            elif self.attributes["jumps_left"] > 0:
                # Need to check for a new press for double jump
                # Since we don't have a robust just_pressed without potentially missing frames in high dt
                # we usually use events, but here we try get_just_pressed if available
                try:
                    if pygame.key.get_just_pressed()[pygame.K_SPACE]:
                        self.velocity.y = self.attributes["jump_velocity"]
                        self.attributes["jumps_left"] -= 1
                except AttributeError:
                    # Fallback for older pygame versions if necessary, though 2.2.0 is common now
                    pass

        # Variable jump height: if space is released while moving up, reduce vertical velocity
        if not keys[pygame.K_SPACE] and self.velocity.y < 0:
            self.velocity.y *= 0.5 * (1.0 - dt * 10) # Smoothly reduce velocity when jump key is released
            if self.velocity.y > -10:
                self.velocity.y = 0
