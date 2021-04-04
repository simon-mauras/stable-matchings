import numpy as np
import json, math, random
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

def run(pop, multM = None, multW = None, S = 1000):
  nbMen, nbWomen = pop.shape
  if multM == None: multM = [2] * nbMen
  if multW == None: multW = [2] * nbWomen
  command = ["./main", str(S), str(nbMen), str(nbWomen)]
  p = Popen(command, stdin=PIPE, stdout=PIPE)
  instance = ""
  for line in [multM, multW] + list(pop):
    instance += " ".join(map(str, line)) + "\n"
  output,_ = p.communicate(instance.encode())
  return transform(json.loads(output.decode()))

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
    

def plot(data, target="plot.pdf"):

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
    
  ticksM = [0] + list(np.cumsum(data["multM"]))
  ticksW = [0] + list(np.cumsum(data["multW"]))
  
  with PdfPages(target) as pdf:
    plt.cm.viridis.set_bad("black")
  
    ## plot popularities
    idx = sum(([i] * m for i,m in enumerate(data["multM"])), [])
    idy = sum(([i] * m for i,m in enumerate(data["multW"])), [])
    popularity = data["popularity"][idx,:][:,idy]
    scaling = matrix_scaling(data["popularity"])
    last = scaling[2].max() - scaling[2].min() > 1e-3
    scaling[2] = scaling[2][idx,:][:,idy]
    
    plt.figure(figsize=(14+4*last,4))
    ax = plt.subplot(1,3+last,1)
    norm = LogNorm(min_nonzero(popularity)/2, popularity.max()*2)
    imshow(popularity, norm=norm)
    plt.colorbar()
    plt.xlabel("woman's id")
    plt.ylabel("man's id")
    set_ticks(ax.xaxis, ticksW)
    set_ticks(ax.yaxis, ticksM)
    plt.title("popularity of each pair")
    
    ax = plt.subplot(1,3+last,2)
    plt.xlabel("man's id")
    plt.ylabel("popularity")
    set_ticks(ax.xaxis, ticksM)
    plt.grid(which="major", linewidth=.5, alpha=.3)
    X = [0] + list(np.cumsum(data["multM"]))
    plt.plot(X[:-1], scaling[0], ".")
    for i in range(data["nbMen"]):
      if X[i+1] != X[i]:
        plt.plot([X[i], X[i+1]-1], [scaling[0][i]]*2, color=plt.cm.tab10(0))
    plt.yscale("log")
    
    ax = plt.subplot(1,3+last,3)
    plt.xlabel("woman's id")
    plt.ylabel("popularity")
    set_ticks(ax.xaxis, ticksW)
    plt.grid(which="major", linewidth=.5, alpha=.3)
    X = [0] + list(np.cumsum(data["multW"]))
    plt.plot(X[:-1], scaling[1], ".")
    for i in range(data["nbWomen"]):
      if X[i+1] != X[i]:
        plt.plot([X[i], X[i+1]-1], [scaling[1][i]]*2, color=plt.cm.tab10(0))
    plt.yscale("log")
    
    if last:
      ax = plt.subplot(1,4,4)
      imshow(scaling[2])
      plt.colorbar()
      plt.xlabel("woman's id")
      plt.ylabel("man's id")
      set_ticks(ax.xaxis, ticksW)
      set_ticks(ax.yaxis, ticksM)
      plt.title("normalized popularity of each pair")
    
    plt.tight_layout()
    pdf.savefig()
    
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
    fig = plt.figure(figsize=(14,4))
    norm = LogNorm(1/(data["nbMen"]*data["nbWomen"]),1)
    ax = plt.subplot(1,3,1)
    plt.title("Pr[matched in some matching]")
    im = imshow(data["ALL_couples"], norm=norm)
    set_ticks(ax.xaxis, ticksW)
    set_ticks(ax.yaxis, ticksM)
    plt.xlabel("woman's id")
    plt.ylabel("man's id")
    plt.colorbar()
    
    ax = plt.subplot(1,3,2)
    plt.title("Pr[matched in MOSM]")
    imshow(data["MOSM_couples"], norm=norm)
    set_ticks(ax.xaxis, ticksW)
    set_ticks(ax.yaxis, ticksM)
    plt.xlabel("woman's id")
    plt.ylabel("man's id")
    plt.colorbar()
    
    ax = plt.subplot(1,3,3)
    plt.title("Pr[matched in WOSM]")
    imshow(data["WOSM_couples"], norm=norm)
    set_ticks(ax.xaxis, ticksW)
    set_ticks(ax.yaxis, ticksM)
    plt.xlabel("woman's id")
    plt.ylabel("man's id")
    plt.colorbar()
    
    plt.tight_layout()
    pdf.savefig()
    
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
    
    ## plot number partners
    plt.figure(figsize=(10,4))
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


# each person has capacity 1 or 2.
M, W = 50, 50
capa = [random.randint(1,2) for i in range(M)]
mult = (capa, list(capa))
random.shuffle(mult[1])
p = [ 0.9 ** i for i in range(M) ]
q = [ 0.95 ** i for i in range(W) ]

# men are students (capacity = 1), women are schools (capacity > 1)
capa = [ 3+i for i in range(10) ]
M, W = int(1.2*sum(capa)), len(capa)
mult = ([1]*M, capa)
p = [ 0.95 ** i for i in range(M) ]
q = [ 0.5 ** i for i in range(W) ]

popularity = np.zeros((M, W))
for i in range(M):
  for j in range(W):
    if random.random() > 0.05:
      popularity[i][j] = p[i] * q[j]  
      #popularity[i][j] = (i-M//2) ** 2 + (j-W//2) ** 2
      #popularity[i][j] = .1 + math.sin(i*5*math.pi/M) ** 2 + (j/W - 1/2) ** 2
plot(run(popularity, *mult, S=10000))
