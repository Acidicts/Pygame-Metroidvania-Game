import pygame
import os
import sys
from pathlib import Path

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
BACKGROUND_COLOR = (50, 50, 50)
TEXT_COLOR = (220, 220, 220)
HIGHLIGHT_COLOR = (100, 150, 255)
FONT_SIZE = 24
SMALL_FONT_SIZE = 18

class AssetViewer:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Asset Viewer - Pygame Metroidvania")
        self.clock = pygame.time.Clock()
        
        # Font setup
        self.font = pygame.font.SysFont(None, FONT_SIZE)
        self.small_font = pygame.font.SysFont(None, SMALL_FONT_SIZE)
        
        # Gather all assets
        self.asset_paths = self.gather_assets()
        self.asset_surfaces = {}
        self.current_index = 0
        
        # Load all assets as surfaces
        self.load_assets()
        
        # UI elements
        self.scroll_offset = 0
        self.max_visible_items = 15
        self.selected_index = 0
        self.show_details = True
        
    def gather_assets(self):
        """Gather all asset file paths from the Game/assets directory"""
        asset_dir = Path("Game/assets")
        asset_paths = []
        
        # Walk through all subdirectories and collect image files
        for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
            for file_path in asset_dir.rglob(f'*{ext}'):
                asset_paths.append(file_path)
                
        # Also include any JSON files that might define sprite sheets
        for file_path in asset_dir.rglob('*.json'):
            if 'cut_tiles' in str(file_path):  # These are sprite sheet definitions
                asset_paths.append(file_path)
        
        return sorted(asset_paths)
    
    def load_assets(self):
        """Load all asset images as surfaces"""
        for path in self.asset_paths:
            try:
                if path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                    surface = pygame.image.load(str(path))
                    self.asset_surfaces[path] = surface
            except pygame.error:
                print(f"Could not load image: {path}")
    
    def draw_sidebar(self):
        """Draw the sidebar with asset list"""
        sidebar_width = 300
        pygame.draw.rect(self.screen, (40, 40, 40), (0, 0, sidebar_width, SCREEN_HEIGHT))
        
        # Calculate visible range
        start_idx = max(0, self.selected_index - self.max_visible_items // 2)
        end_idx = min(len(self.asset_paths), start_idx + self.max_visible_items)
        
        # Adjust scroll offset if needed
        if self.selected_index < start_idx:
            start_idx = self.selected_index
            end_idx = min(len(self.asset_paths), start_idx + self.max_visible_items)
        elif self.selected_index >= end_idx:
            end_idx = self.selected_index + 1
            start_idx = max(0, end_idx - self.max_visible_items)
        
        # Draw asset list
        y_pos = 20
        for idx in range(start_idx, end_idx):
            asset_path = self.asset_paths[idx]
            text = self.small_font.render(str(asset_path.relative_to(Path("Game/assets"))), True, TEXT_COLOR)
            
            # Highlight selected item
            if idx == self.selected_index:
                highlight_rect = pygame.Rect(10, y_pos - 2, sidebar_width - 20, text.get_height() + 4)
                pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, highlight_rect, border_radius=3)
            
            self.screen.blit(text, (20, y_pos))
            y_pos += text.get_height() + 8
    
    def draw_asset_display(self):
        """Draw the main asset display area"""
        display_area = pygame.Rect(310, 20, SCREEN_WIDTH - 330, SCREEN_HEIGHT - 100)
        
        # Draw border for asset display
        pygame.draw.rect(self.screen, (70, 70, 70), display_area)
        pygame.draw.rect(self.screen, (100, 100, 100), display_area, 2)
        
        if self.asset_paths:
            current_asset = self.asset_paths[self.selected_index]
            
            # Display asset if it's an image
            if current_asset.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                if current_asset in self.asset_surfaces:
                    asset_surface = self.asset_surfaces[current_asset]
                    
                    # Calculate position to center the asset in the display area
                    asset_rect = asset_surface.get_rect()
                    display_center_x = display_area.centerx
                    display_center_y = display_area.centery
                    
                    # Scale down if too large for display area
                    max_width = display_area.width - 40
                    max_height = display_area.height - 100
                    
                    scale_factor = 1.0
                    if asset_rect.width > max_width or asset_rect.height > max_height:
                        width_ratio = max_width / asset_rect.width
                        height_ratio = max_height / asset_rect.height
                        scale_factor = min(width_ratio, height_ratio)
                    
                    if scale_factor != 1.0:
                        new_width = int(asset_rect.width * scale_factor)
                        new_height = int(asset_rect.height * scale_factor)
                        asset_surface_scaled = pygame.transform.scale(asset_surface, (new_width, new_height))
                    else:
                        asset_surface_scaled = asset_surface
                    
                    # Center the scaled asset
                    scaled_rect = asset_surface_scaled.get_rect()
                    scaled_rect.center = (display_center_x, display_center_y - 20)
                    
                    self.screen.blit(asset_surface_scaled, scaled_rect)
                    
                    # Draw asset info
                    if self.show_details:
                        self.draw_asset_info(current_asset, asset_surface, display_area)
    
    def draw_asset_info(self, asset_path, asset_surface, display_area):
        """Draw detailed information about the current asset"""
        y_start = display_area.bottom - 70
        
        # Asset name
        name_text = self.font.render(f"Name: {asset_path.name}", True, TEXT_COLOR)
        self.screen.blit(name_text, (display_area.left + 10, y_start))
        
        # Asset dimensions
        size_text = self.small_font.render(f"Size: {asset_surface.get_width()}x{asset_surface.get_height()}", True, TEXT_COLOR)
        self.screen.blit(size_text, (display_area.left + 10, y_start + 30))
        
        # Asset path
        path_text = self.small_font.render(f"Path: {asset_path.relative_to(Path('Game'))}", True, TEXT_COLOR)
        self.screen.blit(path_text, (display_area.left + 10, y_start + 50))
    
    def draw_controls(self):
        """Draw control instructions at the bottom"""
        controls_text = [
            "CONTROLS:",
            "Arrow Keys: Navigate assets | Space: Toggle details | ESC: Quit"
        ]
        
        y_pos = SCREEN_HEIGHT - 40
        for text in controls_text:
            ctrl_text = self.small_font.render(text, True, (180, 180, 180))
            self.screen.blit(ctrl_text, (20, y_pos))
            y_pos += ctrl_text.get_height() + 5
    
    def handle_events(self):
        """Handle user input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_UP:
                    self.selected_index = max(0, self.selected_index - 1)
                elif event.key == pygame.K_DOWN:
                    self.selected_index = min(len(self.asset_paths) - 1, self.selected_index + 1)
                elif event.key == pygame.K_PAGEUP:
                    self.selected_index = max(0, self.selected_index - 10)
                elif event.key == pygame.K_PAGEDOWN:
                    self.selected_index = min(len(self.asset_paths) - 1, self.selected_index + 10)
                elif event.key == pygame.K_SPACE:
                    self.show_details = not self.show_details
                elif event.key == pygame.K_HOME:
                    self.selected_index = 0
                elif event.key == pygame.K_END:
                    self.selected_index = len(self.asset_paths) - 1
        
        return True
    
    def run(self):
        """Main application loop"""
        running = True
        while running:
            running = self.handle_events()
            
            # Clear screen
            self.screen.fill(BACKGROUND_COLOR)
            
            # Draw UI elements
            self.draw_sidebar()
            self.draw_asset_display()
            self.draw_controls()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    viewer = AssetViewer()
    viewer.run()