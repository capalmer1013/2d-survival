import pyxel


class UI:
    def __init__(self, relx, rely, parent, app):
        self.relx, self.rely = relx, rely
        self.parent = parent
        self.app = app
        self.h = 16
        self.w = 128

    def update(self):
        pass

    def draw(self):
        pyxel.rect(
            self.app.model.player.x + self.relx,
            self.app.model.player.y + self.rely,
            self.w,
            self.h,
            13,
        )
        # pyxel.blt(self.relx, self.rely, 0, self.U, self.V, self.w, self.h, 14)


class InventoryUI(UI):
    def __init__(self, relx, rely, parent, app):
        super().__init__(relx, rely, parent, app)

    def draw(self):
        if self.parent.placed:
            # draw inventory, repative to parent
            inv_dict = self.parent.inventory.dict()
            count = 1
            y = 0
            for each in inv_dict:
                pyxel.text(
                    self.relx + 39,
                    self.rely + y,
                    f"[{count}] {each.__name__}(s): {inv_dict[each]}",
                    7,
                )
                y += 8
                count += 1
            pass
