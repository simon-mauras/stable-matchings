#include <iostream>
#include <sstream>
#include <vector>
#include <map>
using namespace std;
using pii = pair<int,int>;
using vi = vector<int>;
using vvi = vector<vi>;
using vd = vector<double>;
using vvd = vector<vd>;

int N, M, R, P, S;
vi u, c;
vvi run, pref;

int getSchool(const vi &p, const vi &capa)
{
  int i = 0;
  while (i < (int)p.size())
  {
    if (capa[p[i]] > 0)
      return p[i];
    i++;
  }
  return -1;
}

int remainStudents(const vi &capa)
{
  int arrived = N - capa[M];
  for (int j=0; j<M; j++)
    arrived += c[j] - capa[j];
  return N - arrived;
}

vvi capacities;
void build_capa(vi capa, int i, int remain)
{
  if (i == M+1)
  {
    capacities.push_back(capa);
    return;
  }
  
  int maxi = (i < M ? c[i] : N);
  for (int x=0; x<=min(remain, maxi); x++)
  {
    capa[i] = maxi - x;
    build_capa(capa, i+1, remain-x);
  }
}


void error(string msg)
{
  cerr << "Error: " << msg << endl;
  exit(1);
}

int main(int argc, char** argv)
{
  R = 10000, S = 100;
  
  // parse command line
  if (argc % 2 == 0) error("number of parameter should be even.");
  for (int i=1; i<argc; i++)
  {
    if (string(argv[i]) == "-R")
      R = atoi(argv[++i]);
    else if (string(argv[i]) == "-S")
      S = atoi(argv[++i]);
    else
      error("parameter \"" + string(argv[i]) + "\" unknown.");
  }
  
  cin >> N >> M >> P;
  N--; // consider the other students
  
  u.resize(M);
  c.resize(M);
  for (int j=0; j<M; j++)
    cin >> u[j] >> c[j];
  
  cin.ignore();
  pref.resize(P);
  for (int p=0; p<P; p++)
  {
    string line;
    getline(cin, line);
    stringstream in(line);
    int tmp;
    while(in >> tmp)
      pref[p].push_back(tmp);
  }
  
  build_capa(vi(M+1, 0), 0, N);
  map<vi,int> id_of_capa;
  for (int i=0; i<(int)capacities.size(); i++)
  {
    id_of_capa[capacities[i]] = i; 
    /*for (auto x : capacities[i])
      cerr << x << " ";
    cerr << endl;*/
  }
  vd distribution(capacities.size(), 0);
  distribution[0] = 1;
  
  // debug
  cerr << "Number of feasible vectors = " << capacities.size() << endl;
  
  // header
  cout << "score,utility";
  for (int p=0; p<P; p++)
    cout << ",p" << p;
  for (int j=0; j<M; j++)
    cout << ",probaOutcome" << j;
  cout << endl;
  
  // aggregate
  vd equilibrium(P, 0);
  vd probaOutcome(M, 0);
  
  for (int x=1; x<=R; x++)
  {
    // compute best move
    vector<int> actions;
    double best = -1;
    for (int p=0; p<(int)pref.size(); p++)
    {
      double util = 0;
      for (int i=0; i<(int)capacities.size(); i++)
      {
        vi capa = capacities[i];
        int j = getSchool(pref[p], capa);
        if (j != -1) util += u[j] * distribution[i];
      }
      
      if (util > best)
      {
        best = util;
        actions.clear();
      }
      if (util == best && actions.empty())
        actions.push_back(p);
    }
    //if (x < 10)
    // cerr << actions.size() << endl;
    
    double pr = 1 / (double)actions.size(); 
    
    // play best response
    for (auto p : actions)
      equilibrium[p] += pr;
    
    vd distr(capacities.size(), 0);
    for (int i=0; i<(int)capacities.size(); i++)
    {
      // compute the proba of someone arriving
      double density = remainStudents(capacities[i]) / (double)(R+1-x);
      
      for (auto p : actions)
      {
        // current capacities
        vi capa = capacities[i];
        
        // next capacity
        int j = getSchool(pref[p], capa);
        if (j != -1)
        {
          capa[j]--;
          probaOutcome[j] += distribution[i] * pr;
        }
        else
          capa.back()--;
        
        // update distribution
        int n = id_of_capa[capa];
        distr[n] += pr * distribution[i] * density;
        distr[i] += pr * distribution[i] * (1 - density);
      }
    }
    distribution = distr;
    
    // output equilibrium
    if (x % S == 0)
    {
      cerr << "\r" << x / S << "/" << R / S << flush;
      cout << 1 - x / (double)R << "," << best;
      for (auto p: equilibrium)
        cout << "," << p / (double)S;
      for (auto p: probaOutcome)
        cout << "," << p / (double)S;
      cout << endl;
      fill(probaOutcome.begin(), probaOutcome.end(), 0);
      fill(equilibrium.begin(), equilibrium.end(), 0);
    }
  }
  
  cerr << endl;
}
