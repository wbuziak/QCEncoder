import ast
import os
import contextlib
from pprint import pprint
from nbconvert import PythonExporter
from pathlib import Path
import linecache
from cudaq.kernel.kernel_builder import PyKernel
from cudaq.kernel.kernel_decorator import PyKernelDecorator
import KerNodeVisitor


class PyParser:
    #TODO: make something to auto identify the file type (py or jupyter)
    '''
    This method was made with AI, I didn't know nbconvert had a python package, I just thought is was a cli tool 
    '''
    @staticmethod 
    def load_ast_from_notebook(notebook_path) -> ast.AST:
             
        #use nbconvert to into python
        exporter = PythonExporter()
        source_code, _ = exporter.from_filename(notebook_path)
        
        #Now do it with python
        pyAST = ast.parse(source_code)
        annotator = ParentAnnotator()
        annotator.visit(pyAST)
        return pyAST


    @staticmethod
    def load_ast_file(filePath: str | Path) -> ast.AST:
        if isinstance(filePath, str):
            filePath = Path(filePath)
 
        if not isinstance(filePath, Path):
            raise TypeError("filePath must be a pathlib.Path or str")

        if not filePath.exists():
            raise FileNotFoundError(f"file not at {filePath}")

        #Read the source code directly and parse it
        source_code = filePath.read_text(encoding="utf-8")
        pyAST = ast.parse(source_code)
        #Add in parent nodes
        annotator = ParentAnnotator()
        annotator.visit(pyAST)

        return pyAST
    

    @staticmethod
    def find_kernels(pyAST: ast.AST): #the quake strings
        kerVis = KerNodeVisitor.KerNodeVisitor()
        kerVis.visit(pyAST)

        return kerVis.return_kernels()


    @staticmethod 
    def extract_kernel_code(pyAST: ast.AST, kernelList) -> dict[str, str]:
        collection: dict[str, str] = {}
        #print(ast.dump(pyAST, indent=4))
        hardKernels = []
        easyKernels = []
        
        #separate the kernels into the two types, there are some that are very hard to parse
        for kernel in kernelList:
            hard: bool = False
            path = kernel["location"]
            for layer in path:
                if layer[1] == "FunctionDef":
                    hard = True
            if hard:
                hardKernels.append(kernel)
            else:
                easyKernels.append(kernel)
        #print("HARD KERNELS:")
        #pprint(hardKernels)
        #print("EASY KERNELS:")
        #pprint(easyKernels)

        #start getting the quake of the easy kernel
        source_code = ast.unparse(pyAST) #get the source back so we can execute it 

        #print(source_code)

        #These next couple of lines were made with the help of AI
        spoofed_file = f"<faked_kernel_file>"
        lines = [line + "\n" for line in source_code.splitlines()]
        linecache.cache[spoofed_file] = (len(source_code), None, lines, spoofed_file)

        compiled_fake_file = compile(source_code, spoofed_file, 'exec') #compile the code so that the line numbers are correct for error messages
        isolated_globals = {"cudaq": __import__("cudaq"), "__name__": "sandbox"}
        with open(os.devnull, 'w') as devnull:
            with contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull): 
                exec(compiled_fake_file, isolated_globals)

        #pprint(isolated_globals)
        #pprint(dir(isolated_globals['k']))
        
        for kernel in easyKernels:
            if kernel["location"]:
                parentObj = isolated_globals[kernel["location"].pop(0)[0]]
                while kernel["location"]:
                    parentObj = getattr(parentObj, kernel["location"].pop(0)[0])
                collection[kernel['name']] = str(getattr(parentObj, kernel["name"]))
            else: 
                collection[kernel['name']] = str(isolated_globals[kernel["name"]])


        #sometimes kernel objects are created by calling a function that returns a kernel, so we need to find those as well, this is the easiest way to extend coverage
        for id, obj in isolated_globals.items():
            if isinstance(obj, PyKernel): # the objects we look for cannot be PyKernelDecoratores
                if id not in collection.keys():
                    collection[id] = str(obj)




        return collection



    @staticmethod
    def find_kernel_paths(pyAST: ast.AST):
        kernelFinder = KernelFinder()
        kernelFinder.visit(pyAST)
        return kernelFinder.results


class ParentAnnotator(ast.NodeVisitor):
    def generic_visit(self, node):
        for child in ast.iter_child_nodes(node):
            child.parent = node
            self.visit(child)


class KernelFinder(ast.NodeVisitor):

    def __init__(self):
        self.results = [] 
        self.possible_kernels = []
        self.possible_kernel_makers = []
        self.kernel_imported: list[str] = ["kernel"]
        self.cudaq_asname: list[str] = ["cudaq"]


    def get_location(self, node) -> list[tuple[str, str]]:
        runningLoc: list[tuple[str, str]] = []
        currNode = node.parent
        currNode = getattr(node, 'parent', None)
        
        while currNode is not None and not isinstance(currNode, ast.Module):
            if isinstance(currNode, ast.ClassDef):
                runningLoc.append((currNode.name, "ClassDef"))

            elif isinstance(currNode, ast.FunctionDef):
                runningLoc.append((currNode.name, "FunctionDef"))
                
            #move up tree, give none if at the top
            currNode = getattr(currNode, 'parent', None)
        return runningLoc[::-1] #reverse to get order from outermost to innermost


    def visit_Import(self, node):
        for alias in node.names:
            if alias.name == 'cudaq' and alias.asname is not None:
                self.cudaq_asname.append(alias.asname)


    def visit_ImportFrom(self, node):
        if node.module == 'cudaq':
            for alias in node.names:
                if alias.name == 'kernel':
                    if alias.asname is not None:
                        self.kernel_imported.append(alias.asname)

    #TODO: add support for finding when cudaq or cudaq kernel or make_kernel is aliased within the code (involves visit_Assign)
    #TODO: scan for functions that return a kernel, add those to the assign visit list!! (fixes some of not being able to see inside functions)
   

    def visit_FunctionDef(self, node):
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Attribute):
                if getattr(decorator.value, "id", None) in self.cudaq_asname and decorator.attr == "kernel":
                    self.results.append({
                        "name": node.name,
                        "type": "cudaq.PyKernelDecorator",
                        "line": node.lineno,
                        "location": self.get_location(node)
                    })
                elif self.kernel_imported != ["kernel"] and node.name in self.kernel_imported:
                    self.results.append({
                        "name": node.name,
                        "type": "cudaq.PyKernelDecorator",
                        "line": node.lineno,
                        "location": self.get_location(node)
                    })
        self.generic_visit(node)


    def visit_Assign(self, node):
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute):
            func = node.value.func
            if getattr(func.value, 'id', None) in self.cudaq_asname and func.attr == 'make_kernel':
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.results.append({
                            "name": target.id, 
                            "type": "cudaq.PyKernel",
                            "line": node.lineno,
                            "location": self.get_location(node)
                        })
        self.generic_visit(node)



if __name__ == "__main__":
    pyAST = PyParser.load_ast_file("../misc_files/GHZ.py")
    kernel_locations = PyParser.find_kernel_path(pyAST)
    pprint(kernel_locations)
    PyParser.extract_kernel_code(pyAST, kernel_locations)





        


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
