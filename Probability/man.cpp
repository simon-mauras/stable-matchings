#include "includes.hpp"

class Man
{
  private:
  vector<vector<Answer>> next;
  R getProba(vector<int> pref, const vector<R> &popularity)
  {
    R before(0), proba(1);
    for (auto idWoman : pref)
    {
      before += 1 / popularity[idWoman];
      proba *= (1 / popularity[idWoman]) / before;
    }
    return proba;
  }
  
  public:
  Man(const vector<R> &popularity)
  {
    vector<int> pref;
    next.push_back({});
    for (int i=0; i<(int)popularity.size(); i++)
      if (popularity[i])
        pref.push_back(i);
    
    do // iterate over all preference lists
    {
      // probability of sampling pref
      R proba = getProba(pref, popularity);
      
      // build data structure (trie)
      int act = 0;
      for (int idWoman : pref)
      {
        int j = 0;
        while (j < (int)next[act].size() && idWoman != next[act][j].value) j++;
        if (j == (int)next[act].size())
        {
          next[act].push_back({idWoman, R(0), (int)next.size()});
          next.push_back({});
        }
        next[act][j].proba += proba;
        act = next[act][j].state;
      }
    }
    while (next_permutation(pref.begin(), pref.end()));
    
    // compute transitions
    for (int state=0; state<(int)next.size(); state++)
    {
      R sum(0);
      for (const Answer &ans : next[state])
        sum += ans.proba;
      for (Answer &ans : next[state])
        ans.proba /= sum;
    }
  }
  
  const vector<Answer>& getNextChoice(int state) {
    return next[state];
  }
};
