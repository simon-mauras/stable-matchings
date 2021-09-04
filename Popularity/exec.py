import numpy as np
import json, math, random, os
from decimal import Decimal
from subprocess import Popen, PIPE

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import FixedLocator, FuncFormatter

def transform(t):
  if type(t) == dict:
    res = dict()
    for k in t:
      v = transform(t[k])
      try: res[int(k)] = v
      except: res[k] = v
    return res
  if type(t) == list:
    return np.array([transform(x) for x in t])
  return t

def run(name, nbMen, nbWomen, popM, popW, multM = None, multW = None, S = 1000):
  with open(name, "w") as f:
    if multM == None: multM = [1] * nbMen
    if multW == None: multW = [1] * nbWomen
    command = ["./main", str(S), str(nbMen), str(nbWomen)]
    p = Popen(command, stdin=PIPE, stdout=f)
    instance = ""
    for line in [multM, multW] + list(popM) + list(popW):
      instance += " ".join(map(str, line)) + "\n"
    p.communicate(instance.encode())

def min_nonzero(t):
  return t[t > 0].min()

def imshow(t, norm=None, cmap=plt.cm.viridis):
  cmap.set_bad("black")
  extent = (0, t.shape[1], 0, t.shape[0])
  return plt.imshow(t, origin="lower", norm=norm, cmap=cmap, extent=extent)

def errorbars(t, label=None, major=None):
  y, e = [], []
  for d in t:
    if any(d.values()):
      mean = sum(v * i for i,v in d.items()) / sum(d.values())
      var = sum(v * (i-mean)**2 for i,v in d.items()) / sum(d.values()) ** 2
      y.append(mean)
      e.append(5 * math.sqrt(var))
    else:
      y.append(0)
      e.append(0)
  y, e = np.array(y), np.array(e)
  p = plt.errorbar(range(len(t)), y, e, fmt="o", markersize=1, label=label)
  color = p[0].get_color()
  for b in p[2]: b.set_alpha(0.3)
  for a,b in zip(major, major[1:]+[len(t)]):
    _x, _y, _e = range(a, b), y[range(a, b)], e[range(a, b)]
    plt.plot(_x, _y, "-", color=color, linewidth=.5)

def matrix_scaling(pop):
  nbMen, nbWomen = pop.shape
  M, W = np.ones(nbMen), np.ones(nbWomen)
  for _ in range(100):
    col = pop.mean(axis=1)
    M, pop = M * col, pop / col.reshape((nbMen, 1))
    row = pop.mean(axis=0)
    W, pop = W * row, pop / row.reshape((1, nbWomen))
  v = math.sqrt(W.mean() / M.mean())
  M, W = M * v, W / v
  return [M, W, pop]
    

