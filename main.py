#!/usr/bin/env python3

import glob

from gen_uvm_block_diagram import *


for file in glob.glob('./include/*'):
    SVClass.parse_file(file)
root_class = SVClass.classes['my_test']

# for file in glob.glob('/home/antoine/test/test/dinoplusai/uvm/mxu/classes/*/*.sv'):
#     SVClass.parse_file(file)
# root_class = SVClass.classes['mxu_env']

root_class.print_tree()

dc = DrawClass(root_class.get_tree())
dc.draw_tree()
