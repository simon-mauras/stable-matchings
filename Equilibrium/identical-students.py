import math
import numpy as np
import matplotlib.pyplot as plt
from itertools import product

mode_rand = True

# game parameter
n = 3
f = lambda x:np.linalg.norm(x)
risk = 0
v = [lambda t: 0, lambda t: risk+t[0], lambda t: risk+t[1]]
c = (n,1,2)
A = ((1,0),(2,0))

for risk in [0,1,2,5]:
  for k,sz in [(100,50), (1000,20), (10000,5)]:
    T = [ np.random.random(2) for _ in range(k) ]
    T.sort(key=f, reverse=True)

    def school(r, a):
      for j in a:
        if r[j] > 0:
          return j
      return None

    # compute equilibrium
    print("compute equilibrium")

    q = {c: 1}
    strat = [(-1, None) for _ in range(k) ]
    for i,t in enumerate(T):
      # find the best move
      for a in A:
        val = 0
        for r,p in q.items():
          val += p * v[school(r, a)](t)
        strat[i] = max(strat[i], (val, a))
      val, a = strat[i]
      # update the distribution
      for act,p in reversed(list(q.items())):
        next = list(act)
        next[school(act, a)] -= 1
        next = tuple(next)
        d = (n-1-sum(c)+sum(act))/(k-i)
        if d > 0:
          if next not in q:
            q[next] = 0
          q[next] += p*d
          q[act] -= p*d

    # plotting
    print("plotting")
    plt.figure(figsize=(5,5), tight_layout=True)

    colors = [(0.5,0.75,0.5),(0.5,0.5,0.75)]
    for a,col in zip(A,colors):
      X,Y = zip(*[T[i] for i in range(k) if strat[i][1] == a])
      plt.plot(X, Y, '.', label=str(a), markersize=sz, color=col)
    plt.legend(loc=2)

    plt.savefig("_figures/identical-students-r%d-k%d.png" % (risk,k))
    plt.close()