def plot(datafile, target):
  
  with open(datafile) as f:
    data = transform(json.load(f))
  
  ## proba of being matched
  S = sum(data["ALL_nbM"][0].values())
  data["ALL_couples"] = data["ALL_couples"] / S
  data["MOSM_couples"] = data["MOSM_couples"] / S
  data["WOSM_couples"] = data["WOSM_couples"] / S
  data["probaM"], data["probaW"] = [], []
  for d in data["ALL_nbM"]:
    v = d[0] if 0 in d else 0
    data["probaM"].append({0: v, 1: sum(d.values())-v})
  for d in data["ALL_nbW"]:
    v = d[0] if 0 in d else 0
    data["probaW"].append({0: v, 1: sum(d.values())-v})
    
  def set_ticks(ax, pos):
    label = { pos[i]:str(i) for i in range(len(pos)) }
    ax.set_minor_locator(FixedLocator(pos))
    ax.set_major_locator(FixedLocator(pos, nbins=11))
    ax.set_major_formatter(FuncFormatter(lambda x, pos: label[x]))
  
  def get_norm(t):
    sup, inf = t.max(), t[t>0].min()
    if sup / inf > 10:
      return LogNorm(inf/1.2, sup*1.2)
    return None
    
  ticksM = [0] + list(np.cumsum(data["multM"]))
  ticksW = [0] + list(np.cumsum(data["multW"]))
  
  with PdfPages(target) as pdf:
    plt.cm.viridis.set_bad("black")
  
    ## plot popularities
    idx = sum(([i] * m for i,m in enumerate(data["multM"])), [])
    idy = sum(([j] * w for j,w in enumerate(data["multW"])), [])
    popularityM = np.exp(data["logpopM"][idx,:][:,idy])
    popularityW = np.exp(data["logpopW"][idy,:][:,idx].T)
    
    fig = plt.figure(figsize=(10,4))
    ax = plt.subplot(1,2,1)
    imshow(popularityM, norm=get_norm(popularityM))
    plt.colorbar()
    plt.xlabel("woman's id")
    plt.ylabel("man's id")
    set_ticks(ax.xaxis, ticksW)
    set_ticks(ax.yaxis, ticksM)
    plt.title("popularity men give to women")
    
    ax = plt.subplot(1,2,2)
    imshow(popularityW, norm=get_norm(popularityW))
    plt.colorbar()
    plt.xlabel("woman's id")
    plt.ylabel("man's id")
    set_ticks(ax.xaxis, ticksW)
    set_ticks(ax.yaxis, ticksM)
    plt.title("popularity women give to men")
    
    plt.tight_layout()
    pdf.savefig()
    plt.close(fig)
    
    # matrix scaling 
    if set(data["multM"]) == {1} and set(data["multW"]) == {1}:
      popularity = popularityM * popularityW
      scaling = matrix_scaling(popularity)
      
      fig = plt.figure(figsize=(10,4))
      ax = plt.subplot(1,2,1)
      imshow(popularity, norm=get_norm(popularity))
      plt.colorbar()
      plt.xlabel("woman's id")
      plt.ylabel("man's id")
      set_ticks(ax.xaxis, ticksW)
      set_ticks(ax.yaxis, ticksM)
      plt.title("product of popularities")
      
      ax = plt.subplot(1,2,2)
      imshow(scaling[2])
      plt.colorbar()
      plt.xlabel("woman's id")
      plt.ylabel("man's id")
      set_ticks(ax.xaxis, ticksW)
      set_ticks(ax.yaxis, ticksM)
      plt.title("doubly stochastic matrix")
      
      plt.tight_layout()
      pdf.savefig()
      plt.close(fig)
      
      fig = plt.figure(figsize=(10,4))
      ax = plt.subplot(1,2,1)
      plt.xlabel("man's id")
      plt.ylabel("popularity")
      set_ticks(ax.xaxis, ticksM)
      plt.grid(which="major", linewidth=.5, alpha=.3)
      X = [0] + list(np.cumsum(data["multM"]))
      plt.plot(X[:-1], scaling[0], ".")
      for i in range(data["nbMen"]):
        if X[i+1] != X[i]:
          plt.plot([X[i], X[i+1]-1], [scaling[0][i]]*2, color=plt.cm.tab10(0))
      plt.title("coefficient men")
      if max(scaling[0])/min(scaling[0]) > 10:
        plt.yscale("log")
      
      ax = plt.subplot(1,2,2)
      plt.xlabel("woman's id")
      plt.ylabel("popularity")
      set_ticks(ax.xaxis, ticksW)
      plt.grid(which="major", linewidth=.5, alpha=.3)
      X = [0] + list(np.cumsum(data["multW"]))
      plt.plot(X[:-1], scaling[1], ".")
      for i in range(data["nbWomen"]):
        if X[i+1] != X[i]:
          plt.plot([X[i], X[i+1]-1], [scaling[1][i]]*2, color=plt.cm.tab10(0))
      plt.title("coefficient women")
      if max(scaling[1])/min(scaling[1]) > 10:
        plt.yscale("log")
    
      plt.tight_layout()
      pdf.savefig()
      plt.close(fig)
    
    """
    ## plot multiplicities
    if set(data["multW"]) != {1} or set(data["multW"]) != {1}:
      fig = plt.figure(figsize=(10,4))
      
      ax = plt.subplot(1,2,1)
      plt.xlabel("man's id")
      plt.ylabel("multiplicity")
      plt.plot(data["multM"], ".-")
      
      ax = plt.subplot(1,2,2)
      plt.xlabel("woman's id")
      plt.ylabel("multiplicity")
      plt.plot(data["multW"], ".-")
      
      plt.tight_layout()
      pdf.savefig()
    """
    
    ## plot extremal matchings
    fig = plt.figure(figsize=(10,4))
    norm = None #LogNorm(1/(data["nbMen"]*data["nbWomen"]),1)
    
    ax = plt.subplot(1,2,1)
    plt.title("Pr[matched in MOSM]")
    imshow(data["MOSM_couples"], norm=norm)
    set_ticks(ax.xaxis, ticksW)
    set_ticks(ax.yaxis, ticksM)
    plt.xlabel("woman's id")
    plt.ylabel("man's id")
    plt.colorbar()
    
    ax = plt.subplot(1,2,2)
    plt.title("Pr[matched in WOSM]")
    imshow(data["WOSM_couples"], norm=norm)
    set_ticks(ax.xaxis, ticksW)
    set_ticks(ax.yaxis, ticksM)
    plt.xlabel("woman's id")
    plt.ylabel("man's id")
    plt.colorbar()
    
    plt.tight_layout()
    pdf.savefig()
    plt.close(fig)
    
    ## plot extremal matchings
    fig = plt.figure(figsize=(10,4))
    # men's rank
    ax = plt.subplot(1,2,1)
    plt.title("outcomes for men")
    plt.ylim((0, data["nbWomen"]))
    plt.xlabel("man's id")
    plt.ylabel("E[rank partner]")
    set_ticks(ax.xaxis, ticksM)
    errorbars(data["WOSM_rankM"], "WOSM", ticksM[:-1])
    errorbars(data["MOSM_rankM"], "MOSM", ticksM[:-1])
    plt.grid(which="major", linewidth=.5, alpha=.3)
    plt.legend()
    # women's rank
    ax = plt.subplot(1,2,2)
    plt.title("outcomes for women")
    plt.ylim((0, data["nbMen"]))
    plt.xlabel("woman's id")
    plt.ylabel("E[rank partner]")
    set_ticks(ax.xaxis, ticksW)
    errorbars(data["WOSM_rankW"], "WOSM", ticksW[:-1])
    errorbars(data["MOSM_rankW"], "MOSM", ticksW[:-1])
    plt.grid(which="major", linewidth=.5, alpha=.3)
    plt.legend()
    # saving fig
    plt.tight_layout()
    pdf.savefig()
    plt.close(fig)
    
    ## plot number partners
    fig = plt.figure(figsize=(10,4))
    # men's rank
    ax = plt.subplot(1,2,1)
    plt.title("outcomes for men")
    plt.xlabel("man's id")
    set_ticks(ax.xaxis, ticksM)
    plt.axhline(1 + math.log(data["nbWomen"]),
      label="1 + log(nbWomen)", color="k", linestyle="--")
    errorbars(data["ALL_deltaM"], "1 + delta rank worst/best partner", ticksM[:-1])
    errorbars(data["ALL_nbM"], "number of stable partners", ticksM[:-1])
    plt.grid(which="major", linewidth=.5, alpha=.3)
    plt.ylim(bottom=0)
    plt.legend()
    # women's rank
    ax = plt.subplot(1,2,2)
    plt.title("outcomes for women")
    plt.xlabel("woman's id")
    set_ticks(ax.xaxis, ticksW)
    plt.axhline(1 + math.log(data["nbMen"]),
      label="1 + log(nbMen)", color="k", linestyle="--")
    errorbars(data["ALL_deltaW"], "1 + delta rank worst/best partner", ticksW[:-1])
    errorbars(data["ALL_nbW"], "number of stable partners", ticksW[:-1])
    plt.grid(which="major", linewidth=.5, alpha=.3)
    plt.ylim(bottom=0)
    plt.legend()
    # saving fig
    plt.tight_layout()
    pdf.savefig()
    plt.close(fig)

