from CirDat import cir
from PyParser import PyParser
from QuakeParser import QuakeParser
import TargetReps
from pathlib import Path


class Orchestrator:
    @staticmethod
    def parse_all_from_file(filePath: str | Path):
        pyAST = PyParser.load_ast_file(filePath)
        kernels_paths = PyParser.find_kernel_paths(pyAST)
        kernels = PyParser.extract_kernel_code(pyAST, kernels_paths)

        for kernel in kernels:
            #we need to import the kernel and out the quake 
            
            #print(kernel)
            quake_ir = QuakeParser.prep_quake_string(str(kernel))
            parsedCir = QuakeParser.parse_quake_string(quake_ir)
            if parsedCir: #make sure a circuit was returned
                TargetReps.graphviz_will_out(parsedCir)
                TargetReps.tuple_out(parsedCir)


        '''
        Query the user on arguments 
        Done in the QuakeParser (future rework perhaps raise them as exceptions, such that all interaction with user happens on this level)
        '''

        '''
        pass parameters to decide which outputs
        talk with othe
        '''

if __name__ == "__main__": 
    #Orchestrator.parse_all_from_file("../circuits/GHZ.ipynb")
    Orchestrator.parse_all_from_file("../misc_files/GHZ.py")
