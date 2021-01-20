#include <iostream>
#include <vector>
#include <functional>
#include <algorithm>
#include <cmath>
#include <random>
using namespace std;

using vi = vector<int>;
using vvi = vector<vi>;

class GaleShapley
{
  private:
  int nbMen, nbWomen;
  vvi pref;     // men's preferences (ranked lists)
  vvi score;    // women's preferences (score)
  vi match[2];  // bipartite matching
  vi prop;      // nb of proposals from each man
  vi minscore;  // minimum score required by each woman
  
  public:
  GaleShapley(vvi m, vvi w)
  : nbMen(m.size()), nbWomen(w.size()),
    pref(m), score(w.size()),
    match({vi(nbMen, -1), vi(nbWomen, -1)}),
    prop(vi(nbMen, 0)), minscore(vi(nbWomen, 0))
  {
    for (int idWoman=0; idWoman<nbWomen; idWoman++)
    {
      score[idWoman] = vi(nbMen, 0);
      for (int i=0; i<(int)w[idWoman].size(); i++)
        score[idWoman][w[idWoman][i]] = w[idWoman].size() - i;
    }
  }
  void nextStable()
  {
    int idMan = 0;
    while (idMan < nbMen)
    {
      int next = idMan + 1;
      if (match[0][idMan] == -1)
      {
        if (prop[idMan] < (int)pref[idMan].size())
        {
          next = idMan;
          int idWoman = pref[idMan][prop[idMan]++];
          if (score[idWoman][idMan] > minscore[idWoman])
          {
            if (match[1][idWoman] != -1)
            {
              next = match[1][idWoman];
              match[0][next] = -1;
            }
            match[0][idMan] = idWoman;
            match[1][idWoman] = idMan;
            minscore[idWoman] = score[idWoman][idMan];
          }
        }
      }
      idMan = next;
    }
  }
  vi getStableHusbands(int g)
  {
    vi res;
    nextStable();
    while (match[1][g] != -1)
    {
      res.push_back(match[1][g]);
      match[0][match[1][g]] = -1;
      match[1][g] = -1;
      nextStable();
    }
    return res;
  }
};

mt19937 generator;
// popularity(i) = 1/lambda^i
// sort by decreasing score(i) = unif^(1/popularity(i))
vi getRandomList(double lambda, int N)
{
  vector<pair<double,int>> t(N);
  uniform_real_distribution<double> distrib(0, 1);
  for (int i=0; i<N; i++)
    t[i] = {log(lambda) * i + log(-log(distrib(generator))), i};
  sort(t.begin(), t.end());
  vi res(N);
  for (int i=0; i<N; i++)
    res[i] = t[i].second;
  return res;
}

int main(int argc, char** argv)
{
  int S = 1;
  int N = 1;
  double lambdaMen = 1, lambdaWomen = 1;
  bool ok = false;
  if (argc == 5)
  {
    S = atoi(argv[1]);
    N = atoi(argv[2]);
    lambdaMen = atof(argv[3]);
    lambdaWomen = atof(argv[4]);
    if (1 <= S)
    if (1 <= N && N <= 1000)
    if (1 <= lambdaMen)
    if (1 <= lambdaWomen)
      ok = true;
  }
  
  if (!ok)
  {
    cerr << "Usage: " << argv[0] << " S N lambdaMen lambdaWomen" << endl;
    cerr << "- lambdaMen >= 1" << endl;
    cerr << "- lambdaWomen >= 1" << endl;
    return 1;
  }
  
  vvi dataCouples(N, vi(N, 0));
  vvi dataHusbands(N, vi(N, 0)), dataHusbandsNb(N, vi(N, 0));
  vvi dataWifes(N, vi(N, 0)), dataWifesNb(N, vi(N, 0));
  
  for (int s=0; s<S; s++)
  {
    if (S == 1)
      cerr << "Generation of preferences..." << endl;
    
    vvi prefMen(N), prefWomen(N);
    for (int i=0; i<N; i++)
      prefMen[i] = getRandomList(lambdaWomen, N);
    for (int i=0; i<N; i++)
      prefWomen[i] = getRandomList(lambdaMen, N);
    
    if (S == 1)
      cerr << "Computing stable husbands..." << endl;
    
    vvi husbands;
    for (int i=0; i<N; i++)
    {
      GaleShapley gs(prefMen, prefWomen);
      husbands.push_back(gs.getStableHusbands(i));
    }
    
    if (S == 1)
      cerr << "Output results" << endl;
    
    vvi wifes(N);
    for (int j=0; j<N; j++)
    {
      vi order(N);
      for (int i=0; i<N; i++)
        order[prefWomen[j][i]] = i;
      dataHusbandsNb[j][husbands[j].size()]++;
      for (auto i : husbands[j])
      {
        dataHusbands[j][order[i]]++;
        wifes[i].push_back(j);
        dataCouples[i][j]++;
      }
    }
    for (int i=0; i<N; i++)
    {
      vi order(N);
      for (int j=0; j<N; j++)
        order[prefMen[i][j]] = j;
      dataWifesNb[i][wifes[i].size()]++;
      for (auto j : wifes[i])
      {
        dataWifes[i][order[j]]++;
      }
    }
  }
  
  auto display = [N,S](const vvi &t) {
    for (int i=0; i<N; i++) {
      for (int j=0; j<N; j++)
        cout << t[i][j] / (double)S << " ";
      cout << endl;
    }
  };
  cout << N << " " << lambdaMen << " " << lambdaWomen << endl;
  display(dataCouples);
  display(dataHusbands);
  display(dataHusbandsNb);
  display(dataWifes);
  display(dataWifesNb);
}
