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
pair<vvi,vvi> generateSymetric(mt19937 &generator, vvd popularity)
{
  uniform_real_distribution<double> uniform(0, 1);
  
  int nbMen = popularity.size();
  int nbWomen = popularity[0].size();
  
  vvi prefMen(nbMen), prefWomen(nbWomen);
  for (int i=0; i<nbMen; i++)
  {
    vector<pair<double,int>> t;
    for (int j=0; j<nbWomen; j++)
      if (popularity[i][j] > 0)
        t.push_back({log(-log(uniform(generator))) - log(popularity[i][j]), j});
    sort(t.begin(), t.end());
    for (int j=0; j<(int)t.size(); j++)
      prefMen[i].push_back(t[j].second);
  }
  for (int j=0; j<nbWomen; j++)
  {
    vector<pair<double,int>> t;
    for (int i=0; i<nbMen; i++)
      if (popularity[i][j] > 0)
        t.push_back({log(-log(uniform(generator))) - log(popularity[i][j]), i});
    sort(t.begin(), t.end());
    for (int i=0; i<(int)t.size(); i++)
      prefWomen[j].push_back(t[i].second);
  }
  
  return {prefMen, prefWomen};
}
