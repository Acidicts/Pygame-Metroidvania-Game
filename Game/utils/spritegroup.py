class SpriteGroup:
    def __init__(self):
        self.sprite_dict = {}

    def add(self, *sprites):
        for sprite in sprites:
            if hasattr(sprite, 'id'):
                self.sprite_dict[sprite.id] = sprite

    def sprites(self):
        return list(self.sprite_dict.values())

    def append(self, sprite):
        if hasattr(sprite, 'id'):
            self.sprite_dict[sprite.id] = sprite
        else:
            self.sprite_dict[len(self.sprite_dict)] = sprite


    def remove(self, *sprites):
        for sprite in sprites:
            if hasattr(sprite, 'id') and sprite.id in self.sprite_dict:
                del self.sprite_dict[sprite.id]
            else:
                # Remove by value if ID is not present or not found by ID
                keys_to_remove = [k for k, v in self.sprite_dict.items() if v == sprite]
                for k in keys_to_remove:
                    del self.sprite_dict[k]

    def get_by_id(self, sprite_id):
        return self.sprite_dict.get(sprite_id)

    def empty(self):
        self.sprite_dict.clear()

    def draw(self, surface, offset):
        for sprite in self.sprite_dict.values():
            sprite.draw(surface, offset)

    def set_sprite_group(self):
        for sprite in self.sprite_dict.values():
            if sprite.sprite_group == None:
                sprite.sprite_group = self

    def update(self, dt):
        self.set_sprite_group()
        for sprite in list(self.sprite_dict.values()):
            sprite.update(dt)