import ast

class KerNodeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.__kernels: list[str] = []
    
    def generic_visit(self, node):
        print(type(node))
        ast.NodeVisitor.generic_visit(self, node) #visit children

    #if assigning a variable with make_kernel
    def visit_Assign(self, node):
        print(print(type(node)), node._fields)
        kerName = None
        isKer = False
        for field, value in ast.iter_fields(node):
            if isinstance(value, list) and isinstance(value[0], ast.Name):
                kerName = getattr(value[0], "id")
            if isinstance(value, ast.Call) and getattr(getattr(value, "func"), "attr", None) == 'make_kernel':
                isKer = True
        if isKer: self.__kernels.append(kerName)
        ast.NodeVisitor.generic_visit(self, node)

    def return_kernels(self):
        return self.__kernels