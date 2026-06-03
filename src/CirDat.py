from dataclasses import dataclass, field

@dataclass
class cir:

    @dataclass
    class qvec:
        base: int
        size: int

    @dataclass
    class gate:
        name: str
        qbits: list[int]
        time: int

    qCount: int = 0
    currTime: int = 0
    qvecs: dict[int, qvec] = field(default_factory=dict)
    gates: list[gate] = field(default_factory=list)
    ref_reg: dict[int, int] = field(default_factory=dict)
    name: str = "testname"
    ir = {}

    def add_gate(self, name: str, qbits: list[int]):
        self.gates.append(self.gate(name, qbits, self.currTime))
        self.currTime += 1

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
                n.append(g.name.split(".")[-1]) # name of the gate
                for i in g.qbits:
                    n.append(str(i)) # add qubit inputs
                if len(g.qbits) == 1:
                    n.append("-1") # if there is only 1 input, the second input is -1
                n.append(str(g.qbits[0])) # output qubit (should always be the first in the qbits list, need to check with Hiram to make sure this is correct)
                n.append(str(g.time)) # replaced with timestep (instead of ith time the gate has been applied to the same inputs)
                curr_qubit = g.qbits[0] # the qubit the output goes to
                n = "_".join(n) # format it like the ir should be
                if len(g.qbits) == 1:
                    self.ir[n] = last[curr_qubit] # if it is a single-input gate, add directly
                else:
                    self.ir[n] = f"{last[curr_qubit]},{last[g.qbits[1]]}" # otherwise need to add the comma separator to signify 2 inputs
                last[curr_qubit] = n # update "last" list
        for i in range(0, self.qCount):
            self.ir[f"q{i}_end"] = last[i] # add end qubits




    def get_gates(self):
        return self.gates

    # this method constructs a graphviz output and writes it to the corresponding file.
    # it does this by stepping back starting at the end qubits
    def graphviz_out(self):
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
                            f.write(f"\t\"{p}\" -> \"{curr}\"\n")
                        idx1 = pred[0].split("_")[3] if pred[0].count("_") > 1 else str(qubit)
                        idx2 = pred[1].split("_")[3] if pred[1].count("_") > 1 else str(qubit)
                        if "end" in curr:
                            if str(qubit) == idx1:
                                pred = pred[0]
                            else:
                                pred = pred[1]
                        elif curr.split("_")[3] == idx1:
                            pred = pred[0]
                        else:
                            pred = pred[1]
                        curr = pred
                        continue
                    f.write(f"\t\"{pred}\" -> \"{curr}\"\n")
                    curr = pred
            f.write("\n")
            for qubit in range(0, self.qCount):
                f.write(f"\t\"q{qubit}_end\" [style=filled, fillcolor=red]\n")
                f.write(f"\t\"q{qubit}_start\" [style=filled, fillcolor=green]\n")
            f.write("}\n")


    def __str__(self):
        out: str = ""
        print(f"Total qubits: {self.qCount}")
        for qvec in self.qvecs.values():
            out = out + f"Qvec: base={qvec.base}, size={qvec.size}\n"
        for gate in self.gates:
            out = out + f"Gate: name={gate.name}, qbits={gate.qbits}, time={gate.time}\n"
        return out
