#include <iostream>
#include <sstream>
#include <vector>
using namespace std;
using integer = long long int;
using pii = pair<integer,integer>;
using vi = vector<integer>;
using vvi = vector<vi>;
using vd = vector<double>;
using vvd = vector<vd>;

int N, R, M, P, S;
vi u, c, util;
vvi run, pref, outcome;

int getSchool(const vi &p, const vi &c)
{
  int i = 0;
  while (i < (int)p.size())
  {
    if (c[p[i]] > 0)
      return p[i];
    i++;
  }
  return -1;
}

// sample and update distribution
// memory O(R), time O(log R)
vi remain;
void remainInit()
{
  int leaf = 1;
  while (leaf < R)
    leaf *= 2;
  remain = vi(leaf*2, 0);
  for (int i=leaf; i<leaf+R; i++)
    remain[i] = N;
  for (int i=leaf-1; i>0; i--)
    remain[i] = remain[2*i] + remain[2*i+1];
}
int remainGet()
{
  int leaf = remain.size() / 2;
  int i = 1, r = rand() % remain[1]--;
  while (i < leaf)
  {
    i *= 2;
    if (r >= remain[i])
      r -= remain[i++];
    remain[i]--;
  }
  return i - leaf;
}

void error(string msg)
{
  cerr << "Error: " << msg << endl;
  exit(1);
}

int main(int argc, char** argv)
{
  R = 1000;
  S = 1000;
  
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
  
  run.resize(R);
  for (int i=0; i<R; i++)
    run[i] = c;
  
  cin.ignore();
  pref.resize(P);
  util.resize(P);
  outcome.resize(P);
  for (int p=0; p<P; p++)
  {
    string line;
    getline(cin, line);
    stringstream in(line);
    int tmp;
    while(in >> tmp)
      pref[p].push_back(tmp);
    util[p] = R * u[pref[p][0]];
    outcome[p] = vi(M, 0);
    outcome[p][pref[p][0]] = R;
  }
  
  // initialize distribution
  srand(P);
  remainInit();
  
  // header
  cout << "score,utility";
  for (int p=0; p<P; p++)
    cout << ",p" << p;
  for (int j=0; j<M; j++)
    cout << ",probaOutcome" << j;
  cout << endl;
  
  // aggregate
  vi equilibrium(P, 0);
  vi probaOutcome(M, 0);
  
  for (int x=1; x<=R*N; x++)
  {
    // compute best move
    pii best(-1, -1);
    for (int p=0; p<(int)pref.size(); p++)
      if (util[p] > best.first)
        best = {util[p], p};
    
    // chose a run to update at random
    int r = remainGet();
    
    // update utility of each move
    for (int p=0; p<(int)pref.size(); p++)
    {
      int j = getSchool(pref[p], run[r]);
      if (j != -1)
      {
        util[p] -= u[j];
        outcome[p][j]--;
      }
    }
    
    // decrease capacity in run r
    int jbest = getSchool(pref[best.second], run[r]);
    if (jbest != -1) run[r][jbest]--;
    
    // update utility of each move
    for (int p=0; p<(int)pref.size(); p++)
    {
      int j = getSchool(pref[p], run[r]);
      if (j != -1)
      {
        util[p] += u[j];
        outcome[p][j]++;
      }
    }
    
    // aggregate data
    equilibrium[best.second]++;
    for (int j=0; j<M; j++)
      probaOutcome[j] += outcome[best.second][j];
    
    // output equilibrium
    if (x % S == 0)
    {
      cerr << "\r" << x / S << "/" << R*N/S << flush;
      cout << 1 - x / (double)(R*N) << "," << best.first / (double)R;
      for (auto p: equilibrium)
        cout << "," << p / (double)S;
      for (auto p: probaOutcome)
        cout << "," << p / (double)R / (double)S;
      cout << endl;
      fill(probaOutcome.begin(), probaOutcome.end(), 0);
      fill(equilibrium.begin(), equilibrium.end(), 0);
    }
  }
  
  cerr << endl;
}
