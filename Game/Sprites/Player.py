import pygame
from statistics import median

from Game.Sprites.PhysicsSprite import PhysicsSprite
from Game.utils.helpers import crop_to_content, find_tilemap_for_rect
from Game.utils.utils import SpriteSheet


class Player(PhysicsSprite):
    def __init__(self, game, position):
        super().__init__(pygame.surface.Surface((32, 32)), position, game)
        self.attributes = {
            "max_speed": 200,
            "velocity": pygame.math.Vector2(0, 0),
            "acceleration": 1200,
            "friction": 600,
            "air_resistance": 100,
            "terminal_velocity": 600,
            "max_health": 10,
            "current_max_health": 5,
            "health": 5,
            "jump_velocity": -500,
            "jumps_left": 1,
            "max_jumps": 1,

            "immunity": 0,
            "attack_cooldown": 0.5,
            "attack_damage": 1,
            "attack_timer": 0,

            "movable": True,
            "movable_timer": 0,
        }

        # Attack hitbox properties
        self.attack_hitbox = None
        self.is_attacking = False
        self.attacked_enemies = set()

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

        self.debug = True

        self.currency = 100 # Default for testing or whatever
        self.inventory = {}

    def add_attributes(self, attrs):
        """Apply a dictionary of attributes to the player"""
        for key, value in attrs.items():
            if key == "health":
                # Increase max health and heal by the same amount
                self.attributes["current_max_health"] += value
                self.attributes["health"] += value

                # Clamp current_max_health to absolute maximum
                if self.attributes["current_max_health"] > self.attributes["max_health"]:
                    self.attributes["current_max_health"] = self.attributes["max_health"]

                # Clamp health to new current_max_health
                if self.attributes["health"] > self.attributes["current_max_health"]:
                    self.attributes["health"] = self.attributes["current_max_health"]

            elif key == "max_speed" or key == "speed":
                self.attributes["max_speed"] += value
            elif key == "jumps":
                self.attributes["max_jumps"] += value
            elif key == "attack_damage":
                self.attributes["attack_damage"] += value
            else:
                # Handle other attributes like luck, looting, etc.
                if key in self.attributes:
                    if isinstance(self.attributes[key], (int, float)):
                        self.attributes[key] += value
                    else:
                        self.attributes[key] = value
                else:
                    self.attributes[key] = value

    def check_enemy_collisions(self):
        for enemy in self.tilemap.enemies.sprites():
            if self.rect.colliderect(enemy.rect) and self.attributes["immunity"] <= 0:
                direction = -1
                if enemy.rect.centerx > self.rect.centerx:
                    direction = 1
                self.take_damage(1, pygame.math.Vector2(-300 * direction, -200))

    def take_damage(self, damage, direction):
        self.attributes["health"] -= damage
        if self.attributes["health"] < 0:
            self.attributes["health"] = 0

        self.attributes["immunity"] = 1.0

        self.apply_knockback(direction)

    def apply_knockback(self, vec):
        self.velocity.x += vec.x
        self.velocity.y += vec.y

    def _resolve_animation_name(self, base_name):
        # Don't apply directional prefixes to attack animations or other special animations
        attack_animations = ["slash", "double_slash"]
        if base_name in attack_animations:
            return base_name

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
        # Don't update animation direction if we're in an attack animation
        if self.animation_base in ["slash", "double_slash"]:
            return

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

        self.animation_frame += speed * dt

        if not loop and int(self.animation_frame) >= len(images):
            # Animation has finished playing
            if self.animation_base in ["slash", "double_slash"]:
                # For attack animations, we handle the completion elsewhere
                # Don't automatically switch to idle here
                pass
            else:
                # For other non-looping animations, go back to idle
                self.set_animation("idle")
        elif int(self.animation_frame) >= len(images) and loop:
            # For looping animations that have reached the end
            self.animation_frame = 0

    def load_animations(self):
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
        if self.rect.y > 1000:
            self.attributes["health"] = 0

        if self.attributes["movable_timer"] > 0:
            self.attributes["movable_timer"] -= dt

        self.controls(dt)
        super().update(dt)

        if self.attributes["immunity"] > 0:
            self.attributes["immunity"] -= dt
        else:
            self.attributes["immunity"] = 0

        # Update facing direction
        if self.velocity.x < -0.01:
            self.facing_right = False
        elif self.velocity.x > 0.01:
            self.facing_right = True

        # Attack logic
        if self.is_attacking:
            self.update_attack_hitbox()
            self.check_attack_collisions()

        self.check_enemy_collisions()

        tilemap_name, tilemap = find_tilemap_for_rect(self.game.tilemaps, self.rect)
        if tilemap is not None:
            self.tilemap_name = tilemap_name
            self.tilemap = tilemap

        self.on_ground = self.collisions["bottom"]

        if self.on_ground:
            self.attributes["jumps_left"] = self.attributes["max_jumps"]

        # Animation State
        if self.is_attacking:
            pass # Keep slash animation
        elif self.on_ground:
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

        # Check for attack animation completion
        if self.is_attacking:
             # Look up animation length
             current_anim = self.animations.get(self.animation)
             if current_anim:
                 images = current_anim[0].get_images_list()
                 if self.animation_frame >= len(images):
                     self.is_attacking = False
                     self.attack_hitbox = None

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

        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)

        self.image = frame
        # Use the precise position for drawing to reduce jittering
        draw_pos = (
            int(self.pos.x + (self.rect.width - frame.get_width()) // 2 - camera_offset[0]),
            int(self.pos.y + self.rect.height - frame.get_height() - camera_offset[1])
        )
        surf.blit(frame, draw_pos)

        # Draw attack hitbox for debugging if needed
        if self.attack_hitbox and self.debug:
            hitbox_surf = pygame.Surface((self.attack_hitbox.width, self.attack_hitbox.height), pygame.SRCALPHA)
            hitbox_surf.fill((255, 0, 0, 100))  # Semi-transparent red
            surf.blit(hitbox_surf, (self.attack_hitbox.x - camera_offset[0], self.attack_hitbox.y - camera_offset[1]))

    def update_attack_hitbox(self):
        if self.is_attacking:
            if self.facing_right:
                hitbox_x = self.rect.right  # Hitbox starts right after the player
            else:
                hitbox_x = self.rect.left - self.rect.width  # Hitbox starts to the left of the player

            hitbox_y = self.rect.y + (self.rect.height // 4)  # Slightly below the top of the player

            # Define hitbox dimensions (slightly larger than player for effective reach)
            hitbox_width = self.rect.width
            hitbox_height = self.rect.height // 2  # Half the player height

            self.attack_hitbox = pygame.Rect(hitbox_x, hitbox_y, hitbox_width, hitbox_height)
        else:
            self.attack_hitbox = None

    def check_attack_collisions(self):
        """Check for collisions between the attack hitbox and enemies"""
        if self.attack_hitbox and self.is_attacking:
            for enemy in self.tilemap.enemies.sprites():
                if self.attack_hitbox.colliderect(enemy.rect):
                    if enemy not in self.attacked_enemies:
                        # Damage the enemy
                        enemy.take_damage(self.attributes["attack_damage"])

                        knockback_direction = 1 if enemy.rect.centerx < self.rect.centerx else -1

                        self.attacked_enemies.add(enemy)

    def attack(self):
        # Only allow attack if cooldown is finished
        if self.attributes["attack_timer"] <= 0:
            self.attributes["attack_timer"] = self.attributes["attack_cooldown"]
            self.is_attacking = True
            self.attacked_enemies.clear()

            # Set the attack animation - it will not be prefixed with direction thanks to our fix
            self.set_animation("slash")  # or "double_slash" for stronger attack

            # Reset animation frame to start from the beginning
            self.animation_frame = 0


    def controls(self, dt):
        keys = pygame.key.get_pressed()

        if not self.attributes["movable"]:
            self.velocity.x = 0
            return

        if keys[pygame.K_w]:
            for npc in self.tilemap.npcs.sprites():
                if self.rect.colliderect(npc.rect) and hasattr(npc, 'interact'):
                    self.attributes["movable"] = npc.interact(self)

        # Update attack timer (cooldown)
        if self.attributes["attack_timer"] > 0:
            self.attributes["attack_timer"] -= dt
            if self.attributes["attack_timer"] < 0:
                self.attributes["attack_timer"] = 0

        # Handle attack input
        if keys[pygame.K_x] or keys[pygame.K_c]:  # Using X or C as attack buttons
            self.attack()


        horizontal_input = 0
        if keys[pygame.K_LEFT]:
            horizontal_input -= 1
        if keys[pygame.K_RIGHT]:
            horizontal_input += 1

        if horizontal_input != 0:
            target_speed = self.attributes["max_speed"] * horizontal_input
            if self.on_ground:
                self.velocity.x += horizontal_input * self.attributes["acceleration"] * dt
                # Clamp to max speed
                self.velocity.x = max(-self.attributes["max_speed"], min(self.attributes["max_speed"], self.velocity.x))
            else:
                air_acceleration = self.attributes["acceleration"] * 0.7
                if (target_speed > 0 and self.velocity.x < target_speed) or (target_speed < 0 and self.velocity.x > target_speed):
                    self.velocity.x += horizontal_input * air_acceleration * dt
                    self.velocity.x = max(-self.attributes["max_speed"], min(self.attributes["max_speed"], self.velocity.x))
                else:
                    friction = self.attributes["air_resistance"] * 0.5
                    decel = friction * dt
                    if self.velocity.x > 0 >= target_speed:
                        self.velocity.x = max(target_speed, self.velocity.x - decel)
                    elif self.velocity.x < 0 <= target_speed:
                        self.velocity.x = min(target_speed, self.velocity.x + decel)
        else:
            if self.velocity.x != 0:
                friction = self.attributes["friction"] if self.on_ground else self.attributes["air_resistance"] * 0.7
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
                try:
                    if pygame.key.get_just_pressed()[pygame.K_SPACE]:
                        self.velocity.y = self.attributes["jump_velocity"]
                        self.attributes["jumps_left"] -= 1
                except AttributeError:
                    pass

        if not keys[pygame.K_SPACE] and self.velocity.y < 0 and self.attributes["immunity"] <= 0:
            self.velocity.y *= 0.3
