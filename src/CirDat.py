from dataclasses import dataclass, field
from numpy import array, ndarray

@dataclass
class cir:

    @dataclass
    class qvec:
        base: int
        size: int

    @dataclass(frozen=True)
    class gate:
        #if is a ctrl gate, it will be reflected in the name quake.cx etc (as in the cudaq)
        #same with the adjoint gates
        name: str
        qbits: tuple[int]
        time: int
        parameters: tuple[float | str] | None = None #if not none; has angles and the pauli word! Pauli word will be last; 
                                                    #be prepped to output that if the gate is pauli
        custom_gate: ndarray | None = None # if not none; custom_gate


        def __str__(self) -> str:
            """Concise human-readable representation."""
            params = ""
            if self.parameters:
                params = f" params={self.parameters}"
            cg = " custom_gate" if self.custom_gate is not None else ""
            qb_str = ",".join(str(q) for q in self.qbits)
            return f"{self.name}({qb_str})@t{self.time}{params}{cg}"


    qCount: int = 0
    currTime: int = 0
    qvecs: dict[int, qvec] = field(default_factory=dict) #The key is the reg they are introduced to
    gates: list[gate] = field(default_factory=list)
    ref_reg: dict[int, int] = field(default_factory=dict) #the key is the reg the reference is placed into 
    val_reg: dict[str, float | str] = field(default_factory=dict) # the ksy is %cst or %arg
    name: str = "testname"
    ir = {}

    def save_value(self, vRegLbl: str, value: float | int):
        self.val_reg[vRegLbl] = value

    def add_gate(self, name: str, qbits: list[int], params: list[float | str] | None = None, cust_gate: ndarray | None = None):
        fixedParams = params
        if params != None:
            fixedParams = tuple(params)
        self.gates.append(self.gate(name, tuple(qbits), self.currTime, parameters=fixedParams, custom_gate=cust_gate))
        if self.gates[-1].custom_gate != None:
            self.gates[-1].custom_gate.flags.writeable = False
        self.currTime += 1

    def get_value(self, vRegLbl) -> float | str:
        return self.val_reg[vRegLbl]

    def add_qvec(self, loc: int, base: int, size: int):
        self.qvecs[loc] = self.qvec(base, size)
        self.qCount += size
        return self.qvecs[loc]
    
    def find_qubit(self, regNum: int) -> int | None:
        return self.ref_reg.get(regNum)

    def add_ref(self, regNum: int, absolute_idx: int):
        self.ref_reg[regNum] = absolute_idx
    
    def get_ir(self):
        return self.ir 

    def init_ir(self):
        last = [] # indexes correspond to qubit, the last thing to happen for each qubit, initialized to be q0_start, etc.
        for i in range(0, self.qCount):
            self.ir[f"q{i}_start"] = None # initialize qubits in both the ir dict and "last" list
            last.append(f"q{i}_start")
        for g in self.gates:
            value = []
            for q in g.qbits:
                value.append(last[q])
                last[q] = g
            self.ir[g] = value
        for i in range(0, self.qCount):
            self.ir[f"q{i}_end"] = last[i] # add end qubits

    def get_gates(self):
        return self.gates

    # this method constructs a graphviz output and writes it to the corresponding file.
    # it does this by stepping back starting at the end qubits
    def graphviz_out(self):
        edges = set() # we only want one of each edge
        measurement = set()
        with open(self.name + "_graphviz_output.txt", "w+") as f: # the output file
            f.write("digraph G {\n") # necessary header for graphviz
            for qubit in range(0, self.qCount): # go through all the qubits
                curr = f"q{qubit}_end" # our current qubit is the ith qubit
                while curr != None: # loop backwards until None (passing the start qubit)
                    if "mz" in curr: # add measurements as they appear
                        measurement.add(curr) 
                    pred = self.ir[curr] # the predecessor to the current qubit
                    if pred == None: # break early if the predecessor is None (we have already added the edge from the current gate/qubit to the next gate)
                        break
                    if "," in pred: # if the gate has multiple inputs
                        pred = pred.split(",") # separate the inputs
                        for p in pred: # add edges for all pred -> curr pairs
                            edges.add(f"\t\"{p}\" -> \"{curr}\"\n")
                        if len(pred) > 2: # this is a special case with the measurement as it is tied to all qubits, we just select the one we started on and take that path
                            curr = pred[qubit] 
                        else:
                            curr = pred[0] if str(qubit) in pred[0].split("_") else pred[1] # choose the matching predecessor (equivalent qubit)
                        continue
                    edges.add(f"\t\"{pred}\" -> \"{curr}\"\n") # if it is a single input gate, just add the edge
                    curr = pred # pred becomes curr
            for edge in edges: # write the edges to the output file
                f.write(edge)
            f.write("\n")
            for qubit in range(0, self.qCount): # write the coloring of qubits and measurements
                f.write(f"\t\"q{qubit}_end\" [style=filled, fillcolor=red]\n")
                f.write(f"\t\"q{qubit}_start\" [style=filled, fillcolor=green]\n")
            for mz in measurement:
                f.write(f"\t\"{mz}\" [style=filled, fillcolor=yellow]\n")
            f.write("}\n")


    def __str__(self):
        out: str = ""
        print(f"Total qubits: {self.qCount}")
        for qvec in self.qvecs.values():
            out = out + f"Qvec: base={qvec.base}, size={qvec.size}\n"
        for gate in self.gates:
            out = out + f"Gate: name={gate.name}, qbits={gate.qbits}, time={gate.time}\n"
        return out
