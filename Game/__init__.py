from Game.FolderStorage import FolderStorage
from Game.MISC.Items import ItemManager
from Game.Sprites.Enemies.GroundCrawler import GroundCrawler
from Game.utils.camera import Camera
from Game.utils.tilemaps import *
from Game.utils.utils import *
from Game.Sprites.Player import Player
from Game.utils.hud import Hud
from Game.GUIs.Inventory import InventoryScreen

class Game:
    def __init__(self):
        pygame.init()
        self.displayed_screen = pygame.display.set_mode((800, 600))
        self.screen = pygame.surface.Surface((400, 300))

        pygame.display.set_caption("Pygame Metroidvania")

        self.clock = pygame.time.Clock()
        self.running = True

        self.assets = {}

        self.items = ItemManager(self)

        self.camera = Camera(self.screen.get_width(), self.screen.get_height())
        self.tilemaps = {}
        self.screens = FolderStorage()
        self.load()

        self.player = Player(self, position=pygame.Vector2(100, 128))
        self.player_tilemap = self.tilemaps["cave"]

        self.current_bg_colour = pygame.Vector3(self.player_tilemap.bg_colour)
        self.target_bg_colour = pygame.Vector3(self.player_tilemap.bg_colour)
        self.current_tint_colour = pygame.Vector3(self.player_tilemap.tint_colour)
        self.target_tint_colour = pygame.Vector3(self.player_tilemap.tint_colour)

        self._create_vignette_mask()
        self._update_vignette()

        self.screen_focus = None

        self.fonts = {
            "Pixel": "Game/assets/fonts/pixels.ttf",
            "workbench": "Game/assets/fonts/workbench.ttf",
            "Arial": "Arial",
        }

        self.hud = Hud(self)

        self.inventory_screen = InventoryScreen(self)
        self.screens["inventory"]["main"] = self.inventory_screen

        # Initialize text overlay properties
        self.text_overlay = "Sample Text Overlay"
        self.text_overlay_show = True

    def _create_vignette_mask(self):
        size = self.screen.get_size()

        # Create a higher resolution gradient surface for smoother transitions
        grad_size = 1024  # Increased from 512 for more precision
        center = grad_size // 2

        radial_grad = pygame.Surface((grad_size, grad_size), pygame.SRCALPHA)

        # Create a smoother vignette using a quadratic falloff
        for y in range(grad_size):
            for x in range(grad_size):
                # Calculate distance from center
                dx = x - center
                dy = y - center
                distance = (dx * dx + dy * dy) ** 0.5
                max_distance = center

                # Use a quadratic curve for smoother transition
                # This creates a more gradual fall-off than linear
                if distance <= max_distance:
                    norm_dist = distance / max_distance
                    alpha = (norm_dist * norm_dist)
                    alpha = max(0, min(1, alpha ** 1.5))
                    alpha_value = int(alpha * 255)

                    radial_grad.set_at((x, y), (255, 255, 255, alpha_value))
                else:
                    radial_grad.set_at((x, y), (255, 255, 255, 0))

        # Scale the gradient to fit the screen with some padding to ensure coverage
        self.vignette_mask = pygame.transform.smoothscale(radial_grad, (int(size[0] * 2.2), int(size[1] * 2.2)))

        final_mask = pygame.Surface(size, pygame.SRCALPHA)
        mask_rect = self.vignette_mask.get_rect(center=(size[0] // 2, size[1] // 2))
        final_mask.blit(self.vignette_mask, mask_rect)
        self.vignette_mask = final_mask

    def _update_vignette(self):
        self.vignette = self.vignette_mask.copy()
        tint = self.current_tint_colour
        self.vignette.fill((int(tint.x), int(tint.y), int(tint.z)), special_flags=pygame.BLEND_RGBA_MULT)

    def restart(self):
        self.clock = pygame.time.Clock()
        self.running = True

        self.assets = {}

        self.items = ItemManager(self)

        self.camera = Camera(self.screen.get_width(), self.screen.get_height())
        self.tilemaps = {}
        self.screens = FolderStorage()
        self.load()

        self.player = Player(self, position=pygame.Vector2(100, 128))
        self.player_tilemap = self.tilemaps["cave"]

        self.current_bg_colour = pygame.Vector3(self.player_tilemap.bg_colour)
        self.target_bg_colour = pygame.Vector3(self.player_tilemap.bg_colour)
        self.current_tint_colour = pygame.Vector3(self.player_tilemap.tint_colour)
        self.target_tint_colour = pygame.Vector3(self.player_tilemap.tint_colour)

        self._create_vignette_mask()
        self._update_vignette()

        self.screen_focus = None

        self.fonts = {
            "Pixel": "Game/assets/fonts/pixels.ttf",
            "workbench": "Game/assets/fonts/workbench.ttf",
            "Arial": "Arial",
        }

        self.hud = Hud(self)

        self.inventory_screen = InventoryScreen(self)
        self.screens["inventory"]["main"] = self.inventory_screen

        # Initialize text overlay properties
        self.text_overlay = "Sample Text Overlay"
        self.text_overlay_show = True

    def load(self):
        config = get_config()
        tile_size = config.get("tile_size", 32)
        mossy_tile_scale = tile_size / 512.0
        TILE_SCALE = 1
        self.assets = {
            "hud":
                {
                    "heart": {
                        "full": load_image("hud/Heart Container Silver/heart_silver_full.png"),
                        "half": load_image("hud/Heart Container Silver/heart_silver_half.png"),
                        "shine": SpriteSheet("hud/Heart Container Silver/heart_silver_shine_full.png", tile_size=16),
                        "blink": SpriteSheet("hud/Heart Container Silver/heart_silver_blink_full.png", tile_size=16),
                        "empty": load_image("hud/Heart Container General/heart_empty.png"),
                    },
                },
            "cave":
                {
                    "big_rocks": SpriteSheet("cave_tiles/Cave - BigRocks1.png", cut=load_json_as_dict("cut_tiles_json/Cave-BigRocks1.json"), scale=TILE_SCALE),
                    "floor": SpriteSheet("cave_tiles/Cave - Floor.png", cut=load_json_as_dict("cut_tiles_json/Cave-Floor.json"), scale=TILE_SCALE),
                    "platform": SpriteSheet("cave_tiles/Cave - Platforms.png", cut=load_json_as_dict("cut_tiles_json/Cave-Platforms.json"), scale=TILE_SCALE),
                },
            "mossy":
               {
                   "tile_set": SpriteSheet("mossy_tiles/Mossy - TileSet.png", tile_size=512, scale=mossy_tile_scale),
                   "mossy_hills": SpriteSheet("mossy_tiles/Mossy - MossyHills.png", cut=load_json_as_dict("cut_tiles_json/Mossy-MossyHills.json"), scale=TILE_SCALE),
                   "hanging_plants": SpriteSheet("mossy_tiles/Mossy - Hanging Plants.png", cut=load_json_as_dict("cut_tiles_json/Mossy-HangingPlants.json"), scale=TILE_SCALE),
                   "platform": SpriteSheet("mossy_tiles/Mossy - FloatingPlatforms.png", cut=load_json_as_dict("cut_tiles_json/Mossy-FloatingPlatforms.json"), scale=TILE_SCALE),
               }
        }

        positions = config.get("tilemap_positions", {})
        
        self.tilemaps["cave"] = TileMap(self, tile_size=tile_size, pos=positions.get("cave", (0, 0)), rendered=True)
        self.tilemaps["mossy"] = TileMap(self, tile_size=tile_size, pos=positions.get("mossy", (0, 0)), rendered=False)

        maps = get_config()["tilemaps"]

        for name, tilemaps in self.tilemaps.items():
            tilemaps.load_map("Game/assets/" + maps[name])

        try:
            cfg = get_config()
        except Exception:
            cfg = {}
        if cfg.get("debug", {}).get("show_platform_hitboxes", False):
            for name, tilemap in self.tilemaps.items():
                print(f"[DEBUG] map '{name}' loaded tiles={len(tilemap.tile_map)}")
                samples = list(tilemap.tile_map.items())[:5]
                for k, v in samples:
                    print(f"  sample tile key={k} -> {v}")
                if len(tilemap.tile_map) == 0:
                    print(f"  WARNING: tile_map for '{name}' is empty")

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    # Handle restart when player is dead
                    if event.key == pygame.K_SPACE and self.hud.can_restart:
                        self.restart()
                    if event.key == pygame.K_TAB:
                        # Prevent opening inventory if interacting with an NPC/Shop
                        can_open = True
                        if not self.inventory_screen.active:
                            for category in self.screens.values():
                                for screen_obj in category.values():
                                    if hasattr(screen_obj, 'bound_sprite') and screen_obj.bound_sprite:
                                        if screen_obj.bound_sprite.interacted:
                                            can_open = False
                                            break

                        if can_open:
                            self.inventory_screen.toggle()
                    if event.key == pygame.K_ESCAPE and self.inventory_screen.active:
                        self.inventory_screen.toggle()

            fade_speed = 5.0 * dt
            if self.current_bg_colour.distance_to(self.target_bg_colour) > 0.1:
                self.current_bg_colour = self.current_bg_colour.lerp(self.target_bg_colour, min(1.0, fade_speed))
            else:
                self.current_bg_colour = pygame.Vector3(self.target_bg_colour)

            if self.current_tint_colour.distance_to(self.target_tint_colour) > 0.1:
                self.current_tint_colour = self.current_tint_colour.lerp(self.target_tint_colour, min(1.0, fade_speed))
                self._update_vignette()
            else:
                if self.current_tint_colour != self.target_tint_colour:
                    self.current_tint_colour = pygame.Vector3(self.target_tint_colour)
                    self._update_vignette()

            self.screen.fill((int(self.current_bg_colour.x), int(self.current_bg_colour.y), int(self.current_bg_colour.z)))

            self.camera.update(self.player)

            for tilemap in self.tilemaps.values():
                tilemap.update(dt)
                if tilemap.rendered:
                    for layer in tilemap._layers:
                        tilemap.render(self.screen, self.camera.offset, layer)

            # Update and draw player and enemies to the off-screen surface
            self.player.update(dt)

            # Update and draw enemies
            for tilemap in self.tilemaps.values():
                if tilemap.rendered:
                    tilemap.enemies.update(dt)

            # Draw player, enemies, HUD, then vignette overlay
            self.player.draw(self.screen, self.camera.offset)

            # Draw enemies
            for tilemap in self.tilemaps.values():
                if tilemap.rendered:
                    tilemap.enemies.draw(self.screen, self.camera.offset)


            self.screen.blit(self.vignette, (0, 0))

            # Scale the off-screen buffer to the displayed screen
            surf = self.displayed_screen
            self.displayed_screen.blit(pygame.transform.scale(self.screen, (surf.get_width(), surf.get_height())), (0, 0))

            # Update and draw screens directly to the displayed screen
            for category in self.screens.values():
                for screen_obj in category.values():
                    if hasattr(screen_obj, 'update'):
                        screen_obj.update(dt)
                    if hasattr(screen_obj, 'draw'):
                        screen_obj.draw(self.displayed_screen)

            self.hud.update(dt)
            self.hud.draw(self.displayed_screen)

            pygame.display.flip()

        pygame.quit()
