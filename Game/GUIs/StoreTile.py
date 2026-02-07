import pygame
import math

class StoreTile:
    def __init__(self, game, data, index=0):
        self.pos = (0, 0)  # Will be set when drawing
        self.game = game
        self.trades = data  # Must be set before create_image()
        self.image = self.create_image()

        self.index = index

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

        # Item name on top
        item_text = font.render(str(self.trades['item']), False, (255, 255, 255))
        item_rect = item_text.get_rect(topleft=(8, 8))
        self.base_surface.blit(item_text, item_rect)

        # Price on bottom left
        price_text = self.num_font.render(str(self.trades['price']), False, (255, 255, 255))
        price_rect = price_text.get_rect(bottomleft=(8, 52))
        self.base_surface.blit(price_text, price_rect)

        # Buy button area (bottom right corner)
        self.buy_rect = pygame.Rect(140, 35, 55, 20)

        # Create final image
        self.image = self.base_surface.copy()
        return self.image

    def is_buy_hovered(self):
        """Check if mouse is over the buy button"""
        mouse_pos = pygame.mouse.get_pos()
        # Scale mouse position from display (800x600) to internal screen (400x300)
        display_size = self.game.displayed_screen.get_size()
        screen_size = self.game.screen.get_size()
        scale_x = screen_size[0] / display_size[0]
        scale_y = screen_size[1] / display_size[1]
        scaled_mouse = (mouse_pos[0] * scale_x, mouse_pos[1] * scale_y)

        # self.pos already includes bounce_offset
        screen_buy_rect = pygame.Rect(
            self.pos[0] + self.buy_rect.x,
            self.pos[1] + self.buy_rect.y,
            self.buy_rect.width,
            self.buy_rect.height
        )
        return screen_buy_rect.collidepoint(scaled_mouse)

    def mouse_over(self, pos, size):
        mouse_pos = pygame.mouse.get_pos()
        rect = pygame.Rect(pos, size)
        return rect.collidepoint(mouse_pos)

    def start_animation(self):
        self.animation_started = True
        self.animation_time = -self.start_delay  # Negative for delay

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
        self.pos = (pos[0], pos[1] + self.bounce_offset)
        draw_pos = self.pos

        # Draw base surface
        screen.blit(self.base_surface, draw_pos)

        # Draw buy button with hover effect
        font = pygame.font.Font(self.game.fonts["Pixel"], 12)

        # Calculate the actual position of the buy button on screen


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
