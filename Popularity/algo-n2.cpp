#include <vector>
#include <algorithm>
#include <cassert>
#include <random>
using namespace std;

using vi = vector<int>;
using vvi = vector<vi>;

const int infty = 1000000000;

class GaleShapley
{
  private:
  int nbMen, nbWomen;
  const vvi &prefM, &prefW;   // preferences (ranked lists)
  vvi score;                  // women's preferences (score)
  vi lastM, lastW;            // previous partner
  vi threshold, mark;         // enumerate stable pairs
  
  public:
  vi matchM, matchW;          // bipartite matching
  vvi husbands;               // stable husbands of each woman
  
  GaleShapley(const vvi &m, const vvi &w)
  : nbMen(m.size()), nbWomen(w.size()),
    prefM(m), prefW(w), score(w.size()),
    lastM(vi(nbMen, 0)), lastW(vi(nbWomen, 0)),
    threshold(nbWomen, infty), mark(),
    matchM(vi(nbMen, -1)), matchW(vi(nbWomen, -1)),
    husbands(nbWomen)
  {
    for (int idWoman=0; idWoman<nbWomen; idWoman++)
    {
      score[idWoman] = vi(nbMen, 0);
      for (int i=0; i<(int)prefW[idWoman].size(); i++)
        score[idWoman][prefW[idWoman][i]] = prefW[idWoman].size() - i;
    }
  }
  void nextStable(int idMan)
  {
    while (idMan != -1)
    {
      int next = -1;
      assert(matchM[idMan] == -1); // idMan is single
      if (lastM[idMan] < (int)prefM[idMan].size())
      { // idMan has a proposition left
        next = idMan;
        int idWoman = prefM[idMan][lastM[idMan]++];
        if (score[idWoman][idMan] > threshold[idWoman])
        { // We detected a p-cycle.
          husbands[idWoman].push_back(idMan);
          threshold[idWoman] = score[idWoman][idMan];
          while (mark.back() != idWoman)
          { // Unmark all women from p-cycle, except idWoman.
            husbands[mark.back()].push_back(matchW[mark.back()]);
            threshold[mark.back()] = infty;
            mark.pop_back();
          }
        }
        if (score[idWoman][idMan] > lastW[idWoman])
        { // accept proposition from idMan to idWoman
          if (threshold[idWoman] == infty)
          { // unmarked -> marked 
            threshold[idWoman] = lastW[idWoman];
            mark.push_back(idWoman);
          }
          else
          { // marked -> unmarked 
            threshold[mark.back()] = infty;
            mark.pop_back();
          }
          next = matchW[idWoman];
          matchM[idMan] = idWoman;
          matchW[idWoman] = idMan;
          lastW[idWoman] = score[idWoman][idMan];
          if (next != -1)
            matchM[next] = -1;
        }
      }
      idMan = next;
    }
  }
  void computeSolution()
  {
    for (int idMan=0; idMan<nbMen; idMan++)
      if (matchM[idMan] == -1)
        nextStable(idMan);
  }
  void computeStableHusbands()
  {
    GaleShapley reverse(prefW, prefM);
    reverse.computeSolution();
    computeSolution();
    fill(threshold.begin(), threshold.end(), infty);
    mark.clear();
    for (int idWoman=0; idWoman<nbWomen; idWoman++)
    {
      husbands[idWoman].clear();
      if (matchW[idWoman] != -1)
        husbands[idWoman].push_back(matchW[idWoman]);
    }
    int idMan = 0;
    while (idMan < nbMen)
    {
      int next = idMan + 1;
      if (matchM[idMan] != reverse.matchW[idMan])
      {
        int idWoman = matchM[idMan];
        matchW[idWoman] = -1;
        matchM[idMan] = -1;
        mark.push_back(idWoman);
        threshold[idWoman] = lastW[idWoman];
        nextStable(idMan);
        assert(mark.empty());
        next = idMan;
      }
      idMan = next;
    }
  }
};


