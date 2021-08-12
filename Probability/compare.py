import numpy as np
from run import solve
from fractions import Fraction
from subprocess import Popen, PIPE

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.colors import LogNorm
from matplotlib.patches import ConnectionPatch
from matplotlib.offsetbox import AnchoredOffsetbox, DrawingArea
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

def draw_matching(match, nbMen, nbWomen):
  width, height = 25, 50
  da = DrawingArea(width, height)
  coordM = [(  width/4, height*(nbMen-i)/(nbMen+1))     for i in range(nbMen)]
  coordW = [(3*width/4, height*(nbWomen-i)/(nbWomen+1)) for i in range(nbWomen)]
  for idWoman in range(nbWomen):
    if match[idWoman] == -1:
      xdata = [coordW[idWoman][0]]
      ydata = [coordW[idWoman][1]]
      da.add_artist(Line2D(xdata, ydata, marker="o",
        markerfacecolor='w', color="k", linewidth=1))
  for idMan in range(nbMen):
    if idMan not in match:
      xdata = [coordM[idMan][0]]
      ydata = [coordM[idMan][1]]
      da.add_artist(Line2D(xdata, ydata, marker="o",
        markerfacecolor='w', color="k", linewidth=1))
  for idWoman,idMan in enumerate(match):
    if idMan != -1:
      xdata = [coordM[idMan][0], coordW[idWoman][0]]
      ydata = [coordM[idMan][1], coordW[idWoman][1]]
      da.add_artist(Line2D(xdata, ydata, marker="o",
        markerfacecolor='w', color="k", linewidth=1))
  return da

from scipy.optimize import minimize
def best_angles(anglesB):
  def f(x, angles):
    result = 0
    for i in range(len(x)):
      result += abs(angles[i] - x[i])
      v = (x[i] - x[i-1]) % 360
      d = min(abs(v), abs(v-360), abs(v+360))
      result += 1.6 ** (10 - d) # parameters
    return result ** 0.1
  anglesA = minimize(f, anglesB, args=(anglesB,))
  return anglesA.x

def draw_figure(popularity, data):
  # init figure
  fig, ax = plt.subplots(constrained_layout=True, figsize=(7,7))
  # pie plot
  wedges,_,texts = ax.pie([p for p,_ in data], 
    startangle=90, counterclock=False,
    autopct="", pctdistance=0.75,
    wedgeprops={'width':0.5,'linewidth':1,'edgecolor':'k','antialiased': True},
    colors="w")
  # matrix plot
  nbMen, nbWomen = popularity.shape
  """
  axmat = inset_axes(ax, "20%", "20%", loc="center")
  axmat.xaxis.tick_top()
  xticks, yticks = list(range(1,1+nbWomen)), list(range(1,1+nbMen))
  axmat.set_xticks(xticks)
  axmat.set_yticks(yticks)
  axmat.set_xticklabels("$w_{%d}$" % i for i in xticks)
  axmat.set_yticklabels("$m_{%d}$" % i for i in yticks)
  axmat.imshow(popularity,
    norm=LogNorm(vmin=0.01,vmax=1000), cmap="gray_r", 
    extent=(0.5, nbWomen+0.5, nbMen+0.5, 0.5))
  for idMan in range(nbMen):
    for idWoman in range(nbWomen):
      axmat.text(1+idWoman, 1+idMan, str(popularity[idMan, idWoman]))
  """
  # angles
  anglesB = [(w.theta2 - w.theta1)/2. + w.theta1 for w in wedges]
  anglesA = best_angles(anglesB)
  # plot matchings
  plt.rc('mathtext', fontset='stix')
  ax.set_xlim(-1.6, 1.6)
  ax.set_ylim(-1.6, 1.6)
  matchings = [ (p,m,w,t) for (p,m),w,t in zip(data, wedges, texts)]
  for i, (p, m, w, t) in enumerate(matchings):
    radius = 1.25
    if abs(w.theta2 - w.theta1) >= 10:
      t.set_text("$\\frac{%d}{%d}$" % (p.numerator, p.denominator))
      t.set_size(22)
    angA, angB = anglesA[i], anglesB[i]
    xA = radius * np.cos(np.deg2rad(angA))
    yA = radius * np.sin(np.deg2rad(angA))
    xB = np.cos(np.deg2rad(angB))
    yB = np.sin(np.deg2rad(angB))
    box = AnchoredOffsetbox(
      child=draw_matching(m, nbMen, nbWomen),
      loc='center', frameon=True,
      bbox_to_anchor=(xA, yA),
      bbox_transform=ax.transData,
      pad=0., borderpad=0.)
    ax.add_artist(box)
    con = ConnectionPatch(
      xyA = (xA,yA), xyB = (xB,yB),
      coordsA="data", coordsB="data")
    ax.add_artist(con)

######## MAIN

if __name__ == "__main__":
  
  instances = []

  instances.append(np.array([
    [2, 4, 0],
    [8, 1, 4]
  ]))

  """
  instances.append(np.array([[1,3,5]]).T * np.array([[1,2,3]]))

  instances.append(np.array([
    [1, 1, 0, 0],
    [1, 1, 1, 0],
    [0, 1, 1, 1],
    [0, 0, 1, 1],
    [0, 1, 0, 1]
  ]))

  instances.append(instances[-1].T)
  """

  datas = [solve(popularity, popularity) for popularity in instances]
  print(datas)

  ## Hardcoded examples: popularity preferences
  instances.append(np.array([[2, 4, 0],[8, 1, 4]]))
  instances.append(np.array([[2, 4, 0],[8, 1, 4]]))
  datas.append(sorted([
  (Fraction(43, 975), (0, 1, -1)),
  (Fraction(44, 325), (0, -1, 1)),
  (Fraction(352, 585), (1, 0, -1)),
  (Fraction(128, 585), (-1, 0, 1))
  ]))
  datas.append(sorted([
  (Fraction(41, 1125), (0, 1, -1)),
  (Fraction(44, 325), (0, -1, 1)),
  (Fraction(8912, 14625), (1, 0, -1)),
  (Fraction(128, 585), (-1, 0, 1))
  ]))

  from matplotlib.backends.backend_pdf import PdfPages

  with PdfPages('result.pdf') as pdf:
    for popularity, data in zip(instances, datas):
      draw_figure(popularity, data)
      pdf.savefig()
      plt.close()

