#include "includes.hpp"

class Woman
{
  private:
  vector<map<int,pair<Answer,Answer>>> answers;
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
  Woman(const vector<R> &popularity)
  {
    vector<int> pref;
    answers.push_back({});
    for (int i=0; i<(int)popularity.size(); i++)
      if (popularity[i])
        pref.push_back(i);
    vector<int> prop(pref);
    
    do // iterate over all preference lists
    {
      R proba = getProba(pref, popularity);
      vector<int> inverse(popularity.size(), -1);
      for (int i=0; i<(int)pref.size(); i++)
        inverse[pref[i]] = i;
      
      do // iterate over all sequences of proposal
      {
        int act = 0;
        int best = pref.size();
        for (int i=0; i<(int)prop.size(); i++)
        {
          bool accepts = false;
          if (inverse[prop[i]] < best)
          {
            best = inverse[prop[i]];
            accepts = true;
          }
          if (!answers[act].count(prop[i]))
            answers[act].insert({prop[i], {{1, R(0), -1}, {0, R(0), -1}}});
          Answer &ans = accepts ? answers[act][prop[i]].first
                                : answers[act][prop[i]].second;
          if (ans.state == -1)
          {
            ans.state = answers.size();
            answers.push_back({});
          }
          ans.proba += proba;
          act = ans.state;
        }
      }
      while (next_permutation(prop.begin(), prop.end()));
    }
    while (next_permutation(pref.begin(), pref.end()));
    
    for (int state=0; state<(int)answers.size(); state++)
    {
      for (auto &ans : answers[state])
      {
        R sum = ans.second.first.proba + ans.second.second.proba;
        ans.second.first.proba /= sum;
        ans.second.second.proba /= sum;
      }
    }
  }
  
  vector<Answer> getAnswer(int state, int idMan) {
    return {answers[state][idMan].first, answers[state][idMan].second};
  }
};
