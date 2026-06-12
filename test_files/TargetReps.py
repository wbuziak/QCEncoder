import CirDat

def tuple_out(cir):
    with open(cir.name + "_tuple_output.txt", "w+") as f:
        for g in cir.gates:
            f.write(f"({g.name[g.name.index('.')+1:]},[")
            f.write(f"{g.qbits[0]}")
            for q in g.qbits[1:]:
                f.write(f",{q}")
            f.write(f"],{g.time})\n")

def graphviz_will_out(cir):
    edges = set()
    with open(cir.name + "_graphviz_will_output.txt", "w+") as f:
        f.write("digraph G {\n")
        for qubit in range(0, cir.qCount):
            curr = f"q{qubit}_end"
            while curr != None:
                pred = cir.ir[curr]
                if pred == None:
                    break
                if "," in pred:
                    pred = pred.split(",")
                    for p in pred:
                        if "end" in curr:
                            edges.add(f"\t\"{p}\" -> \"End\"\n")
                        elif "start" in p:
                            edges.add(f"\t\"Start\" -> \"{curr}\"\n")
                        else:
                            edges.add(f"\t\"{p}\" -> \"{curr}\"\n")
                    idx1 = pred[0].split("_")[1:-1] if pred[0].count("_") > 1 else [pred[0].split("_")[0][1:]]
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
                if "end" in curr:
                    edges.add(f"\t\"{pred}\" -> \"End\"\n")
                elif "start" in pred:
                    edges.add(f"\t\"Start\" -> \"{curr}\"\n")
                else:
                    edges.add(f"\t\"{pred}\" -> \"{curr}\"\n")
                curr = pred
        measurement = set()
        for k in list(cir.ir):
            if "mz" in k:
                measurement.add(k)
                for i in cir.ir[k].split(","):
                    if "end" in i:
                        edges.add(f"\t\"End\" -> \"{k}\"\n")
                    else:
                        edges.add(f"\t\"{i}\" -> \"{k}\"\n")
        for edge in edges:
            f.write(edge)
        f.write("\n")
        f.write(f"\t\"End\" [style=filled, fillcolor=red]\n")
        f.write(f"\t\"Start\" [style=filled, fillcolor=green]\n")
        for mz in measurement:
            f.write(f"\t\"{mz}\" [style=filled, fillcolor=yellow]\n")
        f.write("}\n")