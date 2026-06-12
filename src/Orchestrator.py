from CirDatcir import cir
from PyParser import PyParser
from QuakeParser import QuakeParser
from Pathlib import Path


class Orchestrator:
    @staticmethod
    def parse_all_from_file(filePath: str | Path, outFile: str | Path):
        pyAST = PyParser.load_ast_file(filePath)
        kernels:  = PyParser.find_kernels(pyAST)

        for kernel in kernels:
            print(kernel)
            quake_ir = kernel.get_quake_ir()
            print(quake_ir)
            cir_dat = QuakeParser.parse_quake_string(quake_ir)
            print(cir_dat)
