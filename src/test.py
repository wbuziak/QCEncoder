from QuakeParser import QuakeParser
from CirDat import cir
q = ""
with open("GHZ_quake.qke", "r") as f:
    q = f.read()
h = QuakeParser.prep_quake_string(q)
h = QuakeParser.parse_quake_string(h)
print(h)
print()
print(h.get_gates())
print()
h.init_ir()
print(h.get_ir())
print()
h.graphviz_out()


