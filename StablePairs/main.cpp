#include "algo-n2.cpp"
#include "generate_preferences.cpp"

#include <iostream>
#include <fstream>
#include <vector>
#include <map>
#include <set>
#include <functional>
#include <algorithm>
#include <cassert>
#include <cmath>
#include <random>
using namespace std;
using vi = vector<int>;
using vd = vector<double>;
using vvi = vector<vi>;
using vvd = vector<vd>;
#define UNIQUE(t) t.resize(distance(t.begin(), unique(t.begin(), t.end())))

template<typename T>
ostream& operator<<(ostream& out, const vector<T> &t) {
  out << "[";
  for (auto it=t.begin(); it!=t.end(); it++) {
    if (it != t.begin()) out << ",";
    out << *it;
  }
  return out << "]";
}

template<typename S, typename T>
ostream& operator<<(ostream& out, const map<S, T> &t) {
  out << "{";
  for (auto it=t.begin(); it!=t.end(); it++) {
    if (it != t.begin()) out << ",";
    out << "\"" << it->first << "\":" << it->second;
  }
  return out << "}";
}

int main(int argc, char** argv)
{
  mt19937 generator;
  
  int S = 1, nbMen = 1, nbWomen = 1;
  bool ok = false;
  if (argc == 4)
  {
    S = atoi(argv[1]);
    nbMen = atoi(argv[2]);
    nbWomen = atof(argv[3]);
    if (1 <= S)
    if (1 <= nbMen && nbMen <= 10000)
    if (1 <= nbWomen && nbWomen <= 10000)
      ok = true;
  }
  
  if (!ok)
  {
    cerr << "Usage: " << argv[0] << " S nbMen nbWomen" << endl;
    return 1;
  }
  
  cerr << "running simulations..." << endl;
  
  // read input
  vi multM(nbMen, 0), multW(nbWomen, 0);
  for (int i=0; i<nbMen; i++)
    cin >> multM[i];
  for (int j=0; j<nbWomen; j++)
    cin >> multW[j];
  vvd popularity(nbMen, vd(nbWomen, 0));
  for (int i=0; i<nbMen; i++)
    for (int j=0; j<nbWomen; j++)
      cin >> popularity[i][j];
  
  // multiplicities
  vi cumulM = multM, cumulW = multW;
  for (int i=1; i<nbMen; i++)
    cumulM[i] += cumulM[i-1];
  for (int j=1; j<nbWomen; j++)
    cumulW[j] += cumulW[j-1];
  auto getIdM = [&cumulM](int m) {
    auto it = upper_bound(cumulM.begin(), cumulM.end(), m);
    return distance(cumulM.begin(), it);
  };
  auto getIdW = [&cumulW](int w) {
    auto it = upper_bound(cumulW.begin(), cumulW.end(), w);
    return distance(cumulW.begin(), it);
  };
  
  // all stable pairs
  vvi data_ALL_couples(cumulM.back(), vi(cumulW.back(), 0));
  vector<map<int,int>> data_ALL_nbM(cumulM.back());
  vector<map<int,int>> data_ALL_nbW(cumulW.back());
  vector<map<int,int>> data_ALL_deltaM(cumulM.back());
  vector<map<int,int>> data_ALL_deltaW(cumulW.back());
  
  // man optimal stable matching
  vvi data_MOSM_couples(cumulM.back(), vi(cumulW.back(), 0));
  vector<map<int,int>> data_MOSM_rankM(cumulM.back());
  vector<map<int,int>> data_MOSM_rankW(cumulW.back());
  
  // woman optimal stable matching
  vvi data_WOSM_couples(cumulM.back(), vi(cumulW.back(), 0));
  vector<map<int,int>> data_WOSM_rankM(cumulM.back());
  vector<map<int,int>> data_WOSM_rankW(cumulW.back());
  
  for (int s=0; s<S; s++)
  {
    if (S > 1)
      cerr << "\r" << s+1 << "/" << S << flush;
    
    if (S == 1)
      cerr << "Generation of preferences..." << endl;
    
    vvi prefMen, prefWomen;
    tie(prefMen, prefWomen) =
      generateSymetric(generator, popularity);
    
    // multiplicities
    vvi prefMenMult, prefWomenMult;
    for (int i=0; i<nbMen; i++)
    {
      vi pref;
      for (auto w: prefMen[i])
        for (int j=cumulW[w]-multW[w]; j<cumulW[w]; j++)
          pref.push_back(j);
      for (int r=0; r<multM[i]; r++)
        prefMenMult.push_back(pref);
    }
    for (int j=0; j<nbWomen; j++)
    {
      vi pref;
      for (auto m: prefWomen[j])
        for (int i=cumulM[m]-multM[m]; i<cumulM[m]; i++)
          pref.push_back(i);
      for (int r=0; r<multW[j]; r++)
        prefWomenMult.push_back(pref);
    }
    
    if (S == 1)
      cerr << "Computing stable husbands..." << endl;
    
    GaleShapley gs(prefMenMult, prefWomenMult);
    gs.computeStableHusbands();
    
    if (S == 1)
      cerr << "Output results" << endl;
    
    vvi wifes(cumulM.back());
    for (int j=0; j<cumulW.back(); j++)
    {
      set<int> types;
      for (int i: gs.husbands[j])
        types.insert(getIdM(i));
      data_ALL_nbW[j][types.size()]++;
      if (!gs.husbands[j].empty())
      {
        vi order(nbMen, -1);
        int w = getIdW(j);
        for (int r=0; r<(int)prefWomen[w].size(); r++)
          order[prefWomen[w][r]] = r;
        
        int mosm = gs.husbands[j].front();
        int wosm = gs.husbands[j].back();
        int mosm_rank = order[getIdM(mosm)];
        int wosm_rank = order[getIdM(wosm)];
        data_MOSM_couples[mosm][j]++;
        data_WOSM_couples[wosm][j]++;
        data_MOSM_rankW[j][mosm_rank]++;
        data_WOSM_rankW[j][wosm_rank]++;
        data_ALL_deltaW[j][1 + mosm_rank - wosm_rank]++;
        for (int i:gs.husbands[j])
        {
          data_ALL_couples[i][j]++;
          wifes[i].push_back(j);
        }
      }
    }
    for (int i=0; i<cumulM.back(); i++)
    {
      set<int> types;
      for (int j: wifes[i])
        types.insert(getIdW(j));
      data_ALL_nbM[i][types.size()]++;
      if (!wifes[i].empty())
      {
        vi order(nbWomen, -1);
        int m = getIdM(i);
        for (int r=0; r<(int)prefMen[m].size(); r++)
          order[prefMen[m][r]] = r;
        
        sort(wifes[i].begin(), wifes[i].end(), [&order,&getIdW](int a, int b) {
          int i = getIdW(a), j = getIdW(b);
          return i != j ? order[i] < order[j] : a < b;
        });
        
        int mosm = wifes[i].front();
        int wosm = wifes[i].back();
        int mosm_rank = order[getIdW(mosm)];
        int wosm_rank = order[getIdW(wosm)];
        data_MOSM_rankM[i][mosm_rank]++;
        data_WOSM_rankM[i][wosm_rank]++;
        data_ALL_deltaM[i][1 + wosm_rank - mosm_rank]++;
      }
    }
  }
  
  if (S > 1)
    cerr << endl;
  
  cout << "{\"nbMen\":" << nbMen << ",\"nbWomen\":" << nbWomen << ",\n";
  cout << "\"popularity\":" << popularity << ",\n";
  cout << "\"multM\":" << multM << ",\n";
  cout << "\"multW\":" << multW << ",\n";
  cout << "\"ALL_couples\":" << data_ALL_couples << ",\n";
  cout << "\"ALL_nbM\":" << data_ALL_nbM << ",\n";
  cout << "\"ALL_nbW\":" << data_ALL_nbW << ",\n";
  cout << "\"ALL_deltaM\":" << data_ALL_deltaM << ",\n";
  cout << "\"ALL_deltaW\":" << data_ALL_deltaW << ",\n";
  cout << "\"MOSM_couples\":" << data_MOSM_couples << ",\n";
  cout << "\"MOSM_rankM\":" << data_MOSM_rankM << ",\n";
  cout << "\"MOSM_rankW\":" << data_MOSM_rankW << ",\n";
  cout << "\"WOSM_couples\":" << data_WOSM_couples << ",\n";
  cout << "\"WOSM_rankM\":" << data_WOSM_rankM << ",\n";
  cout << "\"WOSM_rankW\":" << data_WOSM_rankW << "}" << endl;
}
