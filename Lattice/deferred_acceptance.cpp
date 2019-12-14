#include <set>
#include <vector>
using namespace std;
using vi = vector<int>;
using vvi = vector<vi>;
using pii = pair<int,int>;
const int infty = 1000000000;

class GaleShapley
{
  private:
  int nbMen, nbWomen;
  const vvi &prefM, &prefW;        // preferences (ranked lists)
  vvi score;                       // women's preferences (score)
  vi lastM, lastW;                 // last stable matching
  
  vector<char> statusW;            // enumerate rotations
  const char FORBIDDEN = 'F';
  const char INSTACK = 'I';
  const char MARRIED = 'M';
  const char SINGLE = 'S';
  vvi label; int phase;
  
  public:
  vector<vector<pii>> rotation;    // graph of rotations
  vector<set<int>> edges; 
  
  GaleShapley(const vvi &m, const vvi &w)
  : nbMen(m.size()), nbWomen(w.size()),
    prefM(m), prefW(w), score(w.size()),
    lastM(nbMen, -1), lastW(nbWomen),
    statusW(nbWomen, SINGLE),
    label(nbMen, vi(nbWomen, 0)),
    rotation(1), edges(1)
  {
    for (int idWoman=0; idWoman<nbWomen; idWoman++)
    {
      lastW[idWoman] = prefW[idWoman].size();
      score[idWoman] = vi(nbMen, prefW[idWoman].size());
      for (int i=0; i<(int)prefW[idWoman].size(); i++)
        score[idWoman][prefW[idWoman][i]] = i;
    }
  }
  
  int nextStable(int idMan)
  {
    int idProp = lastM[idMan];
    while (++idProp < (int)prefM[idMan].size())
    {
      int idWoman = prefM[idMan][idProp];
      if (score[idWoman][idMan] < lastW[idWoman])
      { // idWoman accepts idMan's proposition
        // by default, idWoman is SINGLE
        int result = nbWomen;
        bool push = true, ret = true;
        if (statusW[idWoman] == FORBIDDEN)
        { // this proposition leads to a dead end
          push = false;
          result = -1;
        }
        if (statusW[idWoman] == INSTACK)
        { // we just found a rotation
          if (phase == 2)
          { // in phase 1, no rotation
            rotation.push_back(vector<pii>());
            edges.push_back(set<int>());
          }
          result = idWoman;
        }
        if (statusW[idWoman] == MARRIED)
        { // find a new wife for idNext
          int idNext = prefW[idWoman][lastW[idWoman]];
          statusW[idWoman] = INSTACK;
          result = nextStable(idNext);
          if (result == -1)
          { // this proposition leads to a dead end
            statusW[idWoman] = FORBIDDEN;
            push = false;
          }
          if (result == idWoman)
          { // end of rotation, re-try proposition
            push = false;
            ret = false;
            idProp--;
          }
        }
        if (push)
        { // we change the last matching
          statusW[idWoman] = MARRIED;
          if (phase == 2)
          {
            rotation.back().push_back({idMan, idWoman});
            for (int s=lastM[idMan]; s<idProp; s++)
              edges.back().insert(label[idMan][prefM[idMan][s]]);
          }
          for (int s=score[idWoman][idMan]; s<lastW[idWoman]; s++)
            label[prefW[idWoman][s]][idWoman] = rotation.size() - 1;
          lastW[idWoman] = score[idWoman][idMan];
          lastM[idMan] = idProp;
        }
        if (ret)
          return result;
      }
    }
    // end of list
    if (phase == 1)
    {
      lastM[idMan] = idProp;
      return nbWomen;
    }
    return -1;
  }
  
  void computeSolution()
  {
    // First phase
    phase = 1;
    for (int idMan=0; idMan<nbMen; idMan++)
      nextStable(idMan);

    // Update status
    for (int idWoman=0; idWoman<nbWomen; idWoman++)
      if (statusW[idWoman] == MARRIED)
        rotation.back().push_back({prefW[idWoman][lastW[idWoman]], idWoman});
      else
        statusW[idWoman] = FORBIDDEN;

    // Second phase
    phase = 2;
    for (int idMan=0; idMan<nbMen; idMan++)
      nextStable(idMan);
  }
};


