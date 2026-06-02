import importlib.util
from importlib.machinery import ModuleSpec
from cudaq.kernel.kernel_builder import PyKernel
from cudaq.kernel.kernel_decorator import PyKernelDecorator
import ast
import inspect

from pathlib import Path
import types
# import cudaq


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
    def find_kernels(pyAST: ast.AST) -> list[PyKernelDecorator | PyKernel]:
        collection: list[PyKernelDecorator | PyKernel] = []


        return collection


    @staticmethod
    def parse_from_file():
        print("hello")


print(pyAST := PyParser.load_ast_file("./_test_mod_for_parse.py"))
PyParser.find_kernels(pyAST)
