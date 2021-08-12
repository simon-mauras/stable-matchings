import math
import numpy as np
import matplotlib.pyplot as plt
from itertools import product
from scipy.stats import hypergeom

mode_rand = True

# game parameter
n, m = 3, 3
risk = 1
v = [lambda t: 0, lambda t: risk+1, lambda t: risk]
s = [lambda t: 0, lambda t: t.dot((2,1)), lambda t: t.dot((1,2))]
c = (n,1,2)

for risk in [1/10,1,10,100]:
  for k,sz in [(100,50), (1000,20), (10000,5)]:
    T = [ np.random.random(2) for _ in range(k) ]

    def proba(x, c):
      global k, n
      return sum(hypergeom.pmf(i,k-1,x,n-1) for i in range(c))

    # compute equilibrium
    print("compute equilibrium")

    X = [0] * m
    strat = [(-1, None) for _ in range(k) ]
    l = [ sorted(range(k), key=lambda i: s[j](T[i])) for j in range(m)]
    while sum(map(len, l)) > 0:
      found = False
      for j in range(m):
        if len(l[j]) > 0:
          i = l[j][-1]
          if strat[i] == (-1,None):
            e = [ v[j2](T[i]) * proba(X[j2], c[j2]) for j2 in range(m)]
            if e[j] == max(e):
              strat[i] = (e[j], j)
              X[j] += 1
          else:
            l[j].pop()

    # plotting
    print("plotting")
    plt.figure(figsize=(5,5), tight_layout=True)

    colors = [(0.5,0.75,0.5),(0.5,0.5,0.75)]
    for j,col in zip(range(1,m),colors):
      X,Y = zip(*[T[i] for i in range(k) if strat[i][1] == j])
      plt.plot(X, Y, '.', label=str(j), markersize=sz, color=col)
    plt.legend(loc=2)

    plt.savefig("_figures/identical-schools-r%d-k%d.png" % (risk,k))
    plt.close()

