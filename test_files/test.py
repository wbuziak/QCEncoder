from ..src.QuakeParser import quakeparser
from ..src.CirDat import cir

h = quakeparser.parse_quake_file("GHZ_quake.txt")
print(h)
print()
print(h.get_gates())
print()
h.init_ir()
print(h.get_ir())
print()
h.graphviz_out()


