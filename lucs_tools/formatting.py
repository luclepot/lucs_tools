import numpy as np
import textwrap 
import numpy as np
import textwrap
import matplotlib.pyplot as plt

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

class joyful:

    @staticmethod
    def _rand(
        min,
        max
    ):
        return np.random.random()*(max - min) + min

    @staticmethod
    def _rand_int(
        min,
        max
    ):
        return int(np.floor(np.random.random()*(max - min + 1)) + min)
    
    @staticmethod
    def _rand_normal(
        mu,
        sigma,
        n=6
    ):
        sum = 0
        for i in range(n):
            sum += joyful._rand(-1., 1.)
        return mu + sigma*sum / n

    @staticmethod
    def _normal_pdf(
        x,
        mu,
        sigma
    ):
        num = np.e**(-((x-mu)**2.)/(2.*(sigma**2.)))
        denom = np.sqrt(2.*np.pi*(sigma**2.))
        return num/denom

    @staticmethod
    def _textwrap_converge(
        text_str,
        n_lines
    ):
        text_lines = len(text_str)
        while len(textwrap.wrap(text_str, text_lines)) < n_lines:
            text_lines -= 1
        return textwrap.wrap(text_str, text_lines)

    @staticmethod    
    def joy_points(
        lines=60,
        points=80,
        size=(625, 593)
    ):
        width = size[0]
        height = size[1]
        xmin = 140
        xmax = width - xmin
        ymin = 100
        ymax = height - ymin
        mx = 0.5*(xmin + xmax)
        dx = (xmax - xmin) / points
        dy = (ymax - ymin) / lines
        x = xmin
        y = ymin
        xplt = np.empty(points)
        yplt = np.empty((lines, points))
        for i in range(lines):
            nmodes = joyful._rand_int(1, 4)
            mus = np.empty(nmodes)
            sigmas = np.empty(nmodes)
            for j in range(nmodes):
                mus[j] = joyful._rand(mx - 50., mx + 50.)
                sigmas[j] = joyful._rand_normal(24, 30)
            w = y
            for k in range(points):
                x = x + dx
                noise = 0
                for l in range(nmodes):
                    noise += joyful._normal_pdf(x, mus[l], sigmas[l])
                yy = 0.3*w + 0.7*(y - 600 * noise + noise * np.random.random() * 200 + np.random.random())
                yplt[i,k] = yy
                xplt[k] = x
                w = yy
            x = xmin
            y = y + dy
        return xplt, ymax - yplt

    @staticmethod
    def joy_plot(
        lines,
        points=60,
        linewidth=1.,
        size=(625, 593)
    ):
        x, ys = joyful.joy_points(lines, points, size)
        for y in ys:
            plt.plot(x,y, c='white', linewidth=linewidth)
        ax = plt.gca()
        ax.set_aspect(float(size[0])/float(size[1]))
        ax.set_facecolor('black')
        ax.axes.get_xaxis().set_ticks([])
        ax.axes.get_yaxis().set_ticks([])
        plt.show()

    @staticmethod
    def letter_plot(
        text,
        points,
        fontsize=6,
        weight='light',
        size=(625, 593),
        subaspect=1.4
    ):
        # formatted = _textwrap_converge(data, lines)
        formatted = textwrap.wrap(text.replace(' ', ''), points)
        lines = len(formatted)
        points = max(map(len, formatted))
        x, ys = joyful.joy_points(lines, points, size)
        for i in range(lines):
            for j in range(len(formatted[i])):
                plt.text(x[j], ys[i,j], formatted[i][j], fontsize=fontsize, weight=weight, color='white', verticalalignment='top', horizontalalignment='left')
        plt.plot(x, np.min(ys, axis=0), 'black')
        #plt.plot(x[0], ys[0,-1])
        plt.plot(x, np.max(ys, axis=0), 'black')
        ax = plt.gca()
        ax.set_aspect(subaspect*float(lines)/float(points))
        ax.set_facecolor('black')
        ax.axes.get_xaxis().set_ticks([])
        ax.axes.get_yaxis().set_ticks([])
        plt.show()
