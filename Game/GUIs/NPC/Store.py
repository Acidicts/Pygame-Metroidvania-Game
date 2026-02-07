from Game.GUIs.Screen import Screen
from Game.GUIs.StoreTile import StoreTile

class StoreScreen(Screen):
    def __init__(self, game, bound_sprite=None):
        super().__init__(game, bound_sprite)

        self.opened = False
        self.opened_progress = 0
        self.max_opened_progress = self.game.screen.get_size()[1] - 50

        self.tiles = {}
        self.tiles_loaded = False

    def on_open(self, dt):
        self.opened = True
        while self.opened and self.opened_progress < self.max_opened_progress:
            self.opened_progress += 500 * dt
            if self.opened_progress > self.max_opened_progress:
                self.opened_progress = self.max_opened_progress

        # Start tile animations after store opens
        if not self.tiles_loaded:
            self.load()
            self.tiles_loaded = True
            for tile in self.tiles.values():
                tile.start_animation()

    def load(self):
        for i, data in enumerate(self.bound_sprite.data["trades"]):
            print(data)
            self.tiles[i] = StoreTile(self.game, data, index=i)

    def draw_tiles(self):
        for i, tile in enumerate(self.tiles.values()):
            pos = (self.game.screen.get_size()[0] // 2, 50 + i * 70)
            tile.draw(self.game.screen, (pos[0], pos[1] + self.game.screen.get_size()[1] - self.opened_progress))

    def draw(self):
        super().draw()
        self.draw_tiles()

    def update(self, dt):
        if self.bound_sprite.interacted and not (self.opened or self.opened_progress > 0):
            self.on_open(dt)

        # Update all tiles for animation
        for tile in self.tiles.values():
            tile.update(dt)
