import cudaq
from cudaq import kernel as kn
import cudaq as cq

cudaq.set_target("nvidia", option="mqpu")

def create_GHZ_circuit(qubit_count: int):
    kernel = cudaq.make_kernel()
    q = kernel.qalloc(qubit_count)

    kernel.h(q[0])
    print("hi")

    a = 5

    for i in range(1, qubit_count):
        kernel.cx(q[0], q[i])

    kernel.mz(q)

    return kernel

qubit_count = 10
kernel = cudaq.make_kernel()
q = kernel.qalloc(qubit_count)

kernel.h(q[0])
print("hi")

a = 5

for i in range(1, qubit_count):
    kernel.cx(q[0], q[i])

kernel.mz(q)

class kernelMaker:
    @staticmethod
    @cq.kernel
    def hello():
        q = cudaq.qvector(10)
        h(q[0])
        
        for i in range(1, 10):
            cx(q[0], q[i])

        mz(q)

    class insider:
        def __init__(self, qubit_count: int):
            kernel = cudaq.make_kernel()
            q = kernel.qalloc(qubit_count)

            kernel.h(q[0])

            for i in range(1, qubit_count):
                kernel.cx(q[0], q[i])

            kernel.mz(q)

            return kernel

@cudaq.kernel
def other_GHZ_circuit():
    q = cudaq.qvector(10)
    h(q[0])
    
    for i in range(1, 10):
        cx(q[0], q[i])

    mz(q)

@cq.kernel
def extra_GHZ_circuit(qubit_count: int): 
    q = cudaq.qvector(qubit_count)
    h(q[0])
    
    for i in range(1, qubit_count):
        cx(q[0], q[i])

    mz(q)



k = create_GHZ_circuit(10)
print(other_GHZ_circuit)
print(k)
