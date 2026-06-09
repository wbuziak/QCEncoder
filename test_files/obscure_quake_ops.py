"""Explore less-common CUDA-Q / Quake lowering paths.

This keeps the examples in the public Python surface that actually lowers into
Quake ops:
- compute_action
- apply_noise
- qvector windowing via front/back
- exp_pauli
- reset and measurements

The truly low-level cable/state ops from the generated Quake dialect bindings
remain in the compiler's roundtrip tests and are not stable public Python APIs.
"""

from __future__ import annotations

import io

import cudaq
import cudaq.mlir.ir as ir
from cudaq.mlir._mlir_libs import _quakeDialects


@cudaq.kernel
def obscure_quake_sampler(theta: float, phi: float, pauli_coeff: float, word: cudaq.pauli_word):
    """A compact Rosetta-stone kernel for the more unusual Quake lowering paths."""

    q = cudaq.qvector(6)
    exp_q = cudaq.qvector(4)

    # Basic anchors so the output still contains the familiar gates.
    h(q[0])
    x(q[1])
    y(q[2])
    z(q[3])

    # Parameterized gates, including constants that lower to %cst values.
    rx(theta, q[0])
    ry(theta, q[1])
    rz(theta, q[2])
    r1(theta, q[3])
    rz(1.5707963267948966, q[4])
    rz(0.7853981633974483, q[5])

    # Multi-parameter example.
    u3(theta, phi, pauli_coeff, q[1])

    # Explicit control and adjoint-like lowering patterns.
    crx(theta, q[0], q[1])
    cry(theta, q[1], q[2])
    crz(theta, q[2], q[3])
    cr1(theta, q[3], q[4])

    # This is one of the easiest ways to force the compiler to use the
    # qview/ref extraction path rather than only simple qalloc/qextract.
    ctrls = q.front(q.size() - 1)
    last = q.back()

    compute = lambda: (h(ctrls), x(ctrls), rz(phi, last))
    action = lambda: z.ctrl(ctrls, last)
    cudaq.compute_action(compute, action)

    # Noise injection lowers to quake.apply_noise.
    cudaq.apply_noise(cudaq.XError, 0.01, q[0])
    cudaq.apply_noise(cudaq.DepolarizationChannel, 0.02, q[1])
    cudaq.apply_noise(cudaq.Depolarization2, 0.03, q[2], q[3])

    # Special-case higher-level op.
    exp_pauli(pauli_coeff, exp_q, word)

    # Reset plus measurements round out the output.
    reset(q[0])
    mx(q[0])
    my(q[1])
    mz(q[2])
    mz(exp_q)


def render_mlir(kernel, *args):
    kernel(*args)
    quake_mlir = str(kernel)
    print("=== RAW QUAKE MLIR ===")
    print(quake_mlir)

    print("=== REPRINTED MLIR MODULE ===")
    context = ir.Context()
    with context:
        _quakeDialects.quake.register_dialect(load=True, context=context)
        _quakeDialects.cc.register_dialect(load=True, context=context)
        context.load_all_available_dialects()

        module = ir.Module.parse(quake_mlir)
        printer = getattr(getattr(module, "operation", None), "print", None)
        if callable(printer):
            try:
                output_stream = io.StringIO()
                printer(file=output_stream, print_generic_op_form=True)
                print(output_stream.getvalue())
                return
            except TypeError:
                pass

        print(module)


if __name__ == "__main__":
    word = cudaq.pauli_word("XYZI")
    render_mlir(obscure_quake_sampler, 0.125, 0.375, 0.5, word)