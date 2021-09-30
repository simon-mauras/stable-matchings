#include <bits/stdc++.h>
using namespace std;
using vi = vector<int>;
using vvi = vector<vi>;

int main(int argc, char** argv)
{
  srand(clock());
  assert(argc == 4);
  
  int repeat = atoi(argv[1]);
  int M = atoi(argv[2]);
  int W = atoi(argv[3]);
  
  vvi prefM(M, vi(W)), rankW(W, vi(M));
  for (int m=0; m<M; m++)
  {
    for (int w=0; w<W; w++)
    {
      prefM[m][w] = w;
      rankW[w][m] = m;
    }
  }
  
  vvi data;
  for (int r=0; r<repeat; r++)
  {
    cerr << "\r" << r+1 << "/" << repeat << flush;
    for (int m=0; m<M; m++)
      random_shuffle(prefM[m].begin(), prefM[m].end());
    for (int w=0; w<W; w++)
      random_shuffle(rankW[w].begin(), rankW[w].end());
    
    vi prop(M, 0), answ(W, M);
    for (int day=0; true; day++)
    {
      int nb = 0;
      for (int m=0; m<M; m++)
      if (prop[m] < prefM[m].size())
      {
        int w = prefM[m][prop[m]];
        if (rankW[w][m] < answ[w])
          answ[w] = rankW[w][m];
      }
      for (int m=0; m<M; m++)
      if (prop[m] < prefM[m].size())
      {
        int w = prefM[m][prop[m]];
        if (rankW[w][m] > answ[w])
          prop[m]++, nb++;
      }
      
      if (day >= data.size())
        data.push_back(vi(2,0));
      data[day][0] += nb;
      if (nb == 0)
      {
        data[day][1]++;
        break;
      }
    }
  }
  cerr << endl;
  
  for (int day=0; day<data.size(); day++)
  {
    cout << day+1;
    for (auto x: data[day])
      cout << " " << x;
    cout << endl;
  }
}
