import os, time, matplotlib
import numpy as np
import matplotlib.pyplot as plt
from subprocess import Popen, PIPE
matplotlib.rcParams['text.usetex'] = True

def run(repeat, nbMen, nbWomen):
  filename = "_data/data-%d-%d-%d.txt" % (repeat, nbMen, nbWomen)
  command = ["./main", str(repeat), str(nbMen), str(nbWomen)]
  if not os.path.isfile(filename):
    t = time.time()
    with open(filename, "w") as f:
      p = Popen(command, stdout=f)
      out,err = p.communicate()
    print("done in %.2fs." % (time.time()-t))
  tab = []
  with open(filename, "r") as f:
    for l in f.readlines():
      tab.append(list(map(int, l.strip().split())))
  return np.array(tab)

S, W = 10000, 1000

plt.figure(figsize=(10,8), tight_layout=True)
for k in [0,1,2,3,W//10,W//2]:
  if k == 0:
    v = np.pi**2/6
  else:
    v = sum(1/i for i in range(1,k+1))/k
  plt.axvline(v*W, color="k")
  plt.text(v*W, W/3, "$\gamma_{%d} \cdot W$" % k,
    horizontalalignment="right",
    verticalalignment="center",
    rotation="vertical")
  print("W gamma_%d ="%k, v*W)  
plt.axvline(W**2/np.log(W), color="k")
plt.text(W**2/np.log(W), W/3, "$\displaystyle\\frac{W^2}{\ln W}$",
    horizontalalignment="right",
    verticalalignment="center",
    rotation="vertical")
print("W^2/ln W =", W**2/np.log(W))  

Ms = [W//2,9*W//10,W-3,W-2,W-1,W,W+1,W+2,W+3,11*W//10]
for M in Ms:
  print("M =", M)
  data = run(S, M, W)
  days, prop, stop = data[:,0], data[:,1]/S, data[:,2]
  
  mean = (stop*days).sum() / stop.sum()
  std = np.sqrt((stop*(days-mean)**2).sum() / stop.sum())
  print("stop =", mean, "+-", 5*std/np.sqrt(S))
  
  mean = int(mean)
  p = plt.plot(days[:mean+1], prop[:mean+1], label="$M = %d$" % M)
  plt.plot([mean+1],[prop[mean]], "o", color=p[0].get_color())

plt.xscale("log")
plt.yscale("log")
plt.legend()
plt.savefig("_figures/figure.pdf")
#plt.show()
