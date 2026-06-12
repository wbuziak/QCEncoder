from QuakeParser import quakeparser
from CirDat import cir
import TargetReps as t

h = quakeparser.parse_quake_file("GHZ_quake.txt")
h.init_ir()
t.tuple_out(h)
t.graphviz_will_out(h)


