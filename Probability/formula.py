import random
import numpy as np
from sympy import Matrix
from itertools import product, permutations
import matplotlib.pyplot as plt

def inverse(M):
  return Matrix([[ 1 / M[i,j]
    for j in range(M.shape[1])] for i in range(M.shape[0])])

def hasMatching(v):
  N = v.shape[0]
  for i in range(N):
    if all(v[i,j] == 0 for j in range(N)):
      return False
    if all(v[j,i] == 0 for j in range(N)):
      return False
  for l in permutations(range(N)):
    if all(v[i,l[i]] for i in range(N)):
      return True
  return False

def getVal(MP, MQ):
  N = MP.shape[0]
  dP, dQ = MP.det(), MQ.det()
  if dP * dQ == 0: return 0
  vP, vQ = 1, 1
  for i in range(N):
    vP *= sum(MP[i,:])
    vQ *= sum(MQ[:,i])
  val =  dP * dQ / (vP * vQ)
  return val

def compute(N, P, Q):
  P, Q = inverse(P), inverse(Q)
  result = Matrix([[0]*N for _ in range(N)])
  for p in product([0,1], repeat=N**2):
    v = Matrix(p).reshape(N,N)
    if hasMatching(v):
      print("\r", v, end="", flush=True)
      MP = v.multiply_elementwise(P)
      MQ = v.multiply_elementwise(Q)
      pr = getVal(MP, MQ)
      assert(pr != 0)
      m = MP.multiply_elementwise(MP.inv().T)
      result += pr * (-1) ** (N + int(sum(p))) * m
  print("\r", end="")
  return result

if __name__ == "__main__":
  N = 4
  random.seed(42)
  P = Matrix([[ random.randint(1,1000) for j in range(N)] for i in range(N)])
  Q = Matrix([[ random.randint(1,1000) for j in range(N)] for i in range(N)])
  
  from run import solve, proba_match
  res1 = Matrix(proba_match(N, N, solve(P, Q)))
  print(res1)
  
  res2 = compute(N, P, Q)
  print(res2)
  
  print(np.array(res1, dtype=float))
  print(np.array(res2, dtype=float))
  print(res1 == res2)

