import numpy as np
import json, math, random
from subprocess import Popen, PIPE

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.backends.backend_pdf import PdfPages

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

def run(pop, S = 1000):
  nbMen, nbWomen = pop.shape
  command = ["./main", str(S), str(nbMen), str(nbWomen)]
  p = Popen(command, stdin=PIPE, stdout=PIPE)
  instance = " ".join(map(str, pop.reshape(-1)))
  output,_ = p.communicate(instance.encode())
  return transform(json.loads(output.decode()))

def min_nonzero(t):
  return t[t > 0].min()

def imshow(t, norm=None, cmap=plt.cm.viridis):
  cmap.set_bad("black")
  plt.imshow(t, origin="lower", norm=norm, cmap=cmap)

def errorbars(t, label=None):
  y, e = [], []
  for d in t:
    mean = sum(v * i for i,v in d.items()) / sum(d.values())
    var = sum(v * (i-mean)**2 for i,v in d.items()) / sum(d.values()) ** 2
    y.append(mean)
    e.append(5 * math.sqrt(var))
  y, e = np.array(y), np.array(e)
  plt.plot(range(len(t)), y, label=label)
  plt.fill_between(range(len(t)), y-e, y+e,
    alpha=0.1)

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
  return M, W, pop
    

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
  
  with PdfPages(target) as pdf:
    plt.cm.viridis.set_bad("black")
  
    ## plot popularities
    scaling = matrix_scaling(data["popularity"])
    last = scaling[2].max() - scaling[2].min() > 1e-3
    
    plt.figure(figsize=(14+4*last,4))
    plt.subplot(1,3+last,1)
    norm = LogNorm(min_nonzero(data["popularity"])/2, data["popularity"].max()*2)
    plt.imshow(data["popularity"],
      origin="lower", norm=norm, cmap=plt.cm.viridis)
    plt.colorbar()
    plt.xlabel("woman's id")
    plt.ylabel("man's id")
    plt.title("popularity of each pair")
    
    plt.subplot(1,3+last,2)
    plt.xlabel("man's id")
    plt.ylabel("popularity")
    #plt.yscale("log")
    plt.plot(scaling[0])
    
    plt.subplot(1,3+last,3)
    plt.xlabel("woman's id")
    plt.ylabel("popularity")
    #plt.yscale("log")
    plt.plot(scaling[1])
    
    if last:
      plt.subplot(1,4,4)
      plt.imshow(scaling[2], origin="lower", cmap=plt.cm.viridis)
      plt.colorbar()
      plt.xlabel("woman's id")
      plt.ylabel("man's id")
      plt.title("normalized popularity of each pair")
    
    plt.tight_layout()
    pdf.savefig()
    
    ## plot extremal matchings
    fig = plt.figure(figsize=(14,4))
    norm = LogNorm(1/S,1)
    plt.subplot(1,3,1)
    plt.title("Pr[matched in some matching]")
    im = plt.imshow(data["ALL_couples"],
      origin="lower", norm=norm, cmap=plt.cm.viridis)
    plt.xlabel("woman's id")
    plt.ylabel("man's id")
    plt.colorbar()
    
    plt.subplot(1,3,2)
    plt.title("Pr[matched in WOSM]")
    plt.imshow(data["WOSM_couples"],
      origin="lower", norm=norm, cmap=plt.cm.viridis)
    plt.xlabel("woman's id")
    plt.ylabel("man's id")
    plt.colorbar()
    
    plt.subplot(1,3,3)
    plt.title("Pr[matched in MOSM]")
    plt.imshow(data["MOSM_couples"],
      origin="lower", norm=norm, cmap=plt.cm.viridis)
    plt.xlabel("woman's id")
    plt.ylabel("man's id")
    plt.colorbar()
    
    plt.tight_layout()
    pdf.savefig()
    
    ## plot extremal matchings
    plt.figure(figsize=(10,4))
    # women's rank
    plt.subplot(1,2,1)
    plt.title("outcomes for women")
    plt.ylim((0, data["nbMen"]))
    plt.xlabel("woman's id")
    plt.ylabel("expected rank of partner")
    errorbars(data["WOSM_rankW"], "WOSM")
    errorbars(data["MOSM_rankW"], "MOSM")
    plt.legend()
    """
    plt.twinx()
    plt.ylim((0, 1))
    plt.ylabel("probability of being matched")
    errorbars(data["probaW"])
    """
    # men's rank
    plt.subplot(1,2,2)
    plt.title("outcomes for men")
    plt.ylim((0, data["nbWomen"]))
    plt.xlabel("man's id")
    plt.ylabel("expected rank of partner")
    errorbars(data["WOSM_rankM"], "WOSM")
    errorbars(data["MOSM_rankM"], "MOSM")
    plt.legend()
    """
    plt.twinx()
    plt.ylim((0, 1))
    plt.ylabel("probability of being matched")
    errorbars(data["probaM"])
    """
    # saving fig
    plt.tight_layout()
    pdf.savefig()
    
    
    ## plot number partners
    maxi = 1
    maxi = max(maxi, max(max(d.keys()) for d in data["ALL_deltaW"]))
    maxi = max(maxi, max(max(d.keys()) for d in data["ALL_deltaM"]))
    plt.figure(figsize=(10,4))
    # women's rank
    plt.subplot(1,2,1)
    plt.title("outcomes for women")
    plt.xlabel("woman's id")
    plt.axhline(1 + math.log(data["nbMen"]),
      label="1 + log(nbMen)", color="k", linestyle="--")
    errorbars(data["ALL_deltaW"], "1 + delta rank worst/best partner")
    errorbars(data["ALL_nbW"], "number of stable partners")
    plt.ylim(bottom=0)
    plt.legend()
    # men's rank
    plt.subplot(1,2,2)
    plt.title("outcomes for men")
    plt.xlabel("man's id")
    plt.axhline(1 + math.log(data["nbWomen"]),
      label="1 + log(nbWomen)", color="k", linestyle="--")
    errorbars(data["ALL_deltaM"], "1 + delta rank worst/best partner")
    errorbars(data["ALL_nbM"], "number of stable partners")
    plt.ylim(bottom=0)
    plt.legend()
    # saving fig
    plt.tight_layout()
    pdf.savefig()

M, W = 100, 100
#p, q = [1] * (M//2) + [2] * (M//2), [1] * (W//2) + [2] * (W//2)
p = [ 0.99 ** i for i in range(M) ]
q = [ 0.95 ** i for i in range(W) ]
#p = [ (i+10) ** .1 for i in reversed(range(M)) ]
#q = [ (i+10) ** -.1 for i in range(W) ]
popularity = np.zeros((M, W))
for i in range(M):
  for j in range(W):
    if random.random() > 0.:
      popularity[i][j] = p[i] * q[j]  
      #popularity[i][j] = (i-M//2) ** 2 + (j-W//2) ** 2
      #popularity[i][j] = .1 + math.sin(i*5*math.pi/M) ** 2 + (j/W - 1/2) ** 2
plot(run(popularity, S=1000))
