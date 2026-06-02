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

    def __str__(self):
        out: str = ""
        print(f"Total qubits: {self.qCount}")
        for qvec in self.qvecs.values():
            out = out + f"Qvec: base={qvec.base}, size={qvec.size}\n"
        for gate in self.gates:
            out = out + f"Gate: name={gate.name}, qbits={gate.qbits}, time={gate.time}\n"
        return out
