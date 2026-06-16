import cudaq
import torch
import numpy as np
import os
import re

def GHZ(qubit_count: int):
    kernel = cudaq.make_kernel()
    q = kernel.qalloc(qubit_count)

    kernel.h(q[0])
    for i in range(1, qubit_count):
        kernel.cx(q[0], q[i])
    kernel.mz(q)

    print(cudaq.draw(kernel))

    return kernel

def parse_cudaq_kernel(kernel):
    """
    Parses Quake IR into a 4-element format:
    [timestep, control_qubit_index, target_qubit_index, gate_id]
    """
    quake_str = str(kernel)
    triples = []
    timestep = 0

    # Dictionary to map SSA registers to actual qubit indices
    ssa_to_qubit = {}

    for line in quake_str.splitlines():
        line = line.strip()
        if not line:
            continue

        # 1. Track qubit reference extractions
        if "quake.extract_ref" in line or "quake.qextract" in line:
            match = re.search(r"%(\d+)\s*=\s*quake\.(?:extract_ref|qextract)\s*%(\d+)\[(\d+)\]", line)
            if match:
                dest_register = match.group(1)
                qubit_index = int(match.group(3))
                ssa_to_qubit[dest_register] = qubit_index
            continue

        # 2. Parse actual gate operations
        if "quake." in line and "quake.alloca" not in line:
            if ":" in line:
                op_part, _ = line.split(":", 1)
            else:
                op_part = line

            gate_match = re.search(r"quake\.(\w+)", op_part)
            if not gate_match:
                continue
            gate_name = gate_match.group(1)

            # Find all SSA registers in the operation
            ssa_regs = re.findall(r"%(\d+)", op_part)

            # Ignore the output register if it's a measurement assignment
            if op_part.startswith("%") and len(ssa_regs) > 0:
                ssa_regs = ssa_regs[1:]

            if not ssa_regs:
                continue

            # Convert SSA registers back to true qubit indices
            qubit_indices = []
            for reg in ssa_regs:
                if reg in ssa_to_qubit:
                    qubit_indices.append(ssa_to_qubit[reg])
                else:
                    # Fallback for whole-vector operations like global mz
                    qubit_indices.append(f"all_qvec_%{reg}")

            # Determine control vs target based on the number of qubits involved
            if len(qubit_indices) == 1:
                # Single qubit gate
                triples.append([timestep, qubit_indices[0], "single_qubit", gate_name])
            elif len(qubit_indices) == 2:
                # Multi-qubit gate (Control, Target)
                triples.append([timestep, qubit_indices[0], qubit_indices[1], gate_name])
            else:
                # Fallback for handling multi-controlled gates if added later
                triples.append([timestep, qubit_indices[:-1], qubit_indices[-1], gate_name])

            timestep += 1

    return triples

if __name__ == "__main__":
    qubit_count = 4
    kernel = GHZ(qubit_count)

    triples = parse_cudaq_kernel(kernel)

    print("\n[timestep, control_qubit_index, target_qubit_index, gate_id]:")
    for row in triples:
        print(row)
