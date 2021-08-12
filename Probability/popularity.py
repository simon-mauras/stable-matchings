from sympy import Symbol, simplify, factor, expand, cancel, solve
from copy import deepcopy
from random import randint
from itertools import permutations, combinations
from scipy.optimize import minimize
import numpy as np

debug = False

from fractions import Fraction
#def Fraction(a, b=1): return a/b

######## DEFERRED ACCEPTANCE
def next(N, P, probaMatching, state, proba):
  global debug
  if proba == 0: return
  menPropositions, womenAnswers = state
  single = 0
  while single in womenAnswers:
    single += 1
  if single == N: # finished
    p = tuple(womenAnswers[i] for i in range(N))
    probaMatching[p] += proba
    if debug: print(womenAnswers, proba)
  else:
    Wbranches = [ w for w in range(N) if w not in menPropositions[single]]
    propSum = sum(P[single][w] for w in Wbranches)
    for w in Wbranches:
      if propSum != 0:
        propP = Fraction(P[single][w], propSum)
      else:
        propP = Fraction(1, len(Wbranches))
      Mbranches = [m for m in range(N) if w in menPropositions[m]]
      answSum = sum(P[m][w] for m in Mbranches)
      if answSum + P[single][w] != 0:
        answP = Fraction(P[single][w], answSum + P[single][w])
      else:
        answP = Fraction(1, len(Mbranches) + 1)
      state2 = deepcopy(state)
      state2[0][single].append(w)
      next(N, P, probaMatching, state2, proba * propP * (1-answP))
      state2[1][w] = single
      next(N, P, probaMatching, state2, proba * propP * answP)


def solve(N, P):
  # Init
  probaMPDA = { p : 0 for p in permutations(range(N)) }
  probaWPDA = { p : 0 for p in permutations(range(N)) }
  state = ([[] for i in range(N)], [None for i in range(N)])
  
  # Deferred acceptance
  next(N, P, probaMPDA, state, Fraction(1))
  next(N, P.T, probaWPDA, state, Fraction(1))
  
  # Results
  error = 0
  for p1 in permutations(range(N)):
    p2 = [None] * N
    for i in range(N):
      p2[p1[i]] = i
    p2 = tuple(p2)
    s = probaMPDA[p1] + probaWPDA[p2]
    """
    if s > 0:
      e = abs(probaMPDA[p1] - probaWPDA[p2]) / s
      error = max(error, e)
    """
    print(p1, cancel(probaMPDA[p1]), cancel(probaWPDA[p2]))
  return error

P = np.array([[2,4,0],[8,1,4],[0,0,0]])
W = Symbol("w")
#P = np.array([[W**1,W**2,0],[W**3,W**0,W**2],[0,0,0]])
print(solve(3, P))

