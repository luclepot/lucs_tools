class Header:
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
        h = Header(len_max + 2*colwidth*factor, char, colwidth)
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
