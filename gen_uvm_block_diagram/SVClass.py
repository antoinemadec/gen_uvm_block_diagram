from .parsers.verible import SVFileParser


class SVClass:
    """Represents systemverilog classes, the way to relate to each other"""

    classes = {}
    exclude = ["uvm_sequence", "uvm_sequence_item"]

    def __init__(self, name, type, properties):
        self.name = self.remove_param_from_string(name)
        self.type = self.remove_param_from_string(type)
        self.full_name = name
        self.full_type = type
        self.properties = properties

    @staticmethod
    def remove_param_from_string(s):
        return s.split()[0].split('#')[0] if s else ''

    def get_tree(self, level=0):
        prop_trees = []
        if self.name in self.exclude or self.type in self.exclude:
            return []
        for p in self.properties:
            class_name = p[0]
            if class_name in self.classes and level < 10:
                prop_trees += self.classes[class_name].get_tree(
                    level + 1)
            else:
                prop_trees += [{'name': class_name, 'type': class_name, 'properties': []}]
        return [{'name': self.name, 'type': self.type, 'properties': prop_trees}]

    def print_tree(self, tree=[], level=0):
        if level == 0:
            tree = self.get_tree()
        for sibling in tree:
            print(f"{level*'  '}{sibling['type']} {sibling['name']}")
            self.print_tree(sibling['properties'], level+1)

    @classmethod
    def parse_file(cls, file):
        p = SVFileParser(file, cls.exclude)
        for cl in p.parse_classes():
            cls.classes[cl['name']] = SVClass(
                cl['name'], cl['type'], cl['properties'])
