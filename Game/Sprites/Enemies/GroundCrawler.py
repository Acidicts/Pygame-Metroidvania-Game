from Game.Sprites.Enemy import Enemy
from Game.utils.helpers import px_to_grid


class GroundCrawler(Enemy):
    def __init__(self, img, position, game, tilemap):
        super().__init__(image=img, position=position, game=game)
        self.direction = 1
        self.tilemap = tilemap

    def update(self, dt):
        self.velocity.x = 50 * self.direction
        enemy_pos = px_to_grid(self.game.player.position)
        if self.tilemap.get_tile(enemy_pos[0] + self.direction, enemy_pos[1] + 1) is None:
            self.direction *= -1
        super().update(dt)
