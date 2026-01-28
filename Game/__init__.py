import pygame

from .utils.camera import Camera
from .utils.tilemaps import *
from .utils.utils import *
from .Sprites.Player import Player

class Game:
    def __init__(self):
        pygame.init()
        self.displayed_screen = pygame.display.set_mode((800, 600))
        self.screen = pygame.surface.Surface((400, 300))

        pygame.display.set_caption("Pygame Metroidvania")

        self.clock = pygame.time.Clock()
        self.running = True

        self.assets = {}

        self.camera = Camera(self.screen.get_width(), self.screen.get_height())
        self.tilemaps = {}
        self.load()

        self.player = Player(self, position=pygame.Vector2(100, 50))
        self.player_tilemap = self.tilemaps["cave"]
        self.current_bg_colour = pygame.Vector3(self.player_tilemap.bg_colour)
        self.target_bg_colour = pygame.Vector3(self.player_tilemap.bg_colour)
        self.current_tint_colour = pygame.Vector3(self.player_tilemap.tint_colour)
        self.target_tint_colour = pygame.Vector3(self.player_tilemap.tint_colour)

        self._create_vignette_mask()
        self._update_vignette()

    def _create_vignette_mask(self):
        self.vignette_mask = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        for y in range(self.vignette_mask.get_height()):
            for x in range(self.vignette_mask.get_width()):
                # Distance from center
                dist = pygame.Vector2(x, y).distance_to(pygame.Vector2(self.vignette_mask.get_width() / 2, self.vignette_mask.get_height() / 2))
                # Normalize distance (0 to 1)
                norm_dist = dist / (pygame.Vector2(0, 0).distance_to(pygame.Vector2(self.vignette_mask.get_width() / 2, self.vignette_mask.get_height() / 2)))
                # Weak vignette: start appearing after 0.4 distance
                alpha = int(max(0, (norm_dist - 0.4) * 2) * 255)
                alpha = min(alpha, 150) # Cap alpha to keep it "weak"
                self.vignette_mask.set_at((x, y), (255, 255, 255, alpha))

    def _update_vignette(self):
        self.vignette = self.vignette_mask.copy()
        tint = self.current_tint_colour
        self.vignette.fill((int(tint.x), int(tint.y), int(tint.z)), special_flags=pygame.BLEND_RGBA_MULT)


    def load(self):

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
                    "big_rocks": SpriteSheet("cave_tiles/Cave - BigRocks1.png", cut=load_json_as_dict("cut_tiles_json/Cave-BigRocks1.json")),
                    "floor": SpriteSheet("cave_tiles/Cave - Floor.png", cut=load_json_as_dict("cut_tiles_json/Cave-Floor.json")),
                    "platform": SpriteSheet("cave_tiles/Cave - Platforms.png", cut=load_json_as_dict("cut_tiles_json/Cave-Platforms.json")),
                },
           "mossy":
               {
                   "platform": SpriteSheet("mossy_tiles/Mossy - FloatingPlatforms.png", tile_size=512),
               }
        }

        config = get_config()
        tile_size = config.get("tile_size", 32)
        self.tilemaps["cave"] = TileMap(self, tile_size=tile_size, pos=(0, 0), rendered=True)
        self.tilemaps["mossy"] = TileMap(self, tile_size=tile_size, pos=(30, -3), rendered=False)

        maps = get_config()["tilemaps"]

        for name, tilemaps in self.tilemaps.items():
            tilemaps.load_map("Game/assets/" + maps[name])

        # Debug: report loaded tile counts and sample tiles
        try:
            cfg = get_config()
        except Exception:
            cfg = {}
        if cfg.get("debug", {}).get("show_platform_hitboxes", False):
            for name, tilemap in self.tilemaps.items():
                print(f"[DEBUG] map '{name}' loaded tiles={len(tilemap.tile_map)}")
                # show up to 5 sample tiles
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

            self.player.update(dt)
            new_tilemap_name, new_tilemap = find_tilemap_for_rect(self.tilemaps, self.player.rect)
            if new_tilemap and new_tilemap != self.player_tilemap:
                self.player_tilemap = new_tilemap
                self.target_bg_colour = pygame.Vector3(self.player_tilemap.bg_colour)
                self.target_tint_colour = pygame.Vector3(self.player_tilemap.tint_colour)

            # Lerp colors
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

            try:
                cfg = get_config()
            except Exception:
                cfg = {}
            if cfg.get("debug", {}).get("show_collision_boxes", False):
                print(f"[DEBUG] camera.offset={self.camera.offset}, player.rect={self.player.rect}")


            for tilemap in self.tilemaps.values():
                tilemap.update(dt)
                if tilemap.rendered:
                    layers = sorted({tile.get('z', 0) for tile in tilemap.tile_map.values()})
                    for layer in layers:
                        tilemap.render(self.screen, self.camera.offset, layer)

            self.player.draw(self.screen, self.camera.offset)

            self.screen.blit(self.vignette, (0, 0))

            self.displayed_screen.fill((0, 0, 0))
            surf = self.displayed_screen
            self.displayed_screen.blit(pygame.transform.scale(self.screen, (surf.get_width(), surf.get_height())), (0, 0))

            pygame.display.flip()

        pygame.quit()
