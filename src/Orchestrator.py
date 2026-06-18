from CirDat import cir
from PyParser import PyParser
from QuakeParser import QuakeParser
import TargetReps
from pathlib import Path

class Orchestrator:
    @staticmethod
    def parse_all_from_file(filePath: str | Path):

        print(f"Grabbing AST from: {filePath}\n")
        pyAST = PyParser.load_ast_file(filePath)

        print("Finding kernels in AST...\n")
        kernels_paths = PyParser.find_kernel_paths(pyAST)

        print(f"Found {len(kernels_paths)} in the AST; Attempting to extracte kernel code from AST...\n")
        kernels = PyParser.extract_kernel_code(pyAST, kernels_paths)

        print(f"Retrieved {len(kernels)} kernels in file: {filePath}\n")
        print("Note: some kernels may not be retrievable")
        
        parsed = 0
        for name, kernel in kernels.items():
            #we need to import the kernel and out the quake 
            
            print(f"\n--- Parsing Quantum Kernel: {name} ---")

            #print(kernel)
            print("\tPrepping Quake string")
            quake_ir = QuakeParser.prep_quake_string(str(kernel))

            print("\tParsing Quake string")
            parsedCir = QuakeParser.parse_quake_string(quake_ir)

            if parsedCir: #make sure a circuit was returned

                print("\tOutputting representations")
                if not parsedCir.name:
                    parsedCir.name = name
                parsedCir.init_ir()
                try:
                    TargetReps.graphviz_will_out(parsedCir)
                except Exception as e:
                    print(f"Error outputting graphviz for kernel: {e}")
                try:
                    TargetReps.tuple_out(parsedCir)
                except Exception as e:
                    print(f"Error outputting tuple for kernel: {e}")
                try:
                    TargetReps.graphviz_out(parsedCir)
                except Exception as e:
                    print(f"Error outputting graphviz for kernel: {e}")
                try:
                    TargetReps.plaintext_out(parsedCir)
                except Exception as e:
                    print(f"Error outputting plaintext for kernel: {e}")
                parsed += 1
            else:
                print(f"Error parsing kernel: {name}, skipping outputting representations")
            
        print(f"\nSuccessfully parsed {parsed}/{len(kernels)} kernels retrieved from file: {filePath}\n\n\n")


        '''
        Query the user on arguments 
        Done in the QuakeParser (future rework perhaps raise them as exceptions, such that all interaction with user happens on this level)
        '''

        '''
        pass parameters to decide which outputs
        talk with othe
        '''

if __name__ == "__main__": 
    Orchestrator.parse_all_from_file("../misc_files/gate_ex.py")
    Orchestrator.parse_all_from_file("../circuits/QFT.ipynb")
    Orchestrator.parse_all_from_file("../misc_files/GHZ.py")

