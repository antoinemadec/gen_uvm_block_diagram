from tree_sitter import Language, Parser


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

    def __init__(self, filepath, exclude):
        self.src_code = bytes(open(filepath, 'r').read(), "utf8")
        self.root_node = self.PARSER.parse(self.src_code).root_node
        self.exclude = exclude

    def node_str(self, node):
        return self.src_code[node.start_byte:node.end_byte].decode("utf8") if node else ""

    def parse_classes(self):
        classes = []
        for node_class, _ in self.query["class"].captures(self.root_node):
            class_info = {
                    "name": "",
                    "type": "",
                    "properties": [],
                    }
            # class.name
            c = self.query["class.name"].captures(node_class)
            assert len(c) == 1
            node_class_name, _ = c[0]
            class_info['name'] = self.node_str(node_class_name)

            # class.type
            c = self.query["class.type"].captures(node_class)
            node_class_type = None
            if c:
                assert len(c) == 1
                node_class_type, _ = c[0]
            class_info['type'] = self.node_str(node_class_type)

            # class.property
            c = self.query["class.property"].captures(node_class)
            type = None
            for node, capture_name in c:
                if capture_name == "class.property.type":
                    type = self.node_str(node)
                else:
                    var = self.node_str(node)
                    class_info['properties'].append([type, var])
            classes.append(class_info)
        return classes
