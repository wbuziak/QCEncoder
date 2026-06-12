from dataclasses import dataclass
from numpy import inner
import cudaq
import cudaq.mlir.ir as ir
from cudaq.mlir._mlir_libs import _quakeDialects
from dataclasses import dataclass
from CirDat import cir

@dataclass
class QuakeParser:
    '''
    bgates: list[str] = ["quake.x", "quake.y", "quake.z", "quake.h", "quake.s", "quake.t", "quake.swap"]
    agates: list[str] = ["quake.r1", "quake.rx", "quake.ry", "quake.rz"]
    aagates: list[str] = ["quake.phased_rx", "quake.u2"]
    aaagates: list[str] = ["quake.u3"]
    mgates: list[str] = ["quake.mz", "quake.mx", "quake.my"]
    '''

    ###THIS NOW EXPECTS LOWERED QUAKE MLIR; not normal QUAKE
    @staticmethod 
    def parse_quake_string(quake_mlir_code: str) -> cir:
        context = ir.Context()
        with context:
            parsedCir: cir = cir()
            # register_map and ref_map are stored on parsedCir
            #_quakeDialects.quake.register_dialect(load=True, context=context)
            #_quakeDialects.cc.register_dialect(load=True, context=context)
            #context.load_all_available_dialects()
            context.allow_unregistered_dialects = True

            #print(quake_mlir_code)
            module = ir.Module.parse(quake_mlir_code)

            #Walk through quake ast, yay! 
            for op in module.body.operations:
                if op.operation.name == "func.func":
                    for region in op.regions:
                        for block in region.blocks:
                            for inner_op in block.operations:
                                print("||||", inner_op)
                                '''
                                # if it is quake.alloca, we need to grab the reg size and record mapping
                                if inner_op.operation.name == "quake.alloca":
                                    result_type = inner_op.results[0].type
                                    type_str = str(result_type)

                                    if "<" in type_str and ">" in type_str:
                                        size_digits = type_str.split("<")[1].split(">")[0]
                                        loc = int(str(inner_op.operation).split()[0].strip("%"))

                                        qubit_register_size = int(size_digits)
                                        base_index = parsedCir.qCount
                                        parsedCir.add_qvec(loc, base_index, qubit_register_size)

                                elif inner_op.operation.name == "quake.extract_ref": 
                                    tokens: list[str] = str(inner_op.operation).split()
                                    loc: int = int(tokens[0].strip("%"))
                                    veq_key, raw_index = tokens[3].strip("%]").split("[")
                                    veq_key = int(veq_key)

                                    raw_index = int(raw_index)
                                    qvec = parsedCir.qvecs[veq_key]
                                    absolute = qvec.base + raw_index
                                    parsedCir.add_ref(loc, absolute)

                                elif inner_op.operation.name.startswith("quake.") and inner_op.operation.name != "quake.dealloc":
                                    qbits = []
                                    for orand in list(inner_op.operands):
                                        qbits.append(parsedCir.find_qubit(int(str(orand).split()[0].split("%")[1])))
                                    parsedCir.add_gate(inner_op.operation.name, qbits)
                                    

                                #HANDLE CUSTOM ANGLES////
                                '''
            return parsedCir

    @staticmethod
    def parse_quake_file(file_path: str) -> cir:
        #load quake files
        with open(file_path, "r") as f:
            quake_mlir_code = f.read()

        return QuakeParser.parse_quake_string(quake_mlir_code)




if __name__ == "__main__":
    h = QuakeParser.parse_quake_file("../test_files/gate_ex.qke")

