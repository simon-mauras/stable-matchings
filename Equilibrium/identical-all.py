from subprocess import Popen, PIPE
import matplotlib.pyplot as plt
import numpy as np
from itertools import combinations, permutations
from utils import *

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
