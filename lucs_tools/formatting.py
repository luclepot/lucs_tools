import textwrap 
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from operator import truediv, mul

class ascii_canvas(np.ndarray):
    def __new__(
        subtype,
        shape,
        canvas_fill=' ',
        buffer=None,
        offset=0,
        strides=None,
        order=None,
        info=None
    ):  
        obj = super(ascii_canvas, subtype).__new__(
            subtype,
            shape,
            '<U1',
            buffer,
            offset,
            strides,
            order
        )

        if len(canvas_fill) == 0:
            canvas_fill = ' '

        obj.fill(canvas_fill)

        assert(len(shape) == 2)

        obj.width,obj.height = shape

        return obj
    
    def __str__(
        self,
    ):
        s = '-'*(self.width + 4) + '\n'
        for row in self[:].T:
            s += ': {} :\n'.format(''.join(row))
        return s + '-'*(self.width + 4) + '\n'
    
    def raw(
        self,
    ):
        s = ''
        for row in self[:].T:
            s += ''.join(row) + '\n'
        return s

class header:
    styles = ['l', 'c']
    def __init__(self, width, char, colwidth=1):
        self.output = ''
        self.width = width
        self.char = char
        self.colwidth = colwidth
        self.hline()
    
    def __call__(self, s='', side='l'):
        assert(side in self.styles)
        newline = self.char*self.colwidth
        if side is 'l':
            newline += ' '*self.colwidth
        else: 
            newline += int((self.width - 2*self.colwidth - len(s))/2.0)*' '    
        newline += s
        newline += (self.width - len(newline) - 1*self.colwidth)*' '
        newline += self.char*self.colwidth + '\n'
        self.output += newline
    
    def __str__(self):
        return self.output
    
    def hline(self):
        newline = self.char*self.width + '\n'
        self.output += newline

    @staticmethod
    def fmt(s, char='%', colwidth=2, factor=2, side='l'):
        slist = s.split('\n')
        len_max = max(*map(len, slist))
        h = header(len_max + 2*colwidth*factor, char, colwidth)
        h()
        for i,line in enumerate(slist):
            if len(line) == 0:
                h()
                h.hline()
                if i < len(slist) - 1:
                    h()
            else:
                h(line, side='l')

        return str(h)

class pretty_map(dict):
    def __str__(
        self,
    ):
        return map_stringrep(self)

    def __repr__(
        self,
    ):
        return map_stringrep(self)

    def depth(
        self,
    ):
        return map_depth(self)

def map_stringrep(
    d,
    depth=0,
    bullet='-',
):
    indent = '  '*depth + bullet + ' '
    if depth == 0:
        indent = ''
    if isinstance(d, dict):
        return ''.join([indent + (str(key).upper() if depth==0 else str(key)) +  '\n' + map_stringrep(d[key], depth + 1) for key in d])
    if not isinstance(d, str) and hasattr(d, '__iter__'):
        return ''.join([str(map_stringrep(delt, depth)) for delt in d])
    return indent + str(d) + '\n'

def map_depth(
    d
):
    if isinstance(d, dict):
        return 1 + (max(map(map_depth, d.values())) if d else 0)
    return 0
