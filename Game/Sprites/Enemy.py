from Game.Sprites.PhysicsSprite import PhysicsSprite

class Enemy(PhysicsSprite):
    def __init__(self, image, position, game):
        super().__init__(image, position, game)

    def update(self, dt):
        super().update(dt)

    def draw(self, screen, offset):
        super().draw(screen, offset)
