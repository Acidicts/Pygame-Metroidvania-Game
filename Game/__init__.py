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

        # Camera should use the in-game render surface size so offsets align
        self.camera = Camera(self.screen.get_width(), self.screen.get_height())
        self.tilemaps = {}
        self.load()

        self.player = Player(self, position=pygame.Vector2(100, 100))


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
        self.tilemaps["mossy"] = TileMap(self, tile_size=tile_size, pos=(30, 0), rendered=False)

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

            self.screen.fill((0, 0, 0))

            self.camera.update(self.player)

            # optional debug prints
            try:
                cfg = get_config()
            except Exception:
                cfg = {}
            if cfg.get("debug", {}).get("show_collision_boxes", False):
                print(f"[DEBUG] camera.offset={self.camera.offset}, player.rect={self.player.rect}")


            for tilemap in self.tilemaps.values():
                tilemap.update(dt)
                if tilemap.rendered:
                    # render all layers present in the tilemap (z values can vary)
                    layers = sorted({tile.get('z', 0) for tile in tilemap.tile_map.values()})
                    for layer in layers:
                        tilemap.render(self.screen, self.camera.offset, layer)

            self.player.draw(self.screen, self.camera.offset)
            self.player.update(dt)

            self.displayed_screen.fill((0, 0, 0))
            surf = self.displayed_screen
            self.displayed_screen.blit(pygame.transform.scale(self.screen, (surf.get_width(), surf.get_height())), (0, 0))

            pygame.display.flip()

        pygame.quit()
