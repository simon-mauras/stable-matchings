import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from subprocess import Popen, PIPE
from itertools import combinations, permutations
import numpy as np
import pandas as pd
import math, os

def instance(nbStudents, schools, prefs):
  instance = "%d %d %d\n" % (nbStudents, len(schools), len(prefs))
  for u,c in schools:
    instance += "%d %d\n" % (u, c)
  for p in prefs:
    instance += " ".join(map(str, p)) + "\n"
  return instance

def run(nbStudents, schools, prefs, filename="tmp"):
  print("run N=%d, M=%d, P=%d" % (nbStudents, len(schools), len(prefs)))
  
  with open(filename + ".in", "w") as fin:
    fin.write(instance(nbStudents, schools, prefs))
  
  # TODO : choose solver
  slow = nbStudents
  for _,c in schools:
    slow *= 1+c
  if slow > 1000:
    print("using approximate solver")
    nbScores = 10 ** 7
    command = ["./approximate",
      "-S", str(nbScores // 1000),
      "-R", str(nbScores // (nbStudents-1))]
  else:
    print("using exact solver")
    nbScores = 10 ** 6
    command = ["./exact",
      "-S", str(nbScores // 1000),
      "-R", str(nbScores)]
  
  if not os.path.isfile(filename + ".out"):
    with open(filename + ".in") as fin:
      with open(filename + ".out", "w") as fout:
        p = Popen(command, stdin=fin, stdout=fout)
        p.wait()

def colormap(x):
  assert(0 <= x <= 1)
  r, g, b = min(2*x, 1), min(2-2*x, 1), 0
  return [0.5 + 0.5 * 0.7 * x for x in [r,g,b]]

def visualize(filename, target):
  
  with open(filename + ".in") as fin:
    data = [ tuple(map(int, l.strip().split())) for l in fin.readlines() ]
    nbStudents, nbSchools, nbPrefs = data[0]
    schools = data[1:1+nbSchools]
    prefs = data[1+nbSchools:]
  
  data = pd.read_csv(filename + ".out")
  
  colors = [ colormap(x) for x in np.linspace(0, 1, nbSchools) ]
  
  nonZero = []
  for i in range(nbPrefs):
    p = data["p%d" % i].to_numpy()
    if any(p): nonZero.append(i)
  
  with PdfPages(target) as pdf:
  
    ## plot outcome
    plt.figure(figsize=(10,5), tight_layout=True)
    score = data.score.to_numpy()
    p = [ data["probaOutcome%d" % j].to_numpy() for j in range(nbSchools) ]
    l = [ "school %d" % (j+1)
          for j in range(nbSchools) ]
    plt.stackplot(score, p, labels=l, edgecolor="k", colors=colors)
    plt.ylabel("outcome")
    plt.legend(loc=2)
    pdf.savefig()
    
    ## plot strategy
    plt.figure(figsize=(10,5), tight_layout=True)
    p = [ data["p%d" % i].to_numpy() * data.utility for i in nonZero ]
    l = [ str(tuple(j+1 for j in prefs[i])) for i in nonZero ]
    plt.stackplot(score, p, labels=l, edgecolor="k", alpha=0.5)
    for u,_ in schools:
      plt.axhline(u, linewidth=0.5, color="gray")
    #plt.plot(score, data.utility.to_numpy(), "k")
    plt.ylabel("expected utility")
    plt.legend(ncol=1+len(nonZero)//20, loc=2)#, fontsize="xx-small")
    pdf.savefig()
    
    ## plot info
    plt.figure(figsize=(10,5), tight_layout=True)
    plt.axis('tight')
    plt.axis('off')
    cell_text, cell_color = [], []
    headers = [
      "",
      "value",
      "capacity",
      "E[nb students]",
      "E[score student]"]
    for j in range(nbSchools):
      u, c = schools[j]
      t = data["probaOutcome%d" % j]
      e = t.mean() * nbStudents
      s = (t * data["score"]).sum() / t.sum()
      color = colors[j]
      cell_text.append(["school %d" % (j+1),
        "$v_{%d} = %d$" % (j+1,u),
        "$c_{%d} = %d$" % (j+1,c),
        "$\\approx %.2f$" % e, "$\\approx %.2f$" % s])
      cell_color.append([color] * 5)
    table = plt.table(cellText=cell_text, cellColours=cell_color,
                      colLabels=headers, loc="center", cellLoc="left")
    pdf.savefig()

## MAIN

instances = [
  ("equal", [1,1,1], None, None),
  ("small", [2,2,1], None, None),
  ("capacities", [5,4,3,2,1], [5,10,5,10,10], 50),
  ("lin", [ i+1      for i in reversed(range(10))], None, None),
  ("quad", [ (i+1)**2 for i in reversed(range(10))], None, None),
  ("exp", [ 2**i     for i in reversed(range(10))], None, None),
]

if __name__ == "__main__":
  for name, util, capa, nbStudents in instances:
    nbSchools = len(util)
    if capa is None: capa = [1] * nbSchools
    if nbStudents is None: nbStudents = sum(capa)
    for nbApplications in [1,2,3,4,5,10]:
      if nbApplications <= nbSchools:
        prefs = list(combinations(range(nbSchools), nbApplications))
        #prefs = list(permutations(range(nbSchools), nbApplications))
        #prefs = list(reversed(prefs))
        print(prefs)
        for mult in [1,2,5,100]:
          filename = "%s-A%d-X%d" % (name, nbApplications, mult)
          schools = [(u, c * mult) for u,c in zip(util, capa) ]
          run(nbStudents * mult, schools, prefs, "_data/" + filename)
          print("equilibrum computed")
          fig = visualize("_data/" + filename, "_figures/%s.pdf" % filename)
