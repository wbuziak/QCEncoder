from CirDat import cir
import graphviz as gv

def tuple_out(cir: cir):
    with open("../output/" + cir.name + "_tuple_output.txt", "w+") as f:
        for g in cir.gates:
            f.write(f"({g.name[g.name.index('.')+1:]},[")
            f.write(f"{g.qbits[0]}")
            for q in g.qbits[1:]:
                f.write(f",{q}")
            f.write(f"],{g.time})\n")

def graphviz_will_out(cir: cir):
    dag = gv.Digraph(format='svg', name=f'{cir.name}_DAG_Will') # creates digraph object
    dag.node('Start', 'Start', style='filled', color='green') # creates start node and makes it green
    dag.node('End', 'End', style='filled', color='red') # creates end node and makes it red
    for g in cir.ir: # creates all gate nodes including measurements
        if type(g) != str:
            if g.name in ["quake.mz", "quake.mx", "quake.my"]:
                dag.node(f'{g}', f"{g.name[g.name.index('.')+1:]}", style='filled', color='yellow') # makes measurement nodes and makes them yellow
            else:
                dag.node(f'{g}', f"{g.name[g.name.index('.')+1:]}") # makes non measurement gate nodes
    for i in cir.ir: # makes all edges
        if len(cir.ir[i]) > 0:
            for j in cir.ir[i]:
                if type(i) == str:
                    if type(j) != str:
                        dag.edge(f'{j}', 'End') # connects end node to ending gates
                    else:
                        dag.edge('Start', 'End') # for edge case of start node connecting directly to end node
                else:
                    if type(j) != str:
                        dag.edge(f'{j}', f'{i}') # connects internal nodes
                    else:
                        dag.edge('Start', f'{i}') # connects start nodes to starting gates
    dag.render(directory='../output') # outputs into file

def graphviz_out(cir: cir):
    dag = gv.Digraph(format='svg', name=f'{cir.name}_DAG') # creates digraph object
    for i in cir.ir: # creates all gate nodes including measurements and all start and end qubit nodes
        if type(i) == str:
            if 'end' in i:
                dag.node(f'{i}', f'{i}', style='filled', color = 'red') # makes start qubit nodes and makes them green
            elif 'start' in i:
                dag.node(f'{i}', f'{i}', style='filled', color = 'green') # makes end qubit nodes and makes them red
        else:
            if "mz" in i.name or "mx" in i.name or "my" in i.name:
                dag.node(f'{i}', f"{i.name[i.name.index('.')+1:]}", style='filled', color='yellow') # makes measurement nodes and makes them yellow
            else:
                dag.node(f'{i}', f"{i.name[i.name.index('.')+1:]}") # makes non measurement gate nodes
    for i in cir.ir: # makes all edges
        if len(cir.ir[i]) > 0:
            for j in cir.ir[i]:
                dag.edge(f'{j}', f'{i}')
    dag.render(directory='../output') # outputs into file
    
def plaintext_out(cir: cir):
    with open("../output/" + cir.name + "_plaintext_output.txt", "w+") as f:
        for g in cir.gates:
            f.write(f"{g}\n")
            
