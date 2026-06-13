from dataclasses import dataclass, field
from numpy import array, ndarray

@dataclass
class cir:

    @dataclass
    class qvec:
        base: int
        size: int

    @dataclass
    class gate:
        #if is a ctrl gate, it will be reflected in the name quake.cx etc (as in the cudaq)
        #same with the adjoint gates
        name: str
        qbits: list[int]
        time: int
        parameters: list[float | str] | None = None # if not none; has angles
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
    qvecs: dict[int, qvec] = field(default_factory=dict)
    gates: list[gate] = field(default_factory=list)
    ref_reg: dict[int, int] = field(default_factory=dict)
    val_reg: dict[str, float | str] = field(default_factory=dict)
    name: str = "testname"
    ir = {}


    def save_value(self, vRegLbl: str, value: float | int):
        self.val_reg[vRegLbl] = value

    def add_gate(self, name: str, qbits: list[int], params: list[float | str] | None = None, cust_gate: ndarray | None = None):
        self.gates.append(self.gate(name, qbits, self.currTime, parameters=params, custom_gate=cust_gate))
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
            if g.name != "quake.mz": # ignore the measurement: it's not a real gate (at least one we care about putting in the ir/DAG)
                n = []
                n.append(g.name[g.name.index(".")+1:]) # name of the gate

                for i in g.qbits:
                    n.append(str(i)) # add qubit inputs
                if len(g.qbits) == 1:
                    n.append("-1") # if there is only 1 input, the second input is -1
                n.append(str(g.time)) # replaced with timestep (instead of ith time the gate has been applied to the same inputs)
                n = "_".join(n) # format it like the ir should be
                if len(g.qbits) == 1:
                    self.ir[n] = last[g.qbits[0]] # if it is a single-input gate, add directly
                    last[g.qbits[0]] = n
                else:
                    self.ir[n] = f"{last[g.qbits[0]]},{last[g.qbits[1]]}" # otherwise need to add the comma separator to signify 2 inputs
                    last[g.qbits[0]] = n # update "last" list
                    last[g.qbits[1]] = n
            elif self.gates[-1].time == g.time: # if measurement is the last "gate", then its predecessor is all of the end qubits
                end = []
                for i in range(0, self.qCount):
                    self.ir[f"q{i}_end"] = last[i]
                    last[i] = f"q{i}_end"
                    end.append(last[i])
                self.ir[f"mz_{g.time}"] = ",".join(end)
            else: # if the measurement is intermediate
                c = []
                for i in range(0, self.qCount):
                    c.append(last[i])
                self.ir[f"mz_{g.time}"] = ",".join(c)
        if "q0_end" not in self.ir:
            for i in range(0, self.qCount):
                self.ir[f"q{i}_end"] = last[i] # add end qubits

    def get_gates(self):
        return self.gates

    # this method constructs a graphviz output and writes it to the corresponding file.
    # it does this by stepping back starting at the end qubits
    def graphviz_out(self):
        edges = set()
        with open(self.name + "_graphviz_output.txt", "w+") as f:
            f.write("digraph G {\n")
            for qubit in range(0, self.qCount):
                curr = f"q{qubit}_end"
                while curr != None:
                    pred = self.ir[curr]
                    if pred == None:
                        break
                    if "," in pred:
                        pred = pred.split(",")
                        for p in pred:
                            edges.add(f"\t\"{p}\" -> \"{curr}\"\n")
                            #if p.count("_") > 1:
                                #f.write(f" [label={p.split('_')[3]}]\n")
                            #else:
                                #f.write(f" [label={p.split('_')[0][1:]}]\n")
                        idx1 = pred[0].split("_")[1:-1] if pred[0].count("_") > 1 else [pred[0].split("_")[0][1:]]
                        idx2 = pred[1].split("_")[1:-1] if pred[1].count("_") > 1 else [pred[1].split("_")[0][1:]]
                        if "end" in curr:
                            if any([str(qubit) == i for i in idx1]):
                                pred = pred[0]
                            else:
                                pred = pred[1]
                        elif any([i == idx1[0] or i == idx1[-1] for i in curr.split("_")[1:-1]]):
                            pred = pred[0]
                        else:
                            pred = pred[1]
                        curr = pred
                        continue
                    edges.add(f"\t\"{pred}\" -> \"{curr}\"\n")
                    #if pred.count("_") > 1:
                        #f.write(f" [label={pred.split('_')[3]}]\n")
                    #else:
                        #f.write(f" [label={pred.split('_')[0][1:]}]\n")
                    curr = pred
            measurement = set()
            for k in list(self.ir):
                if "mz" in k:
                    measurement.add(k)
                    for i in self.ir[k].split(","):
                        edges.add(f"\t\"{i}\" -> \"{k}\"\n")
            for edge in edges:
                f.write(edge)
            f.write("\n")
            for qubit in range(0, self.qCount):
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
