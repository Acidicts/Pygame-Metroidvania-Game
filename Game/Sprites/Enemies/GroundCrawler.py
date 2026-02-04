import pygame
from Game.Sprites.Enemy import Enemy


class GroundCrawler(Enemy):
    def __init__(self, img, position, game, tilemap):
        super().__init__(img, position, game)
        self.direction = 1
        self.tilemap = tilemap
        self.speed = 50  # pixels per second

        # Debug flag
        self.debug = False

        # Ledge detection
        self.ledge_grace_px = 3
        self.flip_cooldown_ms = 150
        self.last_flip_ts = 0
        self.flip_nudge_px = 0.35

        # Multi-sample ledge detection
        self.samples_across = 3
        self.samples_down = 2
        self.ledge_frames_threshold = 2
        self._ledge_frame_counter = 0

    def _do_flip(self, reason, debug_info=None):
        """Flip direction with cooldown and nudge to avoid re-collision."""
        now = pygame.time.get_ticks()

        if now - self.last_flip_ts < self.flip_cooldown_ms:
            if self.debug:
                print(f"[GroundCrawler _do_flip] suppressed (cooldown) reason={reason}")
            return False

        # Flip direction
        self.direction *= -1
        self.velocity.x = self.speed * self.direction

        # Apply small nudge away from edge
        self.pos.x += self.direction * self.flip_nudge_px
        self.rect.x = int(self.pos.x)

        self.last_flip_ts = now

        if self.debug:
            print(f"[GroundCrawler _do_flip] FLIP reason={reason} dir={self.direction}")
        return True

    def take_damage(self, damage):
        if self.rect.centerx > self.game.player.rect.centerx:
            self.direction = 1
        else:
            self.direction = -1
        self.apply_knockback(pygame.Vector2(self.direction*100, -100))

        super().take_damage(damage)

    def _sample_ground_support(self):
        ts = self.tilemap.tile_size
        if ts <= 0:
            return True, False

        # Determine sampling positions
        if self.direction >= 0:
            toe_x = self.rect.right - 1
            horiz_offsets = [toe_x, toe_x - max(2, self.rect.width // 4), self.rect.centerx - max(2, self.rect.width // 4)]
        else:
            toe_x = self.rect.left
            horiz_offsets = [toe_x, toe_x + max(2, self.rect.width // 4), self.rect.centerx + max(2, self.rect.width // 4)]

        vert_offsets = [1, self.ledge_grace_px]

        # Sample points
        ahead_solid = False
        samples = []

        for hx in horiz_offsets:
            for vy in vert_offsets:
                px = int(hx)
                py = int(self.rect.bottom + vy)
                gx = px // ts
                gy = py // ts
                tile = self.tilemap.get_tile(gx, gy)
                solid = tile and ('solid' in tile.get('properties', []))
                samples.append({'px': (px, py), 'gx': gx, 'gy': gy, 'solid': solid})
                if solid:
                    ahead_solid = True

        # Check neighbor tile one step ahead
        neighbor_gx = int((toe_x // ts) + self.direction)
        neighbor_gy = int((self.rect.bottom + 1) // ts)
        neighbor_tile = self.tilemap.get_tile(neighbor_gx, neighbor_gy)
        neighbor_solid = neighbor_tile and ('solid' in neighbor_tile.get('properties', []))

        return ahead_solid, neighbor_solid, samples

    def update(self, dt):
        # Set horizontal velocity
        self.velocity.x = self.speed * self.direction

        # Sample ground ahead
        ahead_solid, neighbor_solid, samples = self._sample_ground_support()

        # Debug output before physics
        if self.debug:
            pos = getattr(self, 'pos', self.rect.topleft)
            sample_summary = ','.join([f"({s['px']}->{s['gx']},{s['gy']} solid={s['solid']})" for s in samples])
            print(f"[GroundCrawler update] BEFORE rect={self.rect.topleft} pos={pos} vel.x={self.velocity.x:.2f} dir={self.direction} samples=[{sample_summary}] neighbor_solid={neighbor_solid} collisions_bottom={self.collisions['bottom']}")

        # Call parent update (physics)
        super().update(dt)

        # Debug output after physics
        if self.debug:
            pos = getattr(self, 'pos', self.rect.topleft)
            print(f"[GroundCrawler update] AFTER rect={self.rect.topleft} pos={pos} vel.x={self.velocity.x:.2f} dir={self.direction} collisions_left={self.collisions['left']} collisions_right={self.collisions['right']}")

        # Check for horizontal collisions and flip
        if self.collisions["left"] or self.collisions["right"]:
            self._do_flip('collision')
            self.velocity.x = self.speed * self.direction

        # Ledge detection: if no support ahead and no neighbor solid, increment counter and flip when threshold reached
        if not ahead_solid and not neighbor_solid:
            self._ledge_frame_counter += 1
            if self._ledge_frame_counter >= self.ledge_frames_threshold:
                flipped = self._do_flip('ledge')
                if flipped:
                    self._ledge_frame_counter = 0
                    self.velocity.x = self.speed * self.direction
        else:
            # Support detected, reset counter
            self._ledge_frame_counter = 0

