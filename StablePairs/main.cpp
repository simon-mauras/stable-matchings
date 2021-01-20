#include "algo-n2.cpp"
#include "generate_preferences.cpp"

#include <iostream>
#include <fstream>
#include <vector>
#include <map>
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
  
  vvd popularity(nbMen, vd(nbWomen, 0));
  for (int i=0; i<nbMen; i++)
    for (int j=0; j<nbWomen; j++)
      cin >> popularity[i][j];
  
  // all stable pairs
  vvi data_ALL_couples(nbMen, vi(nbWomen, 0));
  vector<map<int,int>> data_ALL_nbM(nbMen);
  vector<map<int,int>> data_ALL_nbW(nbWomen);
  vector<map<int,int>> data_ALL_deltaM(nbMen);
  vector<map<int,int>> data_ALL_deltaW(nbWomen);
  
  // man optimal stable matching
  vvi data_MOSM_couples(nbMen, vi(nbWomen, 0));
  vector<map<int,int>> data_MOSM_rankM(nbMen);
  vector<map<int,int>> data_MOSM_rankW(nbWomen);
  
  // woman optimal stable matching
  vvi data_WOSM_couples(nbMen, vi(nbWomen, 0));
  vector<map<int,int>> data_WOSM_rankM(nbMen);
  vector<map<int,int>> data_WOSM_rankW(nbWomen);
  
  for (int s=0; s<S; s++)
  {
    if (S > 1)
      cerr << "\r" << s+1 << "/" << S << flush;
    
    if (S == 1)
      cerr << "Generation of preferences..." << endl;
    
    vvi prefMen, prefWomen;
    tie(prefMen, prefWomen) = generateSymetric(generator, popularity);
    
    if (S == 1)
      cerr << "Computing stable husbands..." << endl;
    
    GaleShapley gs(prefMen, prefWomen);
    gs.computeStableHusbands();
    
    if (S == 1)
      cerr << "Output results" << endl;
      
    vvi wifes(nbMen);
    for (int j=0; j<nbWomen; j++)
    {
      data_ALL_nbW[j][gs.husbands[j].size()]++;
      if (!gs.husbands[j].empty())
      {
        vi order(nbMen, -1);
        for (int i=0; i<(int)prefWomen[j].size(); i++)
          order[prefWomen[j][i]] = i;
        
        int mosm = gs.husbands[j].front();
        int wosm = gs.husbands[j].back();
        data_MOSM_couples[mosm][j]++;
        data_WOSM_couples[wosm][j]++;
        data_MOSM_rankW[j][order[mosm]]++;
        data_WOSM_rankW[j][order[wosm]]++;
        data_ALL_deltaW[j][1 + order[mosm] - order[wosm]]++;
        for (auto i : gs.husbands[j])
        {
          data_ALL_couples[i][j]++;
          wifes[i].push_back(j);
        }
      }
    }
    for (int i=0; i<nbMen; i++)
    {
      data_ALL_nbM[i][wifes[i].size()]++;
      if (!wifes[i].empty())
      {
        vi order(nbWomen, -1);
        for (int j=0; j<(int)prefMen[i].size(); j++)
          order[prefMen[i][j]] = j;
        
        sort(wifes[i].begin(), wifes[i].end(), [order](int a, int b) {
          return order[a] < order[b];
        });
        
        int mosm = wifes[i].front();
        int wosm = wifes[i].back();
        data_MOSM_rankM[i][order[mosm]]++;
        data_WOSM_rankM[i][order[wosm]]++;
        data_ALL_deltaM[i][1 + order[wosm] - order[mosm]]++;
      }
    }
  }
  
  if (S > 1)
    cerr << endl;
  
  cout << "{\"nbMen\":" << nbMen << ",\"nbWomen\":" << nbWomen << ",\n";
  cout << "\"popularity\":" << popularity << ",\n";
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
