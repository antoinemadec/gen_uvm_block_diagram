#!/usr/bin/env python3

import glob

from gen_uvm_block_diagram import *


for file in glob.glob('./include/*'):
    SVClass.parse_file(file)

root_class = SVClass.classes['my_test']
root_class.print_tree()

dc = DrawClass(root_class.get_tree())
dc.draw_tree()
