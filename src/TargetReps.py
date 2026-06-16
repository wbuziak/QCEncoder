import CirDat
import graphviz as gv

def tuple_out(cir):
    with open(cir.name + "_tuple_output.txt", "w+") as f:
        for g in cir.gates:
            f.write(f"({g.name[g.name.index('.')+1:]},[")
            f.write(f"{g.qbits[0]}")
            for q in g.qbits[1:]:
                f.write(f",{q}")
            f.write(f"],{g.time})\n")

def graphviz_will_out(cir):
    dag = gv.Digraph
    dag.node('End', 'End')
    dag.node('Start', 'Start')
    for qubit in range(0, cir.qCount): # go through all the qubits
        curr = f"q{qubit}_end" # our current qubit is the ith qubit
        while curr != None: # loop backwards until None (passing the start qubit)
            pred = cir.ir[curr] # the predecessor to the current qubit
            if pred == None: # break early if the predecessor is None (we have already added the edge from the current gate/qubit to the next gate)
                break
            if "," in pred: # if the gate has multiple inputs
                pred = pred.split(",") # separate the inputs
                for p in pred: # add edges for all pred -> curr pairs
                    if "end" in curr:
                        dag.node(f'{p}', f'{p}')
                        dag.edge(f'{p}', 'End')
                    elif "start" in p:
                        if "mz" in curr:
                            dag.node(f'{curr}', f'{curr}', color='yellow')
                        else:
                            dag.node(f'{curr}', f'{curr}')
                        dag.edge('Start', f'{curr}')
                    else:
                        if "mz" in curr:
                            dag.node(f'{curr}', f'{curr}', color='yellow')
                        else:
                            dag.node(f'{curr}', f'{curr}')
                        dag.edge(f'{p}', f'{curr}')
                if len(pred) > 2: # this is a special case with the measurement as it is tied to all qubits, we just select the one we started on and take that path
                    curr = pred[qubit] 
                else:
                    curr = pred[0] if str(qubit) in pred[0].split("_") else pred[1] # choose the matching predecessor (equivalent qubit)
                continue
            # if it is a single input gate, just add the edge
            if "end" in curr:
                dag.node(f'{pred}', f'{pred}')
                dag.edge(f'{pred}', 'End')
            elif "start" in pred:
                if "mz" in curr:
                    dag.node(f'{curr}', f'{curr}', color='yellow')
                else:
                    dag.node(f'{curr}', f'{curr}')
                dag.edge('Start', f'{curr}')
            else:
                if "mz" in curr:
                    dag.node(f'{curr}', f'{curr}', color='yellow')
                else:
                    dag.node(f'{curr}', f'{curr}')
                dag.edge(f'{pred}', f'{curr}')
            curr = pred # curr becomes pred
    dag.render()

def plaintext_out(cir):
    with open(cir.name + "_plaintext_output.txt", "w+") as f:
        for g in cir.gates:
            f.write(f"{g}\n")

def graphviz_out(cir):
    dag = gv.Digraph
    for qubit in range(0, cir.qCount): # go through all the qubits
        curr = f"q{qubit}_end" # our current qubit is the ith qubit
        while curr != None: # loop backwards until None (passing the start qubit)
            pred = cir.ir[curr] # the predecessor to the current qubit
            if pred == None: # break early if the predecessor is None (we have already added the edge from the current gate/qubit to the next gate)
                break
            if "," in pred: # if the gate has multiple inputs
                pred = pred.split(",") # separate the inputs
                for p in pred: # add edges for all pred -> curr pairs
                    if "end" in curr:
                        dag.node(f'{curr}', f'{curr}', color='red')
                    elif "mz" in curr:
                        dag.node(f'{curr}', f'{curr}', color='yellow')
                    else:
                        dag.node(f'{curr}', f'{curr}')
                    if "start" in p:
                        dag.node(f'{p}', f'{p}', color='green')
                    else:
                        dag.node(f'{p}', f'{p}')
                    dag.edge(f'{p}', f'{curr}')
                if len(pred) > 2: # this is a special case with the measurement as it is tied to all qubits, we just select the one we started on and take that path
                    curr = pred[qubit] 
                else:
                    curr = pred[0] if str(qubit) in pred[0].split("_") else pred[1] # choose the matching predecessor (equivalent qubit)
                continue
            # if it is a single input gate, just add the edge
            if "end" in curr:
                dag.node(f'{curr}', f'{curr}', color='red')
            elif "mz" in curr:
                dag.node(f'{curr}', f'{curr}', color='yellow')
            else:
                dag.node(f'{curr}', f'{curr}')
            if "start" in pred:
                dag.node(f'{pred}', f'{pred}', color='green')
            else:
                dag.node(f'{pred}', f'{pred}')
            dag.edge(f'{pred}', f'{curr}')
            curr = pred # curr becomes pred
    dag.render()
            