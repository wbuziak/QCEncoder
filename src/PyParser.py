import importlib.util
from importlib.machinery import ModuleSpec
from cudaq.kernel.kernel_builder import PyKernel
from cudaq.kernel.kernel_decorator import PyKernelDecorator
import ast
import inspect  

from pathlib import Path
import types
# import cudaq

import KerNodeVisitor


class PyParser:
    @staticmethod
    def load_ast_file(filePath: str | Path) -> ast.AST:
        if isinstance(filePath, str):
            filePath = Path(filePath)

        if not isinstance(filePath, Path):
            raise TypeError("filePath must be a pathlib.Path or str")

        if not filePath.exists():
            raise FileNotFoundError(f"file not at {filePath}")

        # Read the source code directly and parse it
        source_code = filePath.read_text(encoding="utf-8")
        return ast.parse(source_code)  
    
    @staticmethod
    def find_kernels(pyAST: ast.AST) -> list[str]: #the quake strings
        collection: list[str] = []

        kerVis = KerNodeVisitor.KerNodeVisitor()
        kerVis.visit(pyAST)

        return kerVis.return_kernels()




        


# print(pyAST := PyParser.load_ast_file("./_test_mod_for_parse.py"))
# PyParser.find_kernels(pyAST)

#code for testing:
# if(1):
#     t = PyParser.load_ast_file('./GHZ.py')
# else:
#     t = ast.parse('kernel = cudaq.make_kernel()')
# x = KerNodeVisitor.KerNodeVisitor()
# print(ast.dump(t, indent=2))
# print()
# x.visit(t)
# print()
# print(x.return_kernels())
