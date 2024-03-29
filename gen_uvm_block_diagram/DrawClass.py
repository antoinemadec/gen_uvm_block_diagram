from PIL import Image, ImageDraw, ImageFont


class DrawClass:
    """Draw block diagram based on a class tree"""

    def __init__(self, class_tree):
        self.w, self.h = 1920, 1080
        self.margin = 10
        self.root_coords = ((0, 0), (self.w-1, self.h-1))
        self.img = Image.new("RGB", (self.w, self.h))
        self.font = ImageFont.truetype("/home/antoine/.fonts/DejaVuSansMono/DejaVu Sans Mono Nerd Font Complete.ttf", 12)
        self.class_tree = class_tree
        self.type_colors = {
            "uvm_test": "#928374",
            "uvm_env": "#80aa9e",
            "uvm_scoreboard": "#e9b143",
            "uvm_agent": "#e2cca9",
            "uvm_sequencer": "#f28534",
            "uvm_monitor": "#b0b846",
            "uvm_driver": "#db4740",
        }
        self.type_position = {
            "uvm_test": "middle",
            "uvm_env": "middle",
            "uvm_scoreboard": "top",
            "uvm_agent": "middle",
            "uvm_sequencer": "top",
            "uvm_monitor": "middle",
            "uvm_driver": "middle",
        }
        self.default_colors = {
            'backgroud': '#928374',
            'text': '#32302f',
            'outline': '#32302f',
        }

    @staticmethod
    def flip_xy_coord(c):
        return ((c[0][1], c[0][0]), (c[1][1], c[1][0]))

    def draw(self, coords, text, color=""):
        c_backgroud = color if color else self.default_colors['backgroud']
        c_outline = self.default_colors['outline']
        c_text = self.default_colors['text']
        img1 = ImageDraw.Draw(self.img)
        img1.rectangle(coords, fill=c_backgroud, outline=c_outline)
        img1.text((coords[0][0]+self.margin/2, coords[0][1]), text, fill=c_text, font=self.font)

    def get_sibling_coords(self, parent_coords, tree, no_margin=False):
        coords = [((0, 0), (0, 0))]*len(tree)
        idx_top = []
        idx_mini = []
        idx_middle = []
        for i,sibling in enumerate(tree):
            type_position = self.type_position.get(sibling['type'], 'mini')
            if type_position == "top":
                idx_top.append(i)
            elif type_position == "mini":
                idx_mini.append(i)
            elif type_position == "middle":
                idx_middle.append(i)
        if idx_top:
            div3_coords = self.divide_rectangle(
                parent_coords, 3, no_margin, y_div=True)
            top_parent_coords = div3_coords[0]
            parent_coords = (div3_coords[1][0], div3_coords[2][1])
            top_coords = self.divide_rectangle(
                top_parent_coords, len(idx_top), no_margin)
            for i in idx_top:
                coords[i] = top_coords.pop(0)
        if idx_mini:
            ((x0, y0), (x1, y1)) = parent_coords
            mini_parent_coords = ((x0, y0+self.margin), (x1, y0+self.margin+30*len(idx_mini)))
            parent_coords = ((x0, y0+30*len(idx_mini)), (x1, y1))
            mini_coords = self.divide_rectangle(
                mini_parent_coords, len(idx_mini), no_margin)
            for i in idx_mini:
                coords[i] = mini_coords.pop(0)
        if idx_middle:
            middle_coords = self.divide_rectangle(
                parent_coords, len(idx_middle), no_margin)
            for i in idx_middle:
                coords[i] = middle_coords.pop(0)
        return coords

    def divide_rectangle(self, coords, nb, no_margin=False, y_div=False):
        if y_div:
            coords = self.flip_xy_coord(coords)
        margin = self.margin if not no_margin else 0
        ((x0, y0), (x1, y1)) = coords
        dx = ((x1-x0-margin) // nb)
        X0 = x0 + margin
        Y0 = y0 + margin
        Y1 = y1 - margin
        new_coords = [((X0+dx*i, Y0), (X0+dx*(i+1)-margin, Y1))
                      for i in range(nb)]
        if y_div:
            new_coords = [self.flip_xy_coord(c) for c in new_coords]
        return new_coords

    def draw_tree(self, tree=[], parent_coords=()):
        is_root = parent_coords == ()
        # root init
        if is_root:
            parent_coords = self.root_coords
            tree = self.class_tree
        # draw recursively
        sibling_coords = self.get_sibling_coords(
            parent_coords, tree, no_margin=is_root)
        for i, sibling in enumerate(tree):
            color = self.type_colors.get(sibling['type'], "")
            self.draw(sibling_coords[i], f"{sibling['name']}", color)
            properties = sibling['properties']
            if len(properties):
                self.draw_tree(properties, sibling_coords[i])
        # show image when recursion is done
        if is_root:
            self.img.show()
