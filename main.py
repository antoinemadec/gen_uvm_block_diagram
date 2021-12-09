#!/usr/bin/env python3

from tree_sitter import Language, Parser
import glob


class SVClass:
    class_dict = {}

    def __init__(self, name, type, properties):
        self.name = name
        self.type = type
        self.properties = properties

    def get_type_without_param(self, type):
        return type.split()[0].split('#')[0]

    def print_tree(self, level=0):
        for p in self.properties:
            type, _ = p
            print(f"{level*'  '} {p}")
            type_without_param = self.get_type_without_param(type)
            if type_without_param in self.class_dict and level < 10:
                self.class_dict[type_without_param].print_tree(level + 1)


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
classes['my_test'].print_tree()
