import cudaq

# A 4-bit random number generator using cuda-q kernel builder

# Initialize the kernel builder
kernel = cudaq.make_kernel()

qubits = kernel.qalloc(4)

# Apply an H gate to the second qubit (q1)
kernel.h(qubits)

# kernel.mz() automatically maps the measurements to a classical register
kernel.mz(qubits)

print(cudaq.draw(kernel))

# Execute the circuit on the simulator with 100 shots
result = cudaq.sample(kernel, shots_count=100)

# Output the results
print("--- Measurement Counts ---")
result.dump() 

# Highest probable result
most_probable_bitstring = max(result.items(), key=lambda item: item[1])

print("--- Highest Probability Result ---")
print(f"Value: {most_probable_bitstring[0]}")
print(f"Count: {most_probable_bitstring[1]} out of 100 shots")
