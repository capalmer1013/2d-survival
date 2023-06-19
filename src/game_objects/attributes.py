import random


class Inventory:
    def __init__(self, l=None):
        self.items = {}
        if l:
            for each in l:
                self.append(each)

    def getItem(self, index):
        item = self.items[list(self.items.keys())[index]]
        if item.amount > 0:
            item.amount -= 1
            if item.amount <= 0:
                self.items.pop(list(self.items.keys())[index], None)
            return item.__class__
        return None

    def append(self, item):
        if type(item) in self.items:
            self.items[type(item)].amount += item.amount
        else:
            self.items[type(item)] = item
        # if hte list is full just drop it
        pass

    def dict(self):
        return {x: self.items[x].amount for x in self.items}

    def get_all(self):
        return list(self.items.keys())


class HasInventoryMixin:
    def scatterInventory(self):
        for each in self.inventory.get_all():
            randx, randy = random.randint(-8, 8), random.randint(-8, 8)
            self.app.model.gameObjects.append(
                each(self.x + randx, self.y + randy, self, self.app)
            )

    def takeDamage(self, amount):
        self.health -= amount
        if self.health <= 0:  # todo: move this into die function
            self.is_alive = False
            self.scatterInventory()
