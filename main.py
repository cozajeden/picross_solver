from numpy import *
from tkinter import *
from tkinter import messagebox
from threading import Thread
from time import sleep
from itertools import permutations, combinations_with_replacement

class VarLabel(Label):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        text = ''
        if 'text' in kwargs:
            text = kwargs['text']
        if 'textvariable' in kwargs:
            self.tVar = kwargs['textvariable']
        else:
            self.tVar = StringVar(self, text)
            self.configure(textvariable=self.tVar)
        self.set = self.tVar.set
        self.get = self.tVar.get
        self.full = lambda: self.config(bg='black')
        self.empty = lambda: self.config(bg='white')

    def error(self):
        self.config(fg='red', font='Times 12 bold')
        if self.get() == '':
            self.set('▒')

class Window(Tk):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # Create Frames
        self.frame = Frame(self)
        self.hf = Frame(self.frame)
        self.vf = Frame(self.frame)
        self.tf = Frame(self.frame)
        self.phf = Frame(self.frame)
        self.pvf = Frame(self.frame)
        self.frame.pack(fill=BOTH, expand=1,side=TOP)
        self.hf.grid(row=0, column=1, sticky=NSEW)
        self.vf.grid(row=1, column=0, sticky=NSEW)
        self.tf.grid(row=1, column=1, sticky=NSEW)
        self.phf.grid(row=2, column=1, sticky=NSEW)
        self.pvf.grid(row=1, column=2, sticky=NSEW)

        # Create thread
        self.thread = Thread(None, target=self.loop, daemon=True)

    def init(self, h, v):
        if sum([sum(x) for x in h]) != sum([sum(x) for x in v]):
            messagebox.showerror('ValueError', 'Sum in rows have to be equal with sum in cols')
            raise ValueError('Sum in rows have to be equal with sum in cols')

        self.h = h
        self.v = v
        
        x = len(h)
        y = len(v)

        # Create row/col labels with lengths and amounts of possibilities
        [Label(self.hf, text=''.join([str(x) for x in i]), wraplength=1).pack(side=LEFT, fill=BOTH, expand =1) for i in h]
        [Label(self.vf, text=', '.join([str(x) for x in i])).pack(side=TOP, fill=BOTH, expand =1) for i in v]
        self.hplab = [VarLabel(self.phf, text='0', wraplength=1) for i in h]
        self.vplab = [VarLabel(self.pvf, text='0') for i in v]
        [i.pack(side=LEFT, fill=BOTH, expand =1) for i in self.hplab]
        [i.pack(side=TOP, fill=BOTH, expand =1) for i in self.vplab]

        # Create results table
        self.table = empty((x,y), object) # Wiev table
        self.values = empty((x,y), DTYPE) # Table for logic operations
        self.values[:,:] = UNSET
        for i in range(y):
            for j in range(x):
                self.table[j,i] = VarLabel(self.tf, bg='gray')
                self.table[j,i].place(relx=j/x, rely=i/y, relwidth=1/x, relheight=1/y)

        # Calculate all possibilities
        self.pv = []
        self.ph = []
        for row in v: self.pv.append(self.get_all_possibilities(x, row))
        for col in h: self.ph.append(self.get_all_possibilities(y, col))

    def get_all_possibilities(self, x, row):
        amount = len(row)
        free = x - sum(row) - amount + 1
        cb = combinations_with_replacement(range(free + 1), amount + 1)
        # Filter out only combinations that have summ equal to free
        cb = filter(lambda x: sum(x) == free, cb)
        # Get all permutations of left combinations
        per = []
        for c in cb:
            per.extend(list(permutations(c)))
        # Filter out unique permutations
        per = list(set(per))
        # Build all possibilities as lists of cells
        result = []
        for p in per:
            temp = []
            for f, b in zip(p,row):
                temp += [EMPTY]*f
                temp += [FULL]*b + [EMPTY]
            temp += [EMPTY]*p[-1]
            result.append(temp[:-1])
        return array(result)

    def fill_cell_wiev(self, x, y):
        "Update wiev for single cell, and amount of possibilities for row and column."
        if   self.values[x, y] == FULL:  self.table[x, y].full()
        elif self.values[x, y] == EMPTY: self.table[x, y].empty()
        
        self.hplab[x].set(len(self.ph[x]))
        self.vplab[y].set(len(self.pv[y]))

    def step(self, x, y):
        sleep(DELAY)
        h = self.ph[x]
        v = self.pv[y]

        # Check if row or col chave only one possibility for this cell
        v_is_unique = sum(v[:,x] == v[:,x][0]) == len(v[:,x])
        h_is_unique = sum(h[:,y] == h[:,y][0]) == len(h[:,y])

        # Eliminate impossible configurations and update value table
        if   v_is_unique and not h_is_unique: self.ph[x] = h[h[:,y] == v[0][x]]; self.values[x,y] = v[0][x]
        elif h_is_unique and not v_is_unique: self.pv[y] = v[v[:,x] == h[0][y]]; self.values[x,y] = h[0][y]
        elif len(v) == 1: self.values[x,y] = v[0][x]
        elif len(h) == 1: self.values[x,y] = h[0][y]

    def loop(self):
        # Prepare list of all pairs of indicies
        done = False
        xs = zeros(self.values.shape, int)
        ys = zeros(self.values.shape, int)
        for x in range(len(xs)):
            for y in range(len(xs.T)):
                xs[x, y] = x
                ys[x, y] = y
                self.fill_cell_wiev(x,y)
        xs = xs.flatten()
        ys = ys.flatten()

        # End loop while last iteration made no change
        while not done:
            done = True
            idx = []
            for i, x, y in zip(range(len(xs)), xs, ys):
                if not self.values[x, y] in ALL:
                    done = False
                    self.step(x, y)
                    idx.append(i)
                    self.fill_cell_wiev(x,y)
                    sleep(0.01)
            # Leave only pairs that was used
            xs = xs[idx]
            ys = ys[idx]

        # If any row or column is unsolved, mark amout of left possibilities in red
        [i.error() for i in self.hplab if i.get() != '1']
        [i.error() for i in self.vplab if i.get() != '1']

        # Validate results
        self.validate()

    def validate(self):
        h = self.h
        v = self.v
        x = len(h)
        y = len(v)


        for i in range(x):
            col = self.values[i]
            temp = [0]
            for j in col:
                if j == FULL:
                    temp[-1] += 1
                else:
                    if temp[-1] != 0:
                        temp.append(0)
            if temp[-1] == 0:
                temp = temp[:-1]
            if temp != h[i]:
                for cell in self.table[i]:
                    cell.error()

        for i in range(y):
            row = self.values[:,i]
            temp = [0]
            for j in row:
                if j == FULL:
                    temp[-1] += 1
                else:
                    if temp[-1] != 0:
                        temp.append(0)
            if temp[-1] == 0:
                temp = temp[:-1]
            if temp != v[i]:
                for cell in self.table[:,i]:
                    cell.error()

    def mainloop(self):
        self.thread.start()
        super().mainloop()

