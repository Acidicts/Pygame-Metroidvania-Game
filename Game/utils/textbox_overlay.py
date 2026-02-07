import pygame

class TextOverlay:
    def __init__(self, game):
        self.game = game
        self.text_overlay = ""
        self.text_overlay_show = True

        font_config = self.game.fonts.get("Pixel", "Pixel")
        font_size = 24
        if isinstance(font_config, str):
            if font_config.endswith(".ttf"):
                self.font = pygame.font.Font(font_config, font_size)
            else:
                self.font = pygame.font.SysFont(font_config, font_size)
        else:
            self.font = font_config

        self.typewriter_text = ""
        self.current_typewriter_text = ""
        self.typewriter_index = 0
        self.typewriter_timer = 0
        self.typewriter_speed = 0.05
        self.typewriter_finished = True
        self.input_cooldown = 0.0

    def handle_input(self):
        keys = pygame.key.get_pressed()

        if self.input_cooldown > 0:
            return True

        if keys[pygame.K_ESCAPE]:
            self.input_cooldown = 0.2
            if not self.typewriter_finished:
                self.current_typewriter_text = self.typewriter_text
                self.typewriter_index = len(self.typewriter_text)
                self.typewriter_finished = True
                return True
            else:
                self.text_overlay = ""
                self.game.hud.text_overlay = ""
                self.game.hud.text_overlay_show = False
                self.game.player.attributes["movable"] = True
                self.reset_typewriter()
                return False

        return True

    def reset_typewriter(self):
        self.typewriter_text = ""
        self.current_typewriter_text = ""
        self.typewriter_index = 0
        self.typewriter_timer = 0
        self.typewriter_finished = True

    def set_text(self, text):
        self.typewriter_text = text
        self.current_typewriter_text = ""
        self.typewriter_index = 0
        self.typewriter_timer = 0
        self.typewriter_finished = False

        if not text:
            self.typewriter_finished = True

    def update(self, dt):
        if self.input_cooldown > 0:
            self.input_cooldown -= dt

        if self.typewriter_text and not self.typewriter_finished:
            self.typewriter_timer += dt
            if self.typewriter_timer >= self.typewriter_speed:
                chars_to_advance = int(self.typewriter_timer // self.typewriter_speed)
                self.typewriter_timer %= self.typewriter_speed

                self.typewriter_index += chars_to_advance

                if self.typewriter_index >= len(self.typewriter_text):
                    self.typewriter_index = len(self.typewriter_text)
                    self.typewriter_finished = True

                self.current_typewriter_text = self.typewriter_text[:self.typewriter_index]

    def _wrap_text(self, text, font, max_width):
        if not text:
            return []

        words = text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + " " + word if current_line else word
            test_width, _ = font.size(test_line)

            if test_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def draw(self, screen, show):
        text_box_width = int(screen.get_width() * 0.8) # Wider box
        text_box_height = screen.get_height() // 4

        text_box = pygame.surface.Surface((text_box_width, text_box_height), pygame.SRCALPHA)

        rect_with_rounded_corners = pygame.Rect(4, 4, text_box_width-8, text_box_height-8)
        rect_with_rounded_corners_padded_glow = pygame.Rect(0, 0, text_box_width, text_box_height)
        pygame.draw.rect(text_box, (0, 0, 0, 100), rect_with_rounded_corners, border_radius=10)
        pygame.draw.rect(text_box, (0, 0, 0, 200), rect_with_rounded_corners, border_radius=10, width=2)
        pygame.draw.rect(text_box, (255, 255, 255, 100), rect_with_rounded_corners_padded_glow, border_radius=10, width=2)
        pygame.draw.rect(text_box, (255, 255, 255, 200), rect_with_rounded_corners_padded_glow, border_radius=10, width=1)

        if show and (self.typewriter_text or self.text_overlay):
            full_text = self.typewriter_text if self.typewriter_text else self.text_overlay

            if full_text:
                location = ((screen.get_width() - text_box_width) // 2, screen.get_height() - text_box_height - 40)

                max_text_width = text_box_width - 40
                wrapped_lines = self._wrap_text(full_text, self.font, max_text_width)

                y_offset = 20
                line_spacing = self.font.get_linesize()

                if self.typewriter_text:
                    chars_to_show = self.typewriter_index
                else:
                    chars_to_show = len(full_text)

                current_char_count = 0

                for line in wrapped_lines:
                    if current_char_count >= chars_to_show:
                        break

                    line_len = len(line)
                    remaining_chars = chars_to_show - current_char_count

                    if remaining_chars >= line_len:
                        text_to_render = line
                    else:
                        text_to_render = line[:remaining_chars]

                    if text_to_render:
                        text_surface = self.font.render(text_to_render, True, (255, 255, 255))
                        text_box.blit(text_surface, (20, y_offset))

                    y_offset += line_spacing
                    if y_offset + line_spacing > text_box_height - 10:
                        break

                    current_char_count += line_len
                    if current_char_count < len(full_text) and full_text[current_char_count] == " ":
                        current_char_count += 1

                screen.blit(text_box, location)