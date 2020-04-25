#include <vector>
#include <random>
#include <cmath>
using namespace std;
using vi = vector<int>;
using vvi = vector<vi>;


pair<vvi,vvi> generateExample()
{
  vvi exampleMen =
    {{4, 6, 0, 1, 5, 7, 3, 2},
     {1, 2, 6, 4, 3, 0, 7, 5},
     {7, 4, 0, 3, 5, 1, 2, 6},
     {2, 1, 6, 3, 0, 5, 7, 4},
     {6, 1, 4, 0, 2, 5, 7, 3},
     {0, 5, 6, 4, 7, 3, 1, 2},
     {1, 4, 6, 5, 2, 3, 7, 0},
     {2, 7, 3, 4, 6, 1, 5, 0}};
  vvi exampleWomen =
    {{4, 2, 6, 5, 0, 1, 7, 3},
     {7, 5, 2, 4, 6, 1, 0, 3},
     {0, 4, 5, 1, 3, 7, 6, 2},
     {7, 6, 2, 1, 3, 0, 4, 5},
     {5, 3, 6, 2, 7, 0, 1, 4},
     {1, 7, 4, 2, 3, 5, 6, 0},
     {6, 4, 1, 0, 7, 5, 3, 2},
     {6, 3, 0, 4, 1, 2, 5, 7}}; 
  return {exampleMen, exampleWomen};
}

pair<vvi,vvi> generateBounded()
{
  vvi exampleMen =
    {{0, 1, 3, 2},
     {2},
     {1, 0, 4},
     {2, 3},
     {3, 4, 1},
     {2},
     {4, 3, 0},
     {2, 1}};
  vvi exampleWomen =
    {{3, 6, 2, 1, 0},
     {4, 5, 0, 2},
     {2, 0, 3, 7, 1, 4, 6, 5},
     {3, 0, 6, 4},
     {2, 4, 6}}; 
  return {exampleMen, exampleWomen};
}

// popularity(i) = lambda^i with 
// score(i) = unif^(1/popularity(i))
// sort by decreasing score <=> sort by increasing log(-log(score))
vi generateGeometric(mt19937 &generator, int N, double lambda)
{
  assert(0 < lambda && lambda <= 1);
  vector<pair<double,int>> t(N);
  uniform_real_distribution<double> distrib(0, 1);
  for (int i=0; i<N; i++)
    t[i] = {log(-log(distrib(generator))) - i * log(lambda), i};
  sort(t.begin(), t.end());
  vector<int> res(N);
  for (int i=0; i<N; i++)
    res[i] = t[i].second;
  return res;
}

pair<vvi,vvi> generateCycle(int N)
{
  vvi prefMen(N), prefWomen(N);
  for (int i=0; i<N; i++)
  {
    for (int j=0; j<N; j++)
      prefMen[i].push_back((i+j) % N);
    for (int j=0; j<N; j++)
      prefWomen[i].push_back((i+j+1) % N);
  }
  return {prefMen, prefWomen};
}

pair<vvi,vvi> generateCycleRand(mt19937 &generator, int N)
{
  vvi prefMen(N), prefWomen(N);
  uniform_int_distribution<int> distrib(0, N-1);
  for (int i=0; i<N; i++)
  {
    prefMen[i] = vi(N);
    prefWomen[i] = vi(N);
    prefMen[i][0] = distrib(generator);
    prefWomen[i][0] = distrib(generator);
    for (int j=1; j<N; j++)
      prefMen[i][j] = (prefMen[i][j-1]+1) % N;
    for (int j=1; j<N; j++)
      prefWomen[i][j] = (prefWomen[i][j-1]+1) % N;
  }
  return {prefMen, prefWomen};
}

pair<vvi,vvi> generateWorstCase(int lg)
{
  int N = 1 << lg;
  vvi prefMen(N, vi(N)), prefWomen(N, vi(N));
  for (int i=0; i<N; i++)
  {
    for (int j=0; j<N; j++)
      prefMen[i][j] = j;
    for (int l=0; l<lg; l++)
      if (1 & (i >> l))
        for (int j=0; j<(1<<(lg-l-1)); j++)
          for (int k=0; k<(1<<l); k++)
            swap(prefMen[i][k+(2*j)*(1<<l)], prefMen[i][k+(2*j+1)*(1<<l)]);
    for (int j=0; j<N; j++)
      prefWomen[prefMen[i][j]][N-1-j] = i;
  }
  return {prefMen, prefWomen};
}

pair<vvi,vvi> generateTranspositions(int N)
{
  vvi prefMen(N, vi(N)), prefWomen(N, vi(N));
  for (int i=0; i<N; i++)
    for (int j=0; j<N; j++)
      prefMen[i][j] = prefWomen[i][j] = j;
  for (int i=0; i+1<N; i+=2)
  {
    swap(prefMen[i+1][i], prefMen[i+1][i+1]);
    swap(prefWomen[i][i], prefWomen[i][i+1]);
  }
  return {prefMen, prefWomen};
}
pair<vvi, vvi> generateRotationPerfect(int N)
{
  assert(N == 5);
  vvi prefMen =
    {{0, 2, 4, 3, 1},
     {1, 3, 2, 0, 4},
     {2, 3, 4, 1, 0},
     {3, 1, 4, 0, 2},
     {4, 2, 0, 1, 3}};
  vvi prefWomen =
    {{2, 4, 3, 1, 0},
     {0, 4, 2, 3, 1},
     {3, 4, 0, 1, 2},
     {4, 0, 2, 1, 3},
     {1, 3, 2, 0, 4}}; 
  return {prefMen, prefWomen};
}
