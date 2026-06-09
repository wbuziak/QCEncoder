import cudaq
import random

# The Deutsch-Jozsa algorithm with only a balanced oracle

# Kind of defeats the purpose of the algorithm, but 
# we are currently only interested in our ability to parse
# and recreate the algorithm, and we want to avoid classical
# control flow

def create_dj_kernel(n: int):
    kernel = cudaq.make_kernel()
    
    # Allocate n data qubits + 1 target qubit
    qubits = kernel.qalloc(n + 1)
    
    # Avoid the QuakeValue slice error
    data_qubits = [qubits[i] for i in range(n)]
    target_qubit = qubits[n]

    # The target qubit must be initialized to the |-> state.
    kernel.x(target_qubit)

    # Apply H gate to ALL qubits (data + target)
    kernel.h(qubits)

    # --- A Balanced Oracle ---
    kernel.cx(control=data_qubits[0], target=target_qubit)

    # Apply H gate to ONLY the data qubits
    for q in data_qubits:
        kernel.h(q)

    # kernel.mz() cannot accept a Python list, so we measure them in a loop.
    for q in data_qubits:
        kernel.mz(q)

    return kernel

def main():
    n = 3 
    
    # Build the kernel
    dj_kernel = create_dj_kernel(n)
    
    # Execute the circuit. 
    shots = 1000
    result = cudaq.sample(dj_kernel, shots_count=shots)
    
    print("\nMeasurement Counts:")
    result.dump()

    print("\nCircuit Diagram:")
    print(cudaq.draw(dj_kernel))

if __name__ == "__main__":
    main()
