from dataclasses import dataclass
from numpy import inner
import cudaq
import cudaq.mlir.ir as ir
from cudaq.mlir._mlir_libs import _quakeDialects
from CirDat import cir
import io
from typing import ClassVar

DEBUG_INFO = False #if True, this will print out the quake parsing information for every line. 

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
    def parse_quake_string(quake_mlir_code: str) -> cir | None:

        #Please pass the owner of a qubit or cst operand NOT ARG
        def get_loc(opOwner: str) -> str:
            loc: int | str = str(opOwner).split()[0].strip("%")
            return loc


        #retrieve the %CST value or query the user for the value
        ### DO NOT PASS THE OWNER OF A %ARG operand to this function, that passes the whole kernel
        ### We process the operand, not it's owner here
        def handle_angles(pCir: cir, op, main_op) -> float | str:
            value: float | str = ""
            
            if str(op).startswith("Value(%"):
                #get cst value
                value = pCir.get_value(get_loc(op.owner))
                if DEBUG_INFO: print("CST_VAL")

            else:
                #try to reconstruct the arg and collect the value if it exists, if not, query user. 
                reconstructed_name: str = "%arg" + str(op).split(":")[1].strip(" )")
                try:
                    value = pCir.get_value(reconstructed_name)
                    if DEBUG_INFO: print(f"{reconstructed_name} found")
                except KeyError:
                    #query user
                    print(main_op)
                    print("A value passed by argument (to the kernel) has been found. "
                        "Due to how compilation works, the information that would be passed here is not available in quake.")
                    
                    while True:
                        user_input = input(f"Please enter the value of {reconstructed_name} or press enter to continue without values: ").strip()
                        
                        #enter to skip
                        if user_input == "":
                            print("Continuing without value.")
                            value = reconstructed_name
                            if DEBUG_INFO: print(f"no val: {reconstructed_name}, inserting {value}")
                            break
                            
                        #enter float
                        try:
                            value = float(user_input)

                            if DEBUG_INFO:  print(f"new val: {reconstructed_name}, inserting {value}")
                            break
                        except ValueError:
                            print("Invalid input. Please enter a valid decimal number or press Enter to skip.")

                    print("\n")
                    pCir.val_reg[reconstructed_name] = value
                
            return value


        context = ir.Context()
        with context:

            parsedCir: cir = cir()
            context.allow_unregistered_dialects = True

            #print(quake_mlir_code)
            module = ir.Module.parse(quake_mlir_code)


            
            #find the kernel name and save it
            if "cc.python_uniqued" in module.operation.attributes:
                raw_kernel_name = str(module.operation.attributes["cc.python_uniqued"]).strip('"')
                kernel_name = raw_kernel_name.split("..")[0]
            else:
                kernel_name = "unknown_kernel"

            parsedCir.name = kernel_name
            print(f"--- Parsing Quantum Kernel: {parsedCir.name} ---")




            #Walk through quake ast, yay! 
            for op in module.body.operations:
                if op.operation.name == "func.func":
                    for region in op.regions:
                        for block in region.blocks:
                            for inner_op in block.operations:
                                if DEBUG_INFO: 
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

                                op_name: str = str(inner_op.operation.name)
                                qbits = []
 

                                if op_name == "arith.constant":
                                    #find the reg (will be like %cst or %cst_1)
                                    loc = get_loc(inner_op)
                                    value: float = float(str(inner_op.attributes["value"]).split(":")[0].strip())
                                    parsedCir.save_value(get_loc(inner_op), value)
                                    if DEBUG_INFO: print("value stored")

                            
                                # if it is quake.alloca, we need to grab the reg size and record mapping
                                elif op_name == "quake.alloca":

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
                                elif op_name == "quake.extract_ref": 
                                    #get register location 
                                    loc = int(get_loc(inner_op))

                                    #this gets the location of the vector
                                    veq_key = int(get_loc(inner_op.operands[0].owner))

                                    #get raw index (stored in the attr dictionary)
                                    raw_index = int(str(inner_op.attributes["rawIndex"]).split(":")[0].strip())

                                    qvec = parsedCir.qvecs[veq_key]
                                    absolute = qvec.base + raw_index
                                    parsedCir.add_ref(loc, absolute)

                                
                                
                                #basic gates without custom angles
                                elif op_name in QuakeParser.bCtrlGates:

                                    #get qbit list
                                    for orand in list(inner_op.operands):
                                        qbits.append(parsedCir.find_qubit(int(get_loc(orand.owner))))

                                    #check if ctrl; update name in case
                                    if len(inner_op.operands) == 2:
                                        op_name = op_name.replace(".", ".c")

                                    #check if adj; update name in case
                                    elif len(inner_op.operands) == 1:
                                        if "is_adj" in inner_op.attributes:
                                            op_name = op_name + "dg"

                                    else:
                                        print("unrecognized number of operands for bCtrlGate")

                                    #add gate to circuit; possible issue if gate formatting unrecognized
                                    parsedCir.add_gate(op_name, qbits)



                                #Parse gates with a single angle input; handles both ctrl and not 
                                elif op_name in QuakeParser.aCtrlGates:
                                    angles: list[float | str] = []

                                    #get qbit list
                                    for orand in list(inner_op.operands):

                                        try:
                                            qbits.append(parsedCir.find_qubit(int(get_loc(orand.owner))))

                                        except ValueError: #this will trigger if it is a %cst or a %arg0 (AKA an angle)
                                            angles.append(handle_angles(parsedCir, orand, inner_op))
                                        


                                    if len(inner_op.operands) == 3:
                                        op_name = op_name.replace(".", ".c")

                                    elif len(inner_op.operands) != 2:
                                        print("unrecognized number of operands for agate")

                                    parsedCir.add_gate(op_name, qbits, angles)
        


                                #parse measurement gates
                                elif op_name in QuakeParser.mGates:
                                    orand = inner_op.operands[0] #measure only ever has one operand
                                    if str(orand.type) == "!quake.ref":
                                        if DEBUG_INFO: print("single measure")
                                        qbits.append(parsedCir.find_qubit(int(get_loc(orand.owner))))
                                    else:
                                        if DEBUG_INFO: print("qvec measure")
                                        qvec_key = int(get_loc(orand.owner)) #this will lead to the correct qvec
                                        qvec = parsedCir.qvecs[qvec_key]

                                        for i in range(qvec.base, qvec.base + qvec.size): #if it's a qvec, make sure to add the correct qubits to the qbit array
                                            qbits.append(i)

                                    parsedCir.add_gate(op_name, qbits)

    

                                #parse u3 gate
                                elif op_name == "quake.u3":
                                    if DEBUG_INFO: print("u3!")
                                    #3 angles followed by a qubit, I'll just hard code this, lol
                                    angles = []

                                    #handle angles
                                    for i in range(3):
                                        angles.append(handle_angles(parsedCir, inner_op.operands[i], inner_op))

                                    #qubits!

                                    for i in range(3, len(inner_op.operands)):
                                        qbits.append(int(get_loc(inner_op.operands[i].owner)))
                                        if i == 4:
                                            op_name = op_name.replace(".", ".c")
                                    parsedCir.add_gate(op_name, qbits, angles)

                                    

                                #parse exp_pauli gate
                                elif op_name == "quake.exp_pauli":
                                    if DEBUG_INFO: print("exp_pauli!")

                                    params = []

                                    params.append(handle_angles(parsedCir, inner_op.operands[0], inner_op))
                                    
                                    #handle qvec or single qubit
                                    qrand = inner_op.operands[1]
                                    if str(qrand.type) == "!quake.ref":
                                        qbits.append(parsedCir.find_qubit(int(get_loc(qrand.owner))))
                                    else:
                                        qvec_key = int(get_loc(qrand.owner)) #this will lead to the correct qvec
                                        qvec = parsedCir.qvecs[qvec_key]

                                        for i in range(qvec.base, qvec.base + qvec.size): #if it's a qvec, make sure to add the correct qubits to the qbit array
                                            qbits.append(i)


                                    if len(inner_op.operands) == 2: # how it parses if the word it hard coded
                                        params.append(str(inner_op.attributes["pauliLiteral"]).strip("\""))

                                    elif len(inner_op.operands) == 3: #if it's in this format, then the word is passed as an argument, we need to query for it. 

                                        print(inner_op)
                                        print("A pauliword passed by argument (to the kernel) has been found.")
                                        print("Due to how compilation works, the value is not available in quake.")
                                        print(f"Target register size: {len(qbits)} qubit(s).")
                                        
                                        while True: #I didn't want to write the verification below, AI did that. 
                                            user_input = input(f"Please enter the {len(qbits)}-character Pauli word (or Enter to skip): ").strip().upper()
                                            
                                            # Allow skipping
                                            if user_input == "":
                                                print("Continuing without string verification value.")
                                                params.append("UNKNOWN")
                                                break
                                                
                                            # Validate 1: Check length matches target qubit allocations
                                            if len(user_input) != len(qbits):
                                                print(f"Error: Word length ({len(user_input)}) must strictly match targeted qubit count ({len(qbits)}).")
                                                continue
                                                
                                            # Validate 2: Check all characters are strict Pauli primitives
                                            if not all(char in "IXYZ" for char in user_input):
                                                print("Error: Pauli strings must strictly consist of characters: I, X, Y, or Z.")
                                                continue
                                                
                                            # If everything passes, assign it to your parameter track
                                            print(f"Successfully tracked Pauli word parameter: {user_input}")
                                            params.append(user_input)
                                            break

                                    
                                    parsedCir.add_gate(op_name, qbits, params)
                                    

                                else: 
                                    print(f"unidenifiable quake operation {inner_op}. Aborting the parse of this kernel")
                                    return 

                                if DEBUG_INFO: 
                                    if parsedCir.gates:
                                        print("recent gate: ", parsedCir.gates[-1])
                                    print("\n\n\n\n")
                                
            return parsedCir

    @staticmethod
    def parse_quake_file(file_path: str) -> cir | None:
        #load quake files
        with open(file_path, "r") as f:
            quake_mlir_code = f.read()

        return QuakeParser.parse_quake_string(quake_mlir_code)




if __name__ == "__main__":
    h = QuakeParser.parse_quake_file("../test_files/gate_ex.qke")

