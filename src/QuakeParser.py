from dataclasses import dataclass
from numpy import inner
import cudaq
import cudaq.mlir.ir as ir
from cudaq.mlir._mlir_libs import _quakeDialects
from CirDat import cir
import io
from typing import ClassVar

@dataclass
class QuakeParser:
    bCtrlGates: ClassVar[list[str]] = ["quake.x", "quake.y", "quake.z","quake.h", "quake.s", "quake.t"]
    aCtrlGates: tuple[str, ...] = ("quake.r1", "quake.rx", "quake.ry", "quake.rz")
    #aagates: tuple[str, ...] = ("quake.phased_rx", "quake.u2") #These exist in the quake ops def. file, but I cannot figure out how to get them to generate from python cudaq. 
    mGates: tuple[str, ...] = ("quake.mz", "quake.mx", "quake.my")

    #Other gates parsed:
        #U3 gate
        #Exp_pauli gate 


    '''
    This method takes in the quake dialect in the form outputted by the str() method of the kernel class in cudaq
        It then outputs a version of quake that more closesly resembles basic MLIR, which is easier to parse. 
        If you are interested in the differences, take a peek at the gate_ex.py file in the test_files section 
    '''
    @staticmethod 
    def prep_quake_string(quake_mlir: str) -> str:
        context = ir.Context()
        with context:
            _quakeDialects.quake.register_dialect(load=True, context=context)
            _quakeDialects.cc.register_dialect(load=True, context=context)
            context.load_all_available_dialects()

            module = ir.Module.parse(quake_mlir)
            output_stream = io.StringIO()
            module.operation.print(file=output_stream, print_generic_op_form=True)
            return output_stream.getvalue()


    '''
    This takes in quake in mlir gen grammar and parses it creating the Cir Object. 
    
    '''
    ###THIS NOW EXPECTS LOWERED QUAKE MLIR; not normal QUAKE
    @staticmethod 
    def parse_quake_string(quake_mlir_code: str) -> cir:

        def get_loc(op: str) -> str:
            loc: int | str = str(op).split()[0].strip("%")
            return loc

        context = ir.Context()
        with context:

            parsedCir: cir = cir()
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
                                print("_______________")
                                for attr in inner_op.attributes:
                                    print(attr.name, attr.attr)
                                #result_type = inner_op.results[0].type
                                #type_str = str(result_type)
                                #print("TYPE STR", type_str)
                                for item in inner_op.operands:
                                    print(item)
                                    #print(dir(item))

                                

                                if inner_op.operation.name == "arith.constant":
                                    #find the reg (will be like %cst or %cst_1)
                                    loc = get_loc(inner_op)
                                    value: float = float(str(inner_op.attributes["value"]).split(":")[0])
                                    parsedCir.save_value(inner_op, value)
                                    print("value stored")

                            
                                # if it is quake.alloca, we need to grab the reg size and record mapping
                                elif inner_op.operation.name == "quake.alloca":

                                    #search throught the result type to find the allocation size
                                    result_type = inner_op.results[0].type
                                    type_str = str(result_type)
                                    size_digits = type_str.split("<")[1].split(">")[0]

                                    qubit_register_size = int(size_digits)
                                    base_index = parsedCir.qCount

                                    #grab the register location
                                    loc = int(get_loc(inner_op))
                                    parsedCir.add_qvec(loc, base_index, qubit_register_size)

                                    
                                #assigns specific qubit values to registers via extraction of references
                                elif inner_op.operation.name == "quake.extract_ref": 
                                    #get register location 
                                    loc = int(get_loc(inner_op))

                                    #this gets the location of the vector
                                    veq_key = int(get_loc(inner_op.operands[0].owner))

                                    #get raw index (stored in the attr dictionary)
                                    raw_index = int(str(inner_op.attributes["rawIndex"]).split(":")[0].strip())

                                    qvec = parsedCir.qvecs[veq_key]
                                    absolute = qvec.base + raw_index
                                    parsedCir.add_ref(loc, absolute)

                                
                                elif inner_op.operation.name in QuakeParser.bCtrlGates:
                                    print(inner_op.operation.name)
                                    if len(inner_op.operands) == 2:
                                        print("ctrl")

                                    elif len(inner_op.operands) == 1:
                                        if "is_adj" in inner_op.attributes:
                                            print("adjoint")
                                        else:
                                            print("unctrl")

                                    else:
                                        print("unrecognized number of operands for bCtrlGate")

                                elif inner_op.operation.name in QuakeParser.aCtrlGates:
                                    if len(inner_op.operands) == 3:
                                        print("ctrl")
                                    elif len(inner_op.operands) == 2:
                                        print("unctrl")
                                    else:
                                        print("unrecognized number of operands for agate")



                                elif inner_op.operation.name in QuakeParser.mGates:
                                    if str(inner_op.operands[0].type) == "!quake.ref":
                                        print("single measure")
                                    else:
                                        print("qvec measure")




                                elif inner_op.operation.name == "quake.u3":
                                    print("u3!")




                                elif inner_op.operation.name == "quake.exp_pauli":
                                    print("exp_pauli!")



                                '''
                                elif inner_op.operation.name.startswith("quake.") and inner_op.operation.name != "quake.dealloc":
                                    qbits = []
                                    for orand in list(inner_op.operands):
                                        qbits.append(parsedCir.find_qubit(int(str(orand).split()[0].split("%")[1])))
                                    parsedCir.add_gate(inner_op.operation.name, qbits)
                                '''

                                #HANDLE CUSTOM ANGLES////


                                print("\n\n\n\n")
                                
            return parsedCir

    @staticmethod
    def parse_quake_file(file_path: str) -> cir:
        #load quake files
        with open(file_path, "r") as f:
            quake_mlir_code = f.read()

        return QuakeParser.parse_quake_string(quake_mlir_code)




if __name__ == "__main__":
    h = QuakeParser.parse_quake_file("../test_files/gate_ex.qke")

