import pygame
from Game.GUIs.Screen import Screen

class InventoryScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.active = False
        self.font = pygame.font.Font(self.game.fonts["Pixel"], 16)
        self.title_font = pygame.font.Font(self.game.fonts["Pixel"], 48)
        self.item_font = pygame.font.Font(self.game.fonts["Pixel"], 24)

        self.selected_index = 0
        self.was_key_pressed = {pygame.K_UP: False, pygame.K_DOWN: False}

    def toggle(self):
        self.active = not self.active
        if self.active:
            self.game.player.attributes["movable"] = False
            self.selected_index = 0
            # Update max_opened_progress based on display size if needed
            # For Inventory it's mostly static positioning
        else:
            self.game.player.attributes["movable"] = True

    def update(self, dt):
        if not self.active:
            return

        keys = pygame.key.get_pressed()
        inventory_items = list(self.game.player.inventory.keys())

        if not inventory_items:
            return

        # Up key
        if keys[pygame.K_UP] and not self.was_key_pressed[pygame.K_UP]:
            self.selected_index = (self.selected_index - 1) % len(inventory_items)
        # Down key
        if keys[pygame.K_DOWN] and not self.was_key_pressed[pygame.K_DOWN]:
            self.selected_index = (self.selected_index + 1) % len(inventory_items)

        self.was_key_pressed[pygame.K_UP] = keys[pygame.K_UP]
        self.was_key_pressed[pygame.K_DOWN] = keys[pygame.K_DOWN]

    def draw(self, screen):
        if not self.active:
            return

        # Background dimming
        surf = pygame.surface.Surface(screen.get_size(), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 200))
        screen.blit(surf, (0, 0))

        # Main Panel - center it on the screen
        screen_size = screen.get_size()
        panel_width, panel_height = 640, 440 # Doubled dimensions
        panel_rect = pygame.Rect((screen_size[0] - panel_width) // 2, (screen_size[1] - panel_height) // 2, panel_width, panel_height)
        pygame.draw.rect(screen, (30, 30, 30), panel_rect, border_radius=20)
        pygame.draw.rect(screen, (100, 100, 100), panel_rect, 4, border_radius=20)

        # Draw Inventory Title
        title_text = self.title_font.render("Inventory", True, (255, 200, 50))
        title_rect = title_text.get_rect(centerx=screen_size[0] // 2, top=panel_rect.top + 20)
        screen.blit(title_text, title_rect)

        # List items
        inventory = self.game.player.inventory
        if not inventory:
            empty_text = self.item_font.render("Inventory is empty", True, (150, 150, 150))
            empty_rect = empty_text.get_rect(center=(screen_size[0] // 2, panel_rect.centery))
            screen.blit(empty_text, empty_rect)
        else:
            item_list_x = panel_rect.left + 40
            item_list_y = panel_rect.top + 100
            item_height = 50

            inventory_items = list(inventory.items())

            # Draw Item List
            for i, (name, item) in enumerate(inventory_items):
                color = (255, 255, 255) if i == self.selected_index else (120, 120, 120)
                prefix = "> " if i == self.selected_index else "  "
                item_text = self.item_font.render(f"{prefix}{name}", True, color)
                screen.blit(item_text, (item_list_x, item_list_y + i * item_height))

            # Draw Detailed View of Selected Item
            if self.selected_index < len(inventory_items):
                selected_name, selected_item = inventory_items[self.selected_index]

                detail_x = panel_rect.left + 280
                detail_y = panel_rect.top + 100

                # Draw small divider
                pygame.draw.line(screen, (60, 60, 60), (panel_rect.left + 260, panel_rect.top + 100), (panel_rect.left + 260, panel_rect.bottom - 80), 2)

                # Show Stats
                if hasattr(selected_item, 'description'):
                    # We can use a simpler wrap for the inventory view
                    desc_text = self.font.render("Description:", True, (255, 200, 50))
                    screen.blit(desc_text, (detail_x, detail_y))

                    # Very basic wrapping by splitting into lines if needed
                    words = selected_item.description.split(' ')
                    lines = []
                    current_line = ""
                    # Doubled width for high res
                    for word in words:
                        test_line = current_line + " " + word if current_line else word
                        if self.font.size(test_line)[0] < 320:
                            current_line = test_line
                        else:
                            lines.append(current_line)
                            current_line = word
                    lines.append(current_line)

                    for row, line in enumerate(lines):
                        line_surf = self.font.render(line, True, (200, 200, 200))
                        screen.blit(line_surf, (detail_x, detail_y + 30 + row * 24))

                # Attributes section
                if hasattr(selected_item, 'attribute_values') and selected_item.attribute_values:
                    attr_y = detail_y + 160
                    attr_title = self.font.render("Attributes:", True, (255, 200, 50))
                    screen.blit(attr_title, (detail_x, attr_y))

                    for row, (attr, val) in enumerate(selected_item.attribute_values.items()):
                        if attr not in ["name", "description"]:
                            attr_text = self.font.render(f"{attr}: {val}", True, (150, 255, 150))
                            screen.blit(attr_text, (detail_x + 10, attr_y + 30 + row * 24))

        # Controls Hint
        hint_text = self.font.render("[TAB/ESC] Close    [UP/DOWN] Select", True, (100, 100, 100))
        hint_rect = hint_text.get_rect(centerx=screen_size[0] // 2, bottom=panel_rect.bottom - 20)
        screen.blit(hint_text, hint_rect)
