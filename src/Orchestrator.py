from CirDat import cir
from PyParser import PyParser
from QuakeParser import QuakeParser
import TargetReps
from pathlib import Path


class Orchestrator:
    @staticmethod
    def parse_all_from_file(filePath: str | Path):
        pyAST = PyParser.load_ast_file(filePath)
        kernels  = PyParser.find_kernels(pyAST)



        for kernel in kernels:
            print(kernel)
            quake_ir = QuakeParser.prep_quake_string(str(kernel))
            parsedCir = QuakeParser.parse_quake_string(quake_ir)
            TargetReps.graphviz_will_out(parsedCir)
            TargetReps.tuple_out(parsedCir)


        '''
        Query the user on arguments 
        '''

        '''
        pass parameters to decide which outputs
        '''

        '''
        skip storing
        '''

if __name__ == "__main__":
    Orchestrator.parse_all_from_file("GHZ.py")
