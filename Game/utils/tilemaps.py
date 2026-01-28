import pygame

from Game.utils.config import *
from Game.utils.spritegroup import SpriteGroup

AUTOTILE_MAP = {
    tuple(sorted([(1, 0), (0, 1)])): 0,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
    tuple(sorted([(-1, 0), (0, 1)])): 2,
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3,
    tuple(sorted([(-1, 0), (0, -1)])): 4,
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,
    tuple(sorted([(1, 0), (0, -1)])): 6,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,
    tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])): 8
}

NEIGHBOR_OFFSET = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
PHYSICS_TILES = ['solid']

scale_sizing = {
    "cave": {
        "platform": {
            "0": (36, 32),
            "1": (64, 16),
            "2": (103, 32),
            "3": (32, 16),
            "4": (16, 16),
            "5": (32, 16),
            "6": (16, 16),
            "7": (32, 16),
            "8": (32, 32),
        },
    },
    "mossy": {
        "platform": {
            "0": (32, 32),
            "1": (64, 16),
            "2": (96, 32),
            "3": (32, 16),
            "4": (16, 16),
            "5": (32, 16),
            "6": (16, 16),
            "7": (32, 16),
            "8": (32, 32),
        },
    }
}

class TileMap:
    def __init__(self, game, tile_size=48, pos=(0, 0), rendered=False, overlay=None):
        self.game = game
        self.tile_size = tile_size
        self.tile_map = {}
        self.off_grid_tiles = []
        self.pos = pygame.math.Vector2(*pos)
        self.rendered = rendered

        self.sensors = {}
        self.enemies = SpriteGroup()
        self.crystals = SpriteGroup()
        self.items = SpriteGroup()
        self.chests = SpriteGroup()
        self.breakables = SpriteGroup()

        self.overlay = overlay

        self.width = 0
        self.height = 0
        self.tile_size = 0

    def load_map(self, p):
        with open(p, 'r') as f:
            data = json.load(f)

        self.width = data['width']
        self.height = data['height']
        self.tile_size = data['tile_size']

        for layer in data['layers']:

            if layer['type'] == 'sensor_layer':
                for sensor in layer['data']:
                    sensor_id = sensor["id"]
                    if sensor_id is not None:
                        self.sensors[sensor_id] = {
                            "type": sensor['type'],
                            'x': float(sensor['x']),
                            'y': float(sensor['y']),
                            'w': float(sensor['w']),
                            'h': float(sensor['h']),
                            'properties': sensor.get('properties', []),
                            'triggered': False,
                            "id": sensor_id
                        }

            if layer['type'] == 'tilelayer':
                for tile in layer['data']:
                    if "repeat" in tile["properties"]:
                        for x in range(tile["w"]):
                            for y in range(tile["h"]):
                                should_render = True
                                if "alternate" in tile["properties"]:
                                    should_render = (x & int(tile["alternate"])) == 0

                                world_x = int(tile['x'] + x)
                                world_y = int(tile['y'] + y)
                                tile_variant = tile["variant"]

                                if should_render:
                                    if tile["render_cut"][0] != 0 and x == tile["w"] - 1:
                                        tile_variant = None

                                    self.tile_map[(world_x, world_y)] = {
                                        'x': world_x,
                                        'y': world_y,
                                        'z': int(tile['z']),
                                        'environment': data['environment'],
                                        'type': tile["type"],
                                        'variant': tile_variant,
                                        'properties': tile["properties"]
                                    }
                                else:
                                    self.tile_map[(world_x, world_y)] = {
                                        'x': world_x,
                                        'y': world_y,
                                        'z': int(tile['z']),
                                        'environment': data['environment'],
                                        'type': tile["type"],
                                        'variant': None,
                                        'properties': tile["properties"]
                                    }

                                if tile_variant is None:
                                    self.tile_map[(world_x, world_y)] = {
                                        'x': world_x,
                                        'y': world_y,
                                        'z': int(tile['z']),
                                        'environment': data['environment'],
                                        'type': tile["type"],
                                        'variant': None,
                                        'properties': tile["properties"]
                                    }

                                if "dark" in tile["properties"] and should_render:
                                    depth = int(tile["dark_depth"])
                                    try:
                                        solid = int(tile["solid_depth"])
                                    except ValueError:
                                        solid = depth
                                    if solid <= depth:
                                        for y1 in range(depth):
                                            tile_x = int(tile['x'] + x)
                                            tile_y = int(tile['y'] + y1)
                                            if (tile_x, tile_y) not in self.tile_map:
                                                if y1 <= solid:
                                                    self.tile_map[(tile_x, tile_y)] = {
                                                        'x': tile_x,
                                                        'y': tile_y,
                                                        'z': int(tile['z']),
                                                        'environment': data['environment'],
                                                        'type': tile["type"],
                                                        'variant': "dark",
                                                        'properties': ["solid"],
                                                    }
                                                else:
                                                    self.tile_map[(tile_x, tile_y)] = {
                                                        'x': tile_x,
                                                        'y': tile_y,
                                                        'z': int(tile['z']),
                                                        'environment': data['environment'],
                                                        'type': tile["type"],
                                                        'variant': "dark",
                                                        'properties': [],
                                                    }
                                    else:
                                        for y1 in range(solid):
                                            tile_x = int(tile['x'] + x)
                                            tile_y = int(tile['y'] + y1)
                                            if (tile_x, tile_y) not in self.tile_map:
                                                if y1 < solid:
                                                    self.tile_map[(tile_x, tile_y)] = {
                                                        'x': tile_x,
                                                        'y': tile_y,
                                                        'z': int(tile['z']),
                                                        'environment': data['environment'],
                                                        'type': tile["type"],
                                                        'variant': None,
                                                        'properties': ["solid"],
                                                    }

                                if tile["solid_depth"] and "dark_depth" not in tile["properties"]:
                                    solid = int(tile["solid_depth"])
                                    for y1 in range(solid):
                                        tile_x = int(tile['x'] + x)
                                        tile_y = int(tile['y'] + y1)
                                        if (tile_x, tile_y) not in self.tile_map:
                                            if y1 < solid:
                                                self.tile_map[(tile_x, tile_y)] = {
                                                    'x': tile_x,
                                                    'y': tile_y,
                                                    'z': int(tile['z']),
                                                    'environment': data['environment'],
                                                    'type': tile["type"],
                                                    'variant': None,
                                                    'properties': ["solid"],
                                                }

                    else:
                        x, y, z = tile['x'], tile['y'], tile['z']
                        self.tile_map[(x, y)] = {
                            'x': int(x),
                            'y': int(y),
                            'z': int(z),
                            'environment': data['environment'],
                            'type': tile["type"],
                            'variant': tile["variant"],
                            'properties': tile["properties"]
                        }

        for pos, tile in self.tile_map.items():
            if 'solid' in tile.get('properties', []):
                pass

        if self.pos.x != 0 or self.pos.y != 0:
            offset_x = int(self.pos.x)
            offset_y = int(self.pos.y)
            new_map = {}
            for (x, y), tile in self.tile_map.items():
                tile['x'] = x + offset_x
                tile['y'] = y + offset_y
                new_map[(tile['x'], tile['y'])] = tile
            self.tile_map = new_map

        for sensor in self.sensors.values():
            sensor['x'] += int(self.pos.x)
            sensor['y'] += int(self.pos.y)

    def get_tiles_around(self, pos):
        x, y = pos
        grid_x = x // self.tile_size
        grid_y = y // self.tile_size

        tiles = {}
        for dx, dy in NEIGHBOR_OFFSET:
            neighbor_pos = (grid_x + dx, grid_y + dy)
            if neighbor_pos in self.tile_map:
                neighbor_tile = self.tile_map[neighbor_pos]

                if neighbor_tile.get('variant') is None:
                    tiles[(dx, dy)] = None
                    continue

                props = neighbor_tile.get('properties', [])
                try:
                    is_solid = ('solid' in props)
                except TypeError:
                    is_solid = False

                if is_solid:
                    tiles[(dx, dy)] = neighbor_tile
                else:
                    tiles[(dx, dy)] = None
            else:
                tiles[(dx, dy)] = None
        return tiles

    def get_tile(self, x, y):
        return self.tile_map.get((x, y), None)

    def render(self, surface, camera_offset, layer):
        camera_offset = pygame.math.Vector2(camera_offset)
        from Game.utils.config import get_config
        config = get_config()
        if config.get("debug", {}).get("show_platform_hitboxes", False):
            print(f"[DEBUG] TileMap.render: tiles={len(self.tile_map)}, layer={layer}, camera_offset={camera_offset}")
        screen_height = config["resolution"][1]

        for tile in self.tile_map.values():
            if tile["variant"] == "dark" or "dark" in tile.get("properties", []):
                x = tile['x'] * self.tile_size - camera_offset.x
                y = (tile['y']) * self.tile_size - camera_offset.y
                height = screen_height - y
                if height > 0:
                    pygame.draw.rect(surface, (0, 0, 0), (x, y, self.tile_size, self.tile_size))

        self.chests.draw(surface, camera_offset)

        self.items.draw(surface, (camera_offset.x, camera_offset.y))

        self.enemies.draw(surface, (camera_offset.x, camera_offset.y))

        self.breakables.draw(surface, (camera_offset.x, camera_offset.y))

        for tile in self.tile_map.values():
            if tile.get("z") != layer:
                continue

            if tile.get("variant") is None:
                continue

            env = tile.get('environment')
            ttype = tile.get('type')
            if tile.get("variant") == "dark":
                continue
            variant = int(tile.get('variant'))

            try:
                img = self.game.assets[env][ttype].get_images_list()[variant]
            except (KeyError, IndexError):
                img = None

            if img is None:
                continue

            try:
                img = pygame.transform.scale(img, (scale_sizing[env][ttype].get(str(variant), (self.tile_size, self.tile_size))))
            except (TypeError, KeyError):
                img = pygame.transform.scale(img, (self.tile_size, self.tile_size))

            world_pos = (tile['x'] * self.tile_size, tile['y'] * self.tile_size)

            screen_pos = (int(world_pos[0] - camera_offset.x), int(world_pos[1] - camera_offset.y))

            surface.blit(img, screen_pos)

        for tile in self.tile_map.values():
            world_pos = (tile['x'] * self.tile_size, tile['y'] * self.tile_size)

            screen_pos = (int(world_pos[0] - camera_offset.x), int(world_pos[1] - camera_offset.y))
            if 'solid' in tile.get('properties', []) and config.get("debug", {}).get("show_platform_hitboxes", False):
                debug_rect = pygame.Rect(
                    screen_pos[0],
                    screen_pos[1],
                    self.tile_size,
                    self.tile_size
                )
                pygame.draw.rect(surface, (0, 255, 0), debug_rect, 1)

        for sensor in self.sensors.values():
            if config.get("debug", {}).get("show_sensors", False):
                rect = pygame.Rect(sensor["x"]*self.tile_size - camera_offset.x, sensor["y"]*self.tile_size - camera_offset.y, sensor["w"]*self.tile_size, sensor["h"]*self.tile_size)
                pygame.draw.rect(surface, (255, 0, 0), rect, 1)

        self.crystals.draw(surface, (camera_offset.x, camera_offset.y))

        if self.overlay and self.rendered:
            overlay_img = pygame.image.load(self.overlay).convert_alpha()
            overlay_img = pygame.transform.scale(overlay_img, (self.width * self.tile_size, self.height * self.tile_size))
            surface.blit(overlay_img, (-camera_offset.x, - camera_offset.y))

    def is_solid(self, pos, offset):
        x = pos[0] // self.tile_size
        y = pos[1] // self.tile_size

        x += offset[0]
        y += offset[1]

        tile = self.tile_map.get((x, y))
        return tile is not None and ("solid" in tile.get('properties', []))

    def update(self, dt):
        self.chests.update(dt)

        self.items.update(dt)

        self.crystals.update(dt)

        self.breakables.update(dt)

        for sensor in self.sensors.values():
            if sensor["type"] == "render":
                rect = pygame.Rect(sensor["x"] * self.tile_size,
                                   sensor["y"] * self.tile_size,
                                   sensor["w"] * self.tile_size,
                                   sensor["h"] * self.tile_size)

                player_in_sensor = rect.colliderect(self.game.player.rect)

                for prop in sensor["properties"]:
                    if "render" in prop and not sensor["triggered"] and "derender" not in prop and "toggle_render" not in prop:
                        map_name = prop.split(":")[1]
                        if player_in_sensor:
                            self.game.tilemap_current = map_name
                            self.game.tilemap = self.game.tilemaps[self.game.tilemap_current]
                            self.game.tilemaps[map_name].rendered = True
                            sensor["triggered"] = True

                    if "derender" in prop and not sensor["triggered"]:
                        map_name = prop.split(":")[1]
                        if player_in_sensor:
                            self.game.tilemap_current = map_name
                            self.game.tilemap = self.game.tilemaps[self.game.tilemap_current]
                            self.game.tilemaps[map_name].rendered = False
                            sensor["triggered"] = True

                    if "toggle_render" in prop and not sensor["triggered"]:
                        map_name = prop.split(":")[1]
                        if player_in_sensor:
                            self.game.tilemaps[map_name].rendered = not self.game.tilemaps[map_name].rendered

                            current_found = False
                            for name, tilemap in self.game.tilemaps.items():
                                if tilemap.rendered:
                                    self.game.tilemap_current = name
                                    self.game.tilemap = tilemap
                                    current_found = True
                                    break

                            if not current_found:
                                pass

                            sensor["triggered"] = True

                if sensor["triggered"] and not player_in_sensor:
                    sensor["triggered"] = False
