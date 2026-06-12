import CirDat

def tuple_out(cir):
        with open(cir.name + "_tuple_output.txt", "w+") as f:
            for g in cir.gates:
                f.write(f"({g.name[g.name.index('.')+1:]},[")
                f.write(f"{g.qbits[0]}")
                for q in g.qbits[1:]:
                    f.write(f",{q}")
                f.write(f"],{g.time})\n")

