import cudaq

cudaq.set_target("nvidia", option="mqpu")

def create_GHZ_circuit(qubit_count):
    kernel = cudaq.make_kernel()
    q = kernel.qalloc(qubit_count)

    kernel.h(q[0])

    for i in range(1, qubit_count):
        kernel.cx(q[0], q[i])

    kernel.mz(q)

    print(kernel)
    return kernel

create_GHZ_circuit(3)