if __name__ == "__main__":

    DELAY = 0.0    # Time to wait per cell in sec.
    DTYPE = uint8   # Type of states
    UNSET = 0       # Have to be DTYPE
    FULL = 1        # Have to be DTYPE
    EMPTY = 2       # Have to be DTYPE
    ALL = {FULL, EMPTY}

    # Colmuns from left to right. Numbers from top to bottom.
    h = [
        [2,2],
        [4,4,2,2],
        [4,6,4,2],
        [10,3,2],
        [2,5,5],
        [5,2,3,3],
        [4,4,1],
        [4,1,3,1],
        [4,4,2],
        [5,1,3,3],
        [2,2,2,5],
        [10,3,2],
        [2,1,6,3,3],
        [4,4,2,4],
        [2,2,6],
        [1,7],
        [6,2],
        [3,6],
        [5,3],
        [7]
    ]
    # Rows from top to bottom. Numbers from left to right.
    v = [
        [2,2],
        [4,4],
        [4,1,2],
        [3,5,3],
        [9],
        [11],
        [2,5,2],
        [5,5],
        [5,1,6],
        [5,4,2],
        [5,4,4],
        [7,4],
        [2,3,2,2,2],
        [2,5,3,5],
        [2,2,2,2,4,1],
        [4,3,6],
        [2,1,3,3],
        [2,2,7],
        [17],
        [5,7]
    ]

    wnd = Window()
    wnd.init(h,v)
    wnd.mainloop()