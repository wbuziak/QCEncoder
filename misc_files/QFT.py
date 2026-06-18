import cudaq
import numpy as np

cudaq.set_target("nvidia", option="mqpu")

def build_qft_kernel(qubit_count: int, initial_state: list[int]):
    kernel = cudaq.make_kernel()
    qubits = kernel.qalloc(qubit_count)
    for i in range(qubit_count):
        if initial_state[i] == 1:
            kernel.x(qubits[i])

    for i in range(qubit_count):
        kernel.h(qubits[i])
        for j in range(i+1, qubit_count):
            angle = (2.0 * np.pi) / (2**(j - i + 1))
            kernel.cr1(angle, qubits[j], qubits[i])

    return kernel

num_qubits = 3
state_to_prepare = [1, 0, 1]

kernel = build_qft_kernel(num_qubits, state_to_prepare)

print(cudaq.draw(kernel))
