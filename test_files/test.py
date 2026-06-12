from QuakeParser import quakeparser
from CirDat import cir
import TargetReps as t

h = quakeparser.parse_quake_file("GHZ_quake.txt")
print(h)
print()
print(h.get_gates())
print()
h.init_ir()
print(h.get_ir())
print()
t.tuple_out(h)


