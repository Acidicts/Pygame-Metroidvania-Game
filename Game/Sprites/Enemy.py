from Game.Sprites.PhysicsSprite import PhysicsSprite

class Enemy(PhysicsSprite):
    def __init__(self, image, position, game):
        super().__init__(image, position, game)

    def update(self, dt):
        if self.rect.colliderect(self.game.player.rect):
            self.game.player.attributes["health"] -= 1
        super().update(dt)