# This is an example of my idea for the intermediate represenation of a quantum circuit.
# Note that this is for specifically circuits/QFT.ipynb

# key corresponds to current "node" (i.e. the qubit or gate that can be represented in an identical DAG)
# value corresponds to parent node(s) (i.e. the qubit or gate that is the parent of the key in an identical DAG)
# Our starting qubits' keys have their parents (values) set to None to indicate that they are the initial qubits. Although this is also labeled within the formatting of their keys,
# this is for simplicity of implementation of any further tool that takes this IR and converts it to something else
# gates as keys/values are formatted as follows: gateName_qubitIdx1_qubitIdx2_outputQubitIdx_ithTimeThisGateHasBeenAppliedToTheseQubits
# e.g. x_0_-1_0_0 (Pauli X-gate applied to qubit 0 (x only takes 1 input, so qubitIdx2 is -1) whose output is for qubit 0 and this is the first time the x gate has been applied to this qubit)
# note that a control gate taking/outputting 2 qubits will have 2 distinct comma separated formats for the value, while only having 1 for the key
ir = {"q0_start": None, "q1_start": None, "q2_start": None, "x_0_-1_0_0": "q0_start", "x_2_-1_2_0": "q2_start", "h_0_-1_0_0": "x_0_-1_0_0", "r1(1.571)_0_1_0_0": "h_0_-1_0_0,q1_start", "r1(0.7854)_0_2_0_0": "r1(1.571)_0_1_0_0,x_2_-1_2_0", "h_1_-1_1_0": "q1_start", "r1(1.571)_1_2_1_0": "h_1_-1_1_0,x_2_-1_2_0", "h_2_-1_2_0": "x_2_-1_2_0", "q0_end": "r1(0.7854)_0_2_0_0", "q1_end": "r1(1.571)_1_2_1_0", "q2_end": "h_2_-1_2_0"}
# PLEASE NOTE:
# the formatting of keys/values is meant to be DISTINCT AND EASILY READ BY A COMPUTER PROGRAM NOT TO BE EASILY READ BY A HUMAN
# I plan on having the IR formatted this way for simplicity of DAG construction by a future tool
# it must:
# start on the ending qubits, i.e., q0_end, q1_end, etc.
# recurse back through the dictionary by accessing the value for the given key (if the value is comma separated, 2 recursive calls are made)
# this allows for easy DAG construction given this IR
# I expect that given the output of the QIR parser that Hiram is working on, it shouldn't (hopefully) be too difficult to construct this data structure

# THIS MAY NEED TO BE REVISED GIVEN ANY FUTURE ISSUES WITH THIS REPRESENTATION
