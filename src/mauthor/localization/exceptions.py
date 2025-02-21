
class ContentException(Exception):

    def __init__(self, value):
        self.parameter = value
    
    def __str__(self):
        return repr(self.parameter)
    
class NoModulesFoundException(Exception):
    
    def __init__(self):
        self.parameter = "No modules found."
        
    def __str__(self):
        return repr(self.parameter)
    
class NodeNotFoundException(Exception):
    
    def __init__(self, node_name):
        self.parameter = node_name  + " node has not been found in your XLIFF document."
        
    def __str__(self):
        return repr(self.parameter)

class ContentTooBigException(Exception):

    def __init__(self, value):
        self.parameter = value
    
    def __str__(self):
        return repr(self.parameter)