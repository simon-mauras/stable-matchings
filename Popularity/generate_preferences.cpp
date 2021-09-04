#include <random>
#include <vector>
using namespace std;
using vi = vector<int>;
using vd = vector<double>;
using vvi = vector<vi>;
using vvd = vector<vd>;

// score = unif^(1/popularity)
// log(-log(score)) = log(-log(unif)) - log(popularity)
// sort by decreasing score <=> sort by increasing log(-log(score))
vvi generatePreferences(mt19937 &generator, vvd logpop)
{
  uniform_real_distribution<double> uniform(0, 1);
  
  int nbMen = logpop.size();
  int nbWomen = logpop[0].size();
  
  vvi prefMen(nbMen);
  for (int i=0; i<nbMen; i++)
  {
    vector<pair<double,int>> t;
    for (int j=0; j<nbWomen; j++)
      //if (logpop[i][j] >= 0)
        t.push_back({log(-log(uniform(generator))) - logpop[i][j], j});
    sort(t.begin(), t.end());
    for (int j=0; j<(int)t.size(); j++)
      prefMen[i].push_back(t[j].second);
  }
  
  return prefMen;
}
