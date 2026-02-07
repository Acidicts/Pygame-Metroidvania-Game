import pygame
import math

class StoreTile:
    def __init__(self, game, data, index=0):
        self.pos = (0, 0)  # Will be set when drawing
        self.game = game
        self.trades = data  # Must be set before create_image()
        self.image = self.create_image()

        self.index = index

        # Track hover state for info panel
        self.hovered = False
        self.info_panel = None

        # Animation properties
        self.animation_started = False
        self.animation_time = 0
        self.animation_duration = 0.6  # Total animation time in seconds
        self.start_delay = index * 0.1  # Stagger start based on index
        self.bounce_offset = 0


    def create_image(self):
        self.base_surface = pygame.Surface((200, 60), pygame.SRCALPHA)
        self.base_surface.fill((0, 0, 0, 0))
        pygame.draw.rect(self.base_surface, (0, 0, 0, 200), self.base_surface.get_rect(), border_radius=10)
        pygame.draw.rect(self.base_surface, (0, 0, 0), self.base_surface.get_rect(), 2, border_radius=10)

        font = pygame.font.Font(self.game.fonts["Pixel"], 12)
        self.num_font = pygame.font.SysFont("Arial", 16, bold=True)

        # Check if self.trades is an Item object or a trade dictionary
        if hasattr(self.trades, 'name'):  # If it's an Item object
            item_name = str(self.trades.name) if hasattr(self.trades, 'name') else str(self.trades)
        elif isinstance(self.trades, dict) and 'item' in self.trades:  # If it's a trade dictionary
            # Handle case where 'item' might be an Item object or a string
            if hasattr(self.trades['item'], 'name'):
                item_name = str(self.trades['item'].name)
            else:
                item_name = str(self.trades['item'])
        else:
            item_name = str(self.trades)

        # Item name on top
        item_text = font.render(item_name, False, (255, 255, 255))
        item_rect = item_text.get_rect(topleft=(8, 8))
        self.base_surface.blit(item_text, item_rect)

        # Price on bottom left - handle both cases
        if isinstance(self.trades, dict) and 'price' in self.trades:
            price_value = self.trades['price']
        else:
            # If we don't have price info, use a default
            price_value = 0

        price_text = self.num_font.render(str(price_value), False, (255, 255, 255))
        price_rect = price_text.get_rect(bottomleft=(8, 52))
        self.base_surface.blit(price_text, price_rect)

        # Buy button area (bottom right corner)
        self.buy_rect = pygame.Rect(140, 35, 55, 20)

        # Create final image
        self.image = self.base_surface.copy()
        return self.image

    def is_buy_hovered(self):
        """Check if mouse is over the buy button"""
        # Use the current pos which is set during draw
        return self.is_buy_hovered_at_pos(self.pos)

    def is_buy_hovered_at_pos(self, pos):
        """Check if mouse is over the buy button at a specific position"""
        mouse_pos = pygame.mouse.get_pos()
        # Scale mouse position from display (800x600) to internal screen (400x300)
        display_size = self.game.displayed_screen.get_size()
        screen_size = self.game.screen.get_size()
        scale_x = screen_size[0] / display_size[0]
        scale_y = screen_size[1] / display_size[1]
        scaled_mouse = (mouse_pos[0] * scale_x, mouse_pos[1] * scale_y)

        # Calculate the actual position of the buy button on screen
        screen_buy_rect = pygame.Rect(
            pos[0] + self.buy_rect.x,
            pos[1] + self.bounce_offset + self.buy_rect.y,
            self.buy_rect.width,
            self.buy_rect.height
        )
        return screen_buy_rect.collidepoint(scaled_mouse)

    def is_tile_hovered(self, pos):
        """Check if mouse is over the tile but not the buy button"""
        mouse_pos = pygame.mouse.get_pos()
        # Scale mouse position from display (800x600) to internal screen (400x300)
        display_size = self.game.displayed_screen.get_size()
        screen_size = self.game.screen.get_size()
        scale_x = screen_size[0] / display_size[0]
        scale_y = screen_size[1] / display_size[1]
        scaled_mouse = (mouse_pos[0] * scale_x, mouse_pos[1] * scale_y)

        # Define the tile rectangle (same size as the base surface), accounting for bounce offset
        tile_rect = pygame.Rect(pos[0], pos[1] + self.bounce_offset, 200, 60)

        # Check if mouse is over the tile but not over the buy button
        return tile_rect.collidepoint(scaled_mouse) and not self.is_buy_hovered_at_pos(pos)

    def update_hover_state(self, pos):
        """Update the hover state and manage info panel"""
        was_hovered = self.hovered
        self.hovered = self.is_tile_hovered(pos)

        if self.hovered and not was_hovered:
            # Mouse just entered the tile area (not buy button)
            self.create_info_panel()
        elif not self.hovered and was_hovered:
            # Mouse just left the tile area
            self.info_panel = None

    def mouse_over(self, pos, size):
        mouse_pos = pygame.mouse.get_pos()
        rect = pygame.Rect(pos, size)
        return rect.collidepoint(mouse_pos)

    def start_animation(self):
        self.animation_started = True
        self.animation_time = -self.start_delay  # Negative for delay

    def buy(self):
        """Perform the purchase if player has enough currency"""
        player = self.game.player

        # Determine price and item from self.trades
        if isinstance(self.trades, dict):
            price = self.trades.get('price', 0)
            item = self.trades.get('item')
        else:
            # Fallback if trades is not a dict
            price = 0
            item = self.trades

        if player.currency >= price:
            player.currency -= price
            if item:
                # Add to player inventory
                item_name = getattr(item, 'name', 'Item')
                player.inventory[item_name] = item

                if hasattr(item, 'attribute_values'):
                    # Apply attributes from the item to the player
                    player.add_attributes(item.attribute_values)

                print(f"Bought {item_name}! Remaining currency: {player.currency}")
                return True
        else:
             print(f"Not enough currency! Need {price}, have {player.currency}")

        return False

    def create_info_panel(self):
        """Create an info panel with item details"""
        # Get the item object from trades
        if isinstance(self.trades, dict) and 'item' in self.trades:
            item = self.trades['item']
        else:
            item = self.trades  # Assume it's directly an item object

        if hasattr(item, 'name') and hasattr(item, 'description'):
            # Create a surface for the info panel
            font = pygame.font.Font(self.game.fonts["Pixel"], 12)
            title_font = pygame.font.Font(self.game.fonts["Pixel"], 14)

            padding = 12
            line_height = 18
            label_width = 85
            panel_width = 360
            max_value_width = panel_width - padding * 2 - label_width

            # Prepare text lines with wrapped text
            lines = []

            # Name
            name_lines = self.wrap_text(item.name, title_font, max_value_width)
            for i, line in enumerate(name_lines):
                lines.append(("Name:" if i == 0 else "", line, title_font))

            # Description
            desc_lines = self.wrap_text(item.description, font, max_value_width)
            for i, line in enumerate(desc_lines):
                lines.append(("Description:" if i == 0 else "", line, font))

            # Add attributes
            if hasattr(item, 'attribute_values') and item.attribute_values:
                lines.append(("Attributes:", "", font))
                for attr_name, attr_value in item.attribute_values.items():
                    if attr_name not in ["name", "description"]:
                        attr_text = f"{attr_name}: {attr_value}"
                        attr_lines = self.wrap_text(attr_text, font, max_value_width)
                        for j, line in enumerate(attr_lines):
                            lines.append(("", f"  {line}", font))

            panel_height = len(lines) * line_height + 2 * padding

            self.info_panel = {
                'surface': pygame.Surface((panel_width, panel_height), pygame.SRCALPHA),
                'lines': lines,
                'rect': pygame.Rect(0, 0, panel_width, panel_height),
                'padding': padding,
                'line_height': line_height,
                'label_width': label_width
            }

            # Draw the panel background
            panel_surf = self.info_panel['surface']
            pygame.draw.rect(panel_surf, (20, 20, 20, 245), panel_surf.get_rect(), border_radius=10)
            pygame.draw.rect(panel_surf, (150, 150, 150), panel_surf.get_rect(), 2, border_radius=10)

            # Draw the text
            in_label_block = False
            for i, (label, value, font_obj) in enumerate(lines):
                y_pos = padding + i * line_height
                if label:
                    label_text = font_obj.render(label, True, (255, 200, 50))
                    panel_surf.blit(label_text, (padding, y_pos))
                    # Only start a label block if there's a value to wrap on the same/next lines
                    in_label_block = True if value else False

                if value:
                    value_text = font_obj.render(value, True, (240, 240, 240))
                    x_pos = padding
                    if label:
                        x_pos += label_width
                    elif in_label_block:
                        x_pos += label_width

                    if value.startswith("  "): # Attribute indentation (already has spaces)
                        x_pos = padding

                    panel_surf.blit(value_text, (x_pos, y_pos))

    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within a specified width"""
        if not text:
            return [""]

        # First, check if the whole text fits in one line
        if font.size(text)[0] <= max_width:
            return [text]

        words = text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            # Test adding the next word to the current line
            test_line = current_line + " " + word if current_line else word
            text_width = font.size(test_line)[0]

            if text_width <= max_width:
                # Word fits in current line
                current_line = test_line
            else:
                # Word doesn't fit, so finalize current line and start new one
                if current_line:
                    lines.append(current_line)

                # If the single word is too long for the entire width, split it
                if font.size(word)[0] > max_width:
                    # Split the long word into smaller chunks
                    start = 0
                    while start < len(word):
                        # Find the longest substring that fits
                        end = start + 1
                        while end <= len(word) and font.size(word[start:end])[0] <= max_width:
                            end += 1

                        # Add the chunk to lines (adjust end index)
                        if end > start + 1:
                            lines.append(word[start:end-1])
                            start = end - 1
                        else:
                            # If even one character doesn't fit, just add it anyway
                            lines.append(word[start:start+1])
                            start += 1
                    current_line = ""
                else:
                    # The word becomes the start of the next line
                    current_line = word

        # Add the last line if there's anything remaining
        if current_line:
            lines.append(current_line)

        return lines if lines else [""]

    def update(self, dt):
        if not self.animation_started:
            return

        self.animation_time += dt

        if self.animation_time < 0:
            # Still in delay phase
            self.bounce_offset = -100  # Start well above target
            return

        if self.animation_time >= self.animation_duration:
            # Animation complete
            self.bounce_offset = 0
            return

        # Normalize time to 0-1 range (excluding delay)
        t = self.animation_time / self.animation_duration

        # Start at -100 (above), end at 0 (target position)
        # Add a bounce effect using a damped oscillation
        start_offset = -100

        # Ease out with bounce: overshoot then settle
        # Using a combination of ease-out and bounce
        if t < 0.7:
            # First phase: drop down with easing
            progress = t / 0.7
            # Ease out quad
            eased = 1 - (1 - progress) * (1 - progress)
            self.bounce_offset = start_offset * (1 - eased)
        else:
            # Second phase: bounce oscillation
            bounce_progress = (t - 0.7) / 0.3
            # Damped sine wave for bounce
            amplitude = 15 * (1 - bounce_progress)  # Decreasing amplitude
            frequency = 4  # Number of bounces
            self.bounce_offset = amplitude * math.sin(bounce_progress * frequency * math.pi)

    def draw(self, screen, pos):
        # Update hover state before drawing
        self.update_hover_state(pos)

        self.pos = (pos[0], pos[1] + self.bounce_offset)
        draw_pos = self.pos

        # Draw base surface
        screen.blit(self.base_surface, draw_pos)

        # Draw buy button with hover effect
        font = pygame.font.Font(self.game.fonts["Pixel"], 12)

        if self.is_buy_hovered():
            actual_buy_rect = pygame.Rect(
                draw_pos[0] + self.buy_rect.x,
                draw_pos[1] + self.buy_rect.y - 2,
                self.buy_rect.width,
                self.buy_rect.height
            )
            pygame.draw.rect(screen, (50, 50, 50, 200), actual_buy_rect, border_radius=5)
            buy_text = font.render("Buy", False, (100, 255, 100))
        else:
            actual_buy_rect = pygame.Rect(
                draw_pos[0] + self.buy_rect.x,
                draw_pos[1] + self.buy_rect.y,
                self.buy_rect.width,
                self.buy_rect.height
            )
            pygame.draw.rect(screen, (50, 50, 50, 100), actual_buy_rect, border_radius=5)
            buy_text = font.render("Buy", False, (200, 255, 150))

        buy_text_rect = buy_text.get_rect(center=actual_buy_rect.center)
        screen.blit(buy_text, buy_text_rect.topleft)

    def draw_info(self, screen):
        # Draw info panel if hovered (and not hovering over buy button)
        if self.hovered and self.info_panel:
            draw_pos = self.pos
            # Position the info panel above the tile
            panel_x = draw_pos[0]  # Align with the left edge of the tile
            panel_y = draw_pos[1] - self.info_panel['surface'].get_height() - 5  # Above the tile with 5px gap

            # Adjust if panel would go off screen horizontally
            screen_width = screen.get_width()
            panel_width = self.info_panel['surface'].get_width()
            if panel_x + panel_width > screen_width:
                # Position to align with the right edge of the tile if it would go off the right edge
                panel_x = draw_pos[0] + 200 - panel_width  # Align with right edge of tile (200 is tile width)

            # Ensure panel doesn't go off the left edge of the screen
            if panel_x < 0:
                panel_x = 5  # Small margin from left edge

            # Adjust if panel would go off screen vertically (above)
            screen_height = screen.get_height()
            panel_height = self.info_panel['surface'].get_height()
            if panel_y < 0:
                # Position below the tile if it would go above the screen
                panel_y = draw_pos[1] + 60 + 5  # Below the tile (60 is tile height) with 5px gap

            screen.blit(self.info_panel['surface'], (panel_x, panel_y))
