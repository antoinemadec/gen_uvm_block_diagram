#!/usr/bin/env python3

from tree_sitter import Language, Parser
import glob
from PIL import Image, ImageDraw


class DrawClass(object):
    """DrawClass print block diagram based on a class tree"""

    def __init__(self, class_tree):
        self.w, self.h = 800, 800
        self.margin = 20
        self.root_coords = ((0, 0), (self.w-1, self.h-1))
        self.img = Image.new("RGB", (self.w, self.h))
        self.class_tree = class_tree

    def show(self):
        self.img.show()

    def draw(self, coords, text, color="#ffff99"):
        print(f"{coords} {text}")
        img1 = ImageDraw.Draw(self.img)
        img1.rectangle(coords, fill=color, outline="red")
        img1.text(coords[0], text, fill="black")

    def get_coords(self, parent_coords, sibling_nb):
        if parent_coords == self.root_coords and sibling_nb == 1:
            margin = 0
        else:
            margin = self.margin
        ((x0, y0), (x1, y1)) = parent_coords
        dx = ((x1-x0-margin) // sibling_nb)
        X0 = x0 + margin
        Y0 = y0 + margin
        Y1 = y1 - margin
        return [((X0+dx*i, Y0), (X0+dx*(i+1)-margin, Y1)) for i in range(sibling_nb)]

    def print_tree(self, tree=[], parent_coords=()):
        if parent_coords == ():
            parent_coords = self.root_coords
            tree = self.class_tree
        sibling_coords = self.get_coords(parent_coords, len(tree))
        for i, sibling in enumerate(tree):
            self.draw(sibling_coords[i], f"{sibling['name']}")
            properties = sibling['properties']
            if len(properties):
                self.print_tree(properties, sibling_coords[i])


class SVClass:
    class_dict = {}

    def __init__(self, name, type, properties):
        self.name = name
        self.type = type
        self.properties = properties

    def get_type_without_param(self, type):
        return type.split()[0].split('#')[0]

    def get_tree(self, level=0):
        prop_trees = []
        for p in self.properties:
            type, _ = p
            type_without_param = self.get_type_without_param(type)
            if type_without_param in self.class_dict and level < 10:
                prop_trees += self.class_dict[type_without_param].get_tree(
                    level + 1)
        return [{'type': self.type, 'name': self.name, 'properties': prop_trees}]

    def print_tree(self, tree=[], level=0):
        if level == 0:
            tree = self.get_tree()
        for sibling in tree:
            print(f"{level*'  '}{sibling['type']} {sibling['name']}")
            self.print_tree(sibling['properties'], level+1)


class SVFileParser:
    """Parse systemverilog file with treesitter"""

    SV_LIB = "/home/antoine/.local/share/nvim/site/pack/packer/start/nvim-treesitter/parser/verilog.so"
    SV_LANG = Language(SV_LIB, 'verilog')
    PARSER = Parser()
    PARSER.set_language(SV_LANG)

    query = {}
    query["class"] = SV_LANG.query("(class_declaration) @class")
    query["class.name"] = SV_LANG.query("""
            (class_declaration
                (class_identifier
                    (simple_identifier) @class.name
                )
            )""")
    query["class.type"] = SV_LANG.query("""
            (class_declaration
                (class_type
                    (class_identifier
                        (simple_identifier) @class.type
                    )
                )
            )""")
    query["class.property"] = SV_LANG.query("""
            (class_item
              (class_property
                (data_declaration
                  (data_type_or_implicit1) @class.property.type
                  (list_of_variable_decl_assignments) @class.property.variable
                )
              )
            )""")
    query["simple_identifier"] = SV_LANG.query(
        """(simple_identifier) @simple_identifier""")

    def __init__(self, filepath):
        self.src_code = bytes(open(filepath, 'r').read(), "utf8")
        self.tree = self.PARSER.parse(self.src_code)
        self.root_node = self.tree.root_node

    def node_str(self, node):
        return self.src_code[node.start_byte:node.end_byte].decode("utf8") if node else ""

    def parse_classes(self):
        classes = []
        for node_class, _ in self.query["class"].captures(self.root_node):
            # class.name
            c = self.query["class.name"].captures(node_class)
            assert len(c) == 1
            node_class_name, _ = c[0]

            # class.type
            c = self.query["class.type"].captures(node_class)
            node_class_type = None
            if c:
                assert len(c) == 1
                node_class_type, _ = c[0]

            # class.property
            c = self.query["class.property"].captures(node_class)
            properties = []
            type = None
            for node, capture_name in c:
                if capture_name == "class.property.type":
                    type = self.node_str(node)
                else:
                    var = self.node_str(node)
                    properties.append([type, var])
            sv_class = SVClass(
                self.node_str(node_class_name),
                self.node_str(node_class_type),
                properties,
            )
            classes.append(sv_class)
        return classes


classes = {}
for file in glob.glob('./include/*'):
    p = SVFileParser(file)
    for cl in p.parse_classes():
        classes[cl.name] = cl

SVClass.class_dict = classes
root_class = classes['my_test']
tree = root_class.get_tree()
print(tree)
root_class.print_tree()

dc = DrawClass(tree)
dc.print_tree()
dc.show()
