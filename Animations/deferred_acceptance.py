#!/usr/bin/env python3

import random
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

def inverse(n, p):
  res = [n] * n
  for i,x in enumerate(p):
    res[x] = i
  return res

class DeferredAcceptance:

  def __init__(self, prefM, prefW):
    colors = ['white', 'lightgray', 'yellow', 'green', 'red']
    self.cmap = mpl.colors.ListedColormap(colors)
    boundaries = np.arange(-.5, len(colors))
    self.norm = mpl.colors.BoundaryNorm(boundaries, len(colors))
    
    self.nbMen, self.nbWomen = len(prefM), len(prefW)
    self.prefM, self.prefW = prefM, prefW
    self.rankM = [inverse(self.nbWomen, p) for p in self.prefM]
    self.rankW = [inverse(self.nbMen, p) for p in self.prefW]
    self.permM = list(range(self.nbMen))
    self.permW = list(range(self.nbWomen))
    self.__run__()
  
  def __run__(self):
    time = 0
    self.events = [("draw",)]
    prop = [0 for _ in range(self.nbMen)]
    self.match = [None for _ in range(self.nbWomen)]
    m1 = 0
    while m1 < self.nbMen:
      if prop[m1] == len(prefM[m1]):
        m1 += 1
      else:
        w = prefM[m1][prop[m1]]
        m2 = self.match[w]
        if m1 == m2: # already
          m1 += 1
        else: # propose
          self.events.append(("point", m1, w, 2))
          self.events.append(("draw",))
          if m2 is None:
            self.events.append(("point", m1, w, 3)) # accept new
            self.match[w] = m1
            m1 += 1
          elif self.rankW[w][m1] < self.rankW[w][m2]: 
            self.events.append(("point", m2, w, 4)) # reject previous
            self.events.append(("point", m1, w, 3)) # accept new
            self.match[w] = m1
            prop[m2] += 1
            m1 = m2
          else: # rejected
            prop[m1] += 1
            self.events.append(("point", m1, w, 4)) # accept new
          self.events.append(("draw",))
  
  def animation(self, fps=10):
    fig = plt.figure(figsize=(10,5), tight_layout=True)
    frames = [i for i,e in enumerate(self.events) if e[0] == "draw"]
    
    ax1 = plt.subplot(1,2,1)
    ax1.title.set_text("preferences of students")
    ax1.set_ylabel("id student")
    ax1.invert_yaxis()
    ax1.get_xaxis().set_visible(False)
    ax1.set_frame_on(False)
    ax1.yaxis.set_major_locator(mpl.ticker.MaxNLocator(integer=True))


    gridM = np.zeros((2*self.nbMen-1, self.nbWomen))
    Y = [ 1+i//2-0.3*(1-i%2*2) for i in range(2*self.nbMen) ]
    X = range(self.nbWomen+1)
    meshM = plt.pcolormesh(X, Y, gridM, cmap=self.cmap, norm=self.norm)
    
    ax2 = plt.subplot(1,2,2)
    ax2.title.set_text("preferences of schools")
    ax2.set_ylabel("id school")
    ax2.invert_yaxis()
    ax2.get_xaxis().set_visible(False)
    ax2.set_frame_on(False)
    ax2.yaxis.set_major_locator(mpl.ticker.MaxNLocator(integer=True))
    
    gridW = np.zeros((2*self.nbWomen-1, self.nbMen))
    Y = [ 1+i//2-0.3*(1-i%2*2) for i in range(2*self.nbWomen) ]
    X = range(self.nbMen+1)
    meshW = plt.pcolormesh(X, Y, gridW, cmap=self.cmap, norm=self.norm)
    
    def update(i):
      for event in self.events[frames[i]+1:frames[i+1]]:
        if event[0] == "point":
          m,w,x = event[1:]
          if self.rankM[m][w] < len(self.prefM[m]):
            gridM[2*m,self.rankM[m][w]] = x
          if self.rankW[w][m] < len(self.prefW[w]):
            gridW[2*w,self.rankW[w][m]] = x
      meshM.set_array(gridM)
      meshW.set_array(gridW)
      return meshM,meshW
    def init():
      for m in range(self.nbMen):
        gridM[2*m,:len(self.prefM[m])] = 1
      for w in range(self.nbWomen):
        gridW[2*w,:len(self.prefW[w])] = 1
      meshM.set_array(gridM)
      meshW.set_array(gridW)
      return meshM,meshW
    init()
    ani = mpl.animation.FuncAnimation(fig, update, len(frames)-1, init,
      interval=1000/fps, repeat_delay=1000, blit=False)
    return fig, ani
    
  def animationPerm(self, fps=10):
    fig = plt.figure(figsize=(5,5), tight_layout=True)
    plt.xlabel("woman (in receiving order)")
    plt.ylabel("man (in proposing order)")
    
    frames = [i for i,e in enumerate(self.events) if e[0] == "draw"]
    
    grid = np.zeros((self.nbMen, self.nbWomen))
    mesh = plt.pcolormesh(grid, cmap=self.cmap, norm=self.norm)
    
    lines = { e[1]: plt.plot([0,e[1],e[1]], [e[1],e[1],self.nbMen], "red")[0]
      for e in self.events if e[0] == "line"}
    
    def update(i):
      for event in self.events[frames[i]+1:frames[i+1]]:
        if event[0] == "point":
          m,w,x = event[1:]
          grid[self.permM[m],self.permW[w]] = x
        if event[0] == "line":
          x = event[1]
          lines[x].set_visible(True)
      mesh.set_array(grid)
      return [mesh]+list(lines.values())
    def init():
      grid[:] = 0
      mesh.set_array(grid)
      for x in lines:
        lines[x].set_visible(False)
      return [mesh]+list(lines.values())
    init()
    ani = mpl.animation.FuncAnimation(fig, update, len(frames)-1, init,
      interval=1000/fps, repeat_delay=5000, blit=True)
    return fig, ani

class DeferredAcceptanceRev(DeferredAcceptance):
  
  def __run__(self):
    time = 0
    self.events = [("draw",)]
    prop = [0 for _ in range(self.nbWomen)]
    self.match = [None for _ in range(self.nbMen)]
    w1 = 0
    while w1 < self.nbWomen:
      if prop[w1] == len(prefW[w1]):
        w1 += 1
      else:
        m = prefW[w1][prop[w1]]
        w2 = self.match[m]
        if w1 == w2: # already
          w1 += 1
        else: # propose
          self.events.append(("point", m, w1, 2))
          self.events.append(("draw",))
          if w2 is None:
            self.events.append(("point", m, w1, 3)) # accept new
            self.match[m] = w1
            w1 += 1
          elif self.rankM[m][w1] < self.rankM[m][w2]: 
            self.events.append(("point", m, w2, 4)) # reject previous
            self.events.append(("point", m, w1, 3)) # accept new
            self.match[m] = w1
            prop[w2] += 1
            w1 = w2
          else: # rejected
            prop[w1] += 1
            self.events.append(("point", m, w1, 4)) # accept new
          self.events.append(("draw",))

class DeferredAcceptanceSeq(DeferredAcceptance):
  def __run__(self):
    order = []
    self.events = [("draw",)]
    prop = [0 for _ in range(self.nbMen)]
    self.match = [None for _ in range(self.nbWomen)]
    m1 = 0
    separator = 0
    while m1 < self.nbMen:
      if prop[m1] == len(prefM[m1]):
        m1 += 1
      else:
        w = prefM[m1][prop[m1]]
        m2 = self.match[w]
        if m1 == m2: # already
          m1 += 1
        else: # propose
          if m2 is None or self.rankW[w][m1] < self.rankW[w][m2]:
            self.events.append(("point", m1, w, 2))
            self.events.append(("draw",))
            self.match[w] = m1
            self.events.append(("point", m1, w, 3)) # accept new
            for m in self.prefW[w][self.rankW[w][m1]+1:]:
              self.events.append(("point", m, w, 4)) # future rejects
            for m in self.prefW[w][:self.rankW[w][m1]+1]:
              separator = max(m, separator)
            if m2 is None:
              if separator == m1:
                print("separator", m1)
                self.events.append(("line", m1+1))
              order.append(w)
              m1 += 1
            else:
              prop[m2] += 1
              m1 = m2
            self.events.append(("draw",))
          else: # rejected
            prop[m1] += 1
    order.extend(list(set(range(self.nbWomen))-set(order)))
    #self.permW = inverse(self.nbWomen, order)

class DeferredAcceptanceDay(DeferredAcceptance):
  def __run__(self):
    time = 0
    self.events = [("draw",)]
    prop = [0 for _ in range(self.nbMen)]
    self.match = [None for _ in range(self.nbWomen)]
    stop = False
    while not stop:
      stop = True
      answer = []
      for m1 in range(self.nbMen):
        matched = prop[m1] > 0 and self.match[prefM[m1][prop[m1]-1]] == m1
        if not matched and prop[m1] < len(prefM[m1]):
          stop = False
          w = prefM[m1][prop[m1]]
          m2 = self.match[w]
          self.events.append(("point", m1, w, 2))
          prop[m1] += 1
          if m2 is None:
            answer.append(("point", m1, w, 3)) # accept new
            self.match[w] = m1
          elif self.rankW[w][m1] < self.rankW[w][m2]: 
            answer.append(("point", m2, w, 4)) # reject previous
            answer.append(("point", m1, w, 3)) # accept new
            self.match[w] = m1
          else:
            answer.append(("point", m1, w, 4)) # accept new
      self.events.append(("draw",))
      self.events.extend(answer)
      self.events.append(("draw",))

def random_popularity(logpop):
  # sort by increasing Xi ~ Exp(e**logpop[i])
  # log(Xi) = log(-log(unif))-logpop[i]
  s,t = zip(*sorted([(np.log(-np.log(random.random()))-p, i)
    for i,p in enumerate(logpop)]))
  return t#[:len(t)//2]

if __name__ == "__main__":
  random.seed(72)
  nbMen, nbWomen = 20, 20
  #popM = [ np.log(1/(m+1)**1.1) for m in range(nbMen)]
  #popW = [ np.log(1/(w+1)**1.1) for w in range(nbWomen)]
  popM = [ np.log(0.5)*m for m in range(nbMen)]
  popW = [ np.log(1)*w for w in range(nbWomen)]
  prefM = [random_popularity(popW) for _ in range(nbMen)]
  prefW = [random_popularity(popM) for _ in range(nbWomen)]
  
  mode = 1
  if mode == 1:
    key = "_geomunif"
    DA = DeferredAcceptance(prefM, prefW)
    fig, ani = DA.animation(fps=20)
    ani.save("da_student"+key+".mp4")
    plt.savefig("da_student"+key+".png")
    plt.show()
    
    DA2 = DeferredAcceptanceRev(prefM, prefW)
    fig, ani = DA2.animation(fps=50)
    ani.save("da_school"+key+".mp4")
    plt.savefig("da_school"+key+".png")
    plt.show()
    
  elif mode == 2:
    DA = DeferredAcceptanceSeq(prefM, prefW)
    fig, ani = DA.animation(fps=100)
  elif mode == 3:
    DA = DeferredAcceptanceDay(prefM, prefW)
    fig, ani = DA.animation(fps=20)
  elif mode == 4:
    DA = DeferredAcceptanceSeq(prefM, prefW)
    fig, ani = DA.animationPerm(fps=20)
  """
  with open("deferred_acceptance.html", "w") as f:
    f.write(ani.to_jshtml())
  plt.savefig("deferred_acceptance.png")
  ani.save("deferred_acceptance.mp4")
  """
  plt.show()
