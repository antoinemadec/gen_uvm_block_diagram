#!/usr/bin/env python3

import anytree

from .verible_verilog_syntax import VeribleVerilogSyntax


class SVFileParser:
    parser = VeribleVerilogSyntax(
        executable="/home/antoine/src/verible-v0.0-1769-g35f00c1f/bin/verible-verilog-syntax")

    def __init__(self, filepath, exclude):
        data = self.parser.parse_files([filepath])
        for file_path, file_data in data.items():
            self.data = file_data
        self.exclude = exclude

    def parse_classes(self):
        if not self.data.tree:
            return
        classes = []
        for cl in self.data.tree.iter_find_all({"tag": "kClassDeclaration"}):
            class_info = {
                "name": "",
                "type": "",
                "properties": [],
            }

            header = cl.find({"tag": "kClassHeader"})
            if not header:
                continue

            # class name
            name = header.find({"tag": ["SymbolIdentifier", "EscapedIdentifier"]},
                               iter_=anytree.PreOrderIter)
            if not name:
                continue
            class_info["name"] = name.text

            # class type
            type = header.find({"tag": "kExtendsList"})
            if type:
                type_id = type.find(
                    {"tag": ["SymbolIdentifier", "EscapedIdentifier"]})
                if type_id:
                    class_info["type"] = type_id.text

            # properties
            items = cl.find({"tag": "kClassItems"})
            if items:
                for data_decl in items.iter_find_all({"tag": ["kDataDeclaration"]}):
                    if not data_decl:
                        continue
                    type = data_decl.find({"tag": "kDataType"})
                    if not type:
                        continue
                    type_name = type.find(
                        {"tag": ["SymbolIdentifier", "EscapedIdentifier"]})
                    if not type_name:
                        continue
                    var_list = data_decl.find(
                        {"tag": "kVariableDeclarationAssignmentList"})
                    if not var_list:
                        continue
                    for var_name in var_list.iter_find_all(
                            {"tag": ["SymbolIdentifier", "EscapedIdentifier"]}):
                        if var_name:
                            class_info['properties'].append(
                                (type_name.text, var_name.text))

            classes.append(class_info)
        return classes
