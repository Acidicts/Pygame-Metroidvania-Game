from Game.GUIs.Screen import Screen
from Game.GUIs.StoreTile import StoreTile
import pygame

class StoreScreen(Screen):
    def __init__(self, game, bound_sprite=None):
        super().__init__(game, bound_sprite)

        self.opened = False
        self.opened_progress = 0
        self.max_opened_progress = self.game.displayed_screen.get_size()[1] - 50

        self.tiles = {}
        self.tiles_loaded = False
        self.was_mouse_pressed = False

    def on_open(self, dt):
        self.opened = True
        # Start tile animations after store opens
        if not self.tiles_loaded:
            self.load()
            self.tiles_loaded = True
            for tile in self.tiles.values():
                tile.start_animation()

    def load(self):
        for i, trade_data in enumerate(self.bound_sprite.data["trades"]):
            item_key = trade_data["item"]  # Extract the item name from the trade data
            item_obj = self.game.items[item_key]

            # Create a combined data object that includes both the item object and trade info
            combined_data = {
                "item": item_obj,
                "price": trade_data["price"]
            }

            self.tiles[i] = StoreTile(self.game, combined_data, index=i)

    def draw_tiles(self, screen):
        # First pass: draw all tiles
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        for i, tile in enumerate(self.tiles.values()):
            pos = (screen_width // 2, 50 + i * 140)
            tile.draw(screen, (pos[0], pos[1] + screen_height - self.opened_progress))

        # Second pass: draw info panels (so they appear on top of all tiles)
        for tile in self.tiles.values():
            tile.draw_info(screen)

    def draw(self, screen):
        if self.opened_progress > 0:
            # Draw background dimming based on progress
            alpha = min(150, int((self.opened_progress / self.max_opened_progress) * 150))
            surf = pygame.surface.Surface(screen.get_size(), pygame.SRCALPHA)
            surf.fill((0, 0, 0, alpha))
            screen.blit(surf, (0, 0))

            self.draw_tiles(screen)

    def update(self, dt):
        if self.bound_sprite.interacted:
            if not self.opened:
                self.on_open(dt)

            # Update max_opened_progress in case it changed or should be based on current screen
            self.max_opened_progress = self.game.displayed_screen.get_size()[1] - 50

            if self.opened_progress < self.max_opened_progress:
                self.opened_progress += 1500 * dt
                if self.opened_progress > self.max_opened_progress:
                    self.opened_progress = self.max_opened_progress
        else:
            self.opened = False
            if self.opened_progress > 0:
                self.opened_progress -= 1500 * dt
                if self.opened_progress < 0:
                    self.opened_progress = 0
            else:
                # Fully closed
                self.tiles_loaded = False
                self.tiles = {}

        mouse_pressed = pygame.mouse.get_pressed()[0]

        # Use a list of keys to safely remove items while iterating
        tile_keys = list(self.tiles.keys())
        for key in tile_keys:
            tile = self.tiles[key]
            tile.update(dt)

            # Check for purchase if store is fully opened or opening
            if self.opened and mouse_pressed and not self.was_mouse_pressed:
                # Find which original trade this corresponds to
                # StoreTile stores index, but we can also use the key if they match

                # Calculate current position to match drawing logic
                screen_width = self.game.displayed_screen.get_width()
                screen_height = self.game.displayed_screen.get_height()

                base_pos = (screen_width // 2, 50 + tile.index * 70)
                current_y = base_pos[1] + screen_height - self.opened_progress
                actual_pos = (base_pos[0], current_y)

                if tile.is_buy_hovered_at_pos(actual_pos):
                    if tile.buy():
                        # Remove from UI
                        del self.tiles[key]

                        # Remove from the NPC's actual trade data so it stays gone
                        if self.bound_sprite and "trades" in self.bound_sprite.data:
                            # The index should match the position in the trades list
                            # However, removing from list changes indices of subsequent items.
                            # It's safer to reconstruct self.tiles or use a stable identifier.
                            # For now, let's just remove it from the list if the index matches.
                            if 0 <= tile.index < len(self.bound_sprite.data["trades"]):
                                self.bound_sprite.data["trades"].pop(tile.index)

                                # Re-index remaining tiles to avoid drawing gaps/misalignment
                                new_tiles = {}
                                for i, t in enumerate(self.tiles.values()):
                                    t.index = i
                                    new_tiles[i] = t
                                self.tiles = new_tiles

                        break # Only buy one item per click

        self.was_mouse_pressed = mouse_pressed
