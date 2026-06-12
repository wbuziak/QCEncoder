# this is very much ai generated 
# I just need a rosetta stone of sorts
# see how everything shows up in quake 
#
#
import io

import cudaq
import cudaq.mlir.ir as ir
from cudaq.mlir._mlir_libs import _quakeDialects

@cudaq.kernel
def ultimate_quake_inspector(
    r_angle: float,        # 1-operand agates (rx, ry, rz, r1)
    u3_a1: float,         # 3-operand aaagates (u3)
    u3_a2: float,
    u3_a3: float,
    pauli_coeff: float,   # For quake.exp_pauli
    word: cudaq.pauli_word
):
    # Allocate a vector of qubits to track SSA wire variables
    q = cudaq.qvector(5)
    exp_q = cudaq.qvector(4)
 
    # -------------------------------------------------------------
    # 1. bgates (basic gates: 0 parameters)
    # -------------------------------------------------------------
    x(q[0])
    y(q[1])
    z(q[2])
    h(q[3])
    s(q[0])
    t(q[1])
     
    # Common multi-qubit bgates
    cx(q[0], q[1])
    cy(q[1], q[2])
    cz(q[2], q[3])
    ch(q[0], q[2])
    swap(q[2], q[3])

    # Controlled single-qubit gate examples that lower to quake.c* ops.
    cs(q[0], q[3])
    ct(q[1], q[4])

    # -------------------------------------------------------------
    # 2. agates (1 dynamic parameter operand)
    # -------------------------------------------------------------
    rx(r_angle, q[0])
    ry(r_angle, q[1])
    rz(r_angle, q[2])
    r1(r_angle, q[3])  # Standard phase-shift gate

    # Literal constants show up in the MLIR as %cst values.
    rz(1.5707963267948966, q[4])
    rz(0.7853981633974483, q[0])

    # Controlled dynamic rotations
    crx(r_angle, q[0], q[1])
    cry(r_angle, q[1], q[2])
    crz(r_angle, q[2], q[3])
    cr1(r_angle, q[3], q[4])

    # Adjoint examples without any classical control flow.
    sdg(q[0])
    tdg(q[1])

    # -------------------------------------------------------------
    # 3. aaagates (3 dynamic parameter operands)
    # -------------------------------------------------------------
    u3(u3_a1, u3_a2, u3_a3, q[1])

    # -------------------------------------------------------------
    # 4. Special Case: quake.exp_pauli
    # -------------------------------------------------------------
    exp_pauli(pauli_coeff, exp_q, word)

    # -------------------------------------------------------------
    # 5. mgates (Measurement Gates)
    # -------------------------------------------------------------
    mx(q[0])
    my(q[1])
    mz(q[2])
    mx(exp_q)

if __name__ == "__main__":
    #print("=== RAW QUAKE MLIR OUTPUT ===")

    # 1. Define your Pauli word configuration outside the AST bridge
    my_word = cudaq.pauli_word("XYZI")
    
    # 2. Invoke the kernel with your dummy inputs to trigger JIT compilation.
    # This populates the internal MLIR Module inside the kernel object.
    ultimate_quake_inspector(0.1, 0.2, 0.3, 0.4, 0.5, my_word)
    
    # 3. Cast the compiled kernel directly to a string to print the raw MLIR text
    quake_mlir = str(ultimate_quake_inspector)
    #print(quake_mlir)

    #print("=== REPRINTED MLIR MODULE ===")
    context = ir.Context()
    with context:
        _quakeDialects.quake.register_dialect(load=True, context=context)
        _quakeDialects.cc.register_dialect(load=True, context=context)
        context.load_all_available_dialects()

        module = ir.Module.parse(quake_mlir)
        output_stream = io.StringIO()
        try:
            module.operation.print(file=output_stream, print_generic_op_form=True)
            print(output_stream.getvalue())
        except (AttributeError, TypeError):
            print(module)