if __name__ == "__main__":
  instances = []

  # men are students (capacity = 1), women are schools (capacity > 1)
  capa = [ 3+i for i in range(10) ]
  M, W = int(1.2*sum(capa)), len(capa)
  mult = ([1]*M, capa)
  popularity = ([[w*math.log(0.9) for w in range(W)]] * M,
                [[m*math.log(0.9) for m in range(M)]] * W)
  instances.append(("school-choice", M, W, mult, popularity))

  # each person has capacity 1 or 2.
  M, W = 50, 50
  capa = [random.randint(1,2) for i in range(M)]
  mult = (capa, list(capa))
  random.shuffle(mult[1])
  popularity = ([[w*math.log(0.9) for w in range(W)]] * M,
                [[m*math.log(0.9) for m in range(M)]] * W)
  instances.append(("capacities", M, W, mult, popularity))
  
  # geometric popularity preferences
  M, W = 100, 100
  mult = ([1]*M, [1]*W)
  pop = [0.5, 0.9, 0.99, 1]
  for i in range(len(pop)):
    for j in range(i, len(pop)):
      name = "pop-%d-%d" % (100*pop[i], 100*pop[j])
      popularity = ([[w*math.log(pop[i]) for w in range(W)]] * M,
                    [[m*math.log(pop[j]) for m in range(M)]] * W)
      instances.append((name, M, W, mult, popularity))

  # two poles
  M, W = 100, 100
  mult = ([1]*M, [1]*W)
  popularity = (np.log(np.array([[ 1 + (m-M/3)**2 + (w-W/3)**2
                for w in range(W)] for m in range(M)])),
                np.log(np.array([[ 1 + (m-M/2)**2 + (w-3*W/4)**2
                for m in range(M)] for w in range(W)])))
  instances.append(("two-poles", M, W, mult, popularity))

  # waves
  M, W = 100, 100
  mult = ([1]*M, [1]*W)
  popularity = (np.log(np.array([[ 2 + np.cos(3*2*np.pi*(m+w)/(M+W))
                for w in range(W)] for m in range(M)])),
                np.log(np.array([[ 2 + np.cos(3*2*np.pi*(m-w)/(M+W))
                for m in range(M)] for w in range(W)])))
  instances.append(("waves", M, W, mult, popularity))

  for name, M, W, mult, popularity in instances:
    print("instance", name)
    filedata, fileplot = "_data/%s.json"%name, "_plot/%s.pdf"%name
    if not os.path.isfile(filedata):
      run(filedata, M, W, *popularity, *mult, S=10**4)
    plot(filedata, fileplot)
