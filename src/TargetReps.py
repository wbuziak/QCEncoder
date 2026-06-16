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
    dag = gv.Digraph(format='svg', name=f'{cir.name}_DAG_Will')
    dag.node('Start', 'Start', style='filled', color='green')
    dag.node('End', 'End', style='filled', color='red')
    for g in cir.gates:
        if "mz" in g.name:
            dag.node(f'{g}', f"{g.name[g.name.index('.')+1:]}", style='filled', color='yellow')
        else:
            dag.node(f'{g}', f"{g.name[g.name.index('.')+1:]}")
    for g in cir.gates:   
        for i in cir.ir[g]:
            if type(i) == str:
                dag.edge('Start', f'{g}')
            else:
                dag.edge(f'{i}', f'{g}')
    for i in cir.ir:
        if type(i) == str:
            if 'end' in i:
                dag.edge(f'{g}', 'End')
    dag.render(directory='../output')
    

def plaintext_out(cir: cir):
    with open("../output/" + cir.name + "_plaintext_output.txt", "w+") as f:
        for g in cir.gates:
            f.write(f"{g}\n")

def graphviz_out(cir: cir):
    dag = gv.Digraph(format='svg', name=f'{cir.name}_DAG')
    for i in cir.ir:
        if type(i) == str:
            if 'end' in i:
                dag.node(f'{i}', f'{i}', style='filled', color = 'red')
            elif 'start' in i:
                dag.node(f'{i}', f'{i}', style='filled', color = 'green')
        else:
            if "mz" in i.name:
                dag.node(f'{i}', f"{i.name[i.name.index('.')+1:]}", style='filled', color='yellow')
            else:
                dag.node(f'{i}', f"{i.name[i.name.index('.')+1:]}")
    for g in cir.gates:   
        for i in cir.ir[g]:
            dag.edge(f'{i}', f'{g}')
    for i in cir.ir:
        if type(i) == str:
            if 'end' in i:
                dag.edge(f'{g}', f'{i}')
    dag.render(directory='../output')
            