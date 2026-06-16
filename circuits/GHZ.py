# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: hydrogen
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: cudaq-env
#     language: python
#     name: python3
# ---

# %% [markdown]
# # GHZ Circuit

# %%
import cudaq

# Set up the CUDA-Q target for multiple QPUs if available
cudaq.set_target("nvidia", option="mqpu")


# %%
def create_GHZ_circuit(qubit_count):
    kernel = cudaq.make_kernel()
    q = kernel.qalloc(qubit_count)

    kernel.h(q[0])

    for i in range(1, qubit_count):
        kernel.cx(q[0], q[i])

    kernel.mz(q)

    print("GHZ Circuit:")
    print(cudaq.draw(kernel))
    print("================")
    print()
    return kernel

