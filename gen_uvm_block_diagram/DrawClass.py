from PIL import Image, ImageDraw


class DrawClass:
    """Draw block diagram based on a class tree"""

    def __init__(self, class_tree):
        self.w, self.h = 800, 800
        self.margin = 20
        self.root_coords = ((0, 0), (self.w-1, self.h-1))
        self.img = Image.new("RGB", (self.w, self.h))
        self.class_tree = class_tree
        self.type_colors = {
            "uvm_test": "#928374",
            "uvm_env": "#80aa9e",
            "uvm_scoreboard": "#e9b143",
            "uvm_agent": "#e2cca9",
        }
        self.default_colors = {
                'backgroud': '#7c6f64',
                'text': '#32302f',
                'outline': '#32302f',
                }

    def draw(self, coords, text, color=""):
        print(text, coords)
        c_backgroud = color if color else self.default_colors['backgroud']
        c_outline = self.default_colors['outline']
        c_text = self.default_colors['text']
        img1 = ImageDraw.Draw(self.img)
        img1.rectangle(coords, fill=c_backgroud, outline=c_outline)
        img1.text(coords[0], text, fill=c_text)

    def get_coords(self, parent_coords, sibling_nb, no_margin=False):
        margin = self.margin if not no_margin else 0
        ((x0, y0), (x1, y1)) = parent_coords
        dx = ((x1-x0-margin) // sibling_nb)
        X0 = x0 + margin
        Y0 = y0 + margin
        Y1 = y1 - margin
        return [((X0+dx*i, Y0), (X0+dx*(i+1)-margin, Y1)) for i in range(sibling_nb)]

    def draw_tree(self, tree=[], parent_coords=()):
        is_root = parent_coords == ()
        # root init
        if is_root:
            parent_coords = self.root_coords
            tree = self.class_tree
        # draw recursively
        sibling_coords = self.get_coords(parent_coords, len(tree), is_root)
        for i, sibling in enumerate(tree):
            color = self.type_colors.get(sibling['type'], "")
            self.draw(sibling_coords[i], f"{sibling['name']}", color)
            properties = sibling['properties']
            if len(properties):
                self.draw_tree(properties, sibling_coords[i])
        # show image when recursion is done
        if is_root:
            self.img.show()
