import openfermion
import numpy as np
import cudaq

# Import the classes and functions from your provided script
# (Assuming your script is saved as 'qnp_vqe.py')
from vqe_cudaq_qnp import VQE, get_cudaq_hamiltonian

def main():
    # 1. Define the physical system parameters
    n_qubits = 4
    num_active_electrons = 2
    spin = 0

    # 2. Construct a dummy Hamiltonian
    print("Constructing the Hamiltonian...")
    jw_hamiltonian = (
        openfermion.QubitOperator('Z0', 0.5) +
        openfermion.QubitOperator('Z1', 0.5) +
        openfermion.QubitOperator('X0 X1 Y2 Y3', 0.2) +
        openfermion.QubitOperator('', 0.1)
    )

    # 3. Convert OpenFermion QubitOperator to CUDA-Q SpinOperator
    cudaq_hamiltonian, energy_core = get_cudaq_hamiltonian(jw_hamiltonian)

    # 4. Set VQE configuration options
    options = {
        'n_vqe_layers': 1,
        'maxiter': 50,
        # Set to False to prevent the StateMemoryView compatibility error
        'return_final_state_vec': False,
        'energy_core': energy_core,
        'mpi_support': False
    }

    # 5. Initialize the VQE class
    print("Initializing Quantum-Number-Preserving VQE...")
    vqe_solver = VQE(
        n_qubits=n_qubits,
        num_active_electrons=num_active_electrons,
        spin=spin,
        options=options
    )

    # 6. Execute the optimization
    print("Starting optimization with COBYLA...")
    results = vqe_solver.execute(cudaq_hamiltonian)

    # 7. Output the results
    print("\n--- Final VQE Results ---")
    print(f"Total Optimized Energy : {results['energy_optimized']:.6f}")
    print(f"Best Parameters        : {results['best_parameters']}")

    # 8. Print the Circuit
    print("\n--- Optimized Quantum Circuit ---")
    # Retrieve the kernel structure from your VQE class
    kernel, thetas = vqe_solver.layers()

    # cudaq.draw takes the kernel and then the arguments it expects (the optimal parameters)
    print(cudaq.draw(kernel, results['best_parameters']))

if __name__ == "__main__":
    main()
