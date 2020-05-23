#include "includes.hpp"
#include "man.cpp"
#include "woman.cpp"

class DeferredAcceptance
{
  private:
  vector<Man> man;
  vector<Woman> woman;
  vector<int> stateM, stateW, answer;
  void compute(R proba)
  {
    if (proba == R(0)) return;
    
    vector<bool> single(man.size(), true);
    for (auto m : answer)
      if (m != -1)
        single[m] = false;
    
    int idMan = 0;
    vector<Answer> proposals;
    while (idMan < (int)man.size())
    {
      if (single[idMan])
      {
        proposals = man[idMan].getNextChoice(stateM[idMan]);
        if (!proposals.empty()) break;
      }
      idMan++;
    }
    
    // we found a stable matching
    if (proposals.empty())
    {
      result[answer] += proba;
      /*
      cout << "matching ";
      for (auto m : answer)
        cout << "m" << m << " ";
      cout << endl;
      //*/
      return;
    }
    
    // for every possible proposal
    for (Answer prop : proposals)
    {
      int idWoman = prop.value;
      vector<Answer> accept = woman[idWoman].getAnswer(stateW[idWoman], idMan);
      for (Answer ans : accept)
      {
        int oldstateM = stateM[idMan];
        int oldstateW = stateW[idWoman];
        int oldanswer = answer[idWoman];
        
        if (ans.value) // proposal is accepted
        {
          stateM[idMan]   = prop.state;
          stateW[idWoman] = ans.state;
          answer[idWoman] = idMan;
          compute(proba * prop.proba * ans.proba);
        }
        else // proposal is rejected
        {
          stateM[idMan]   = prop.state;
          stateW[idWoman] = ans.state;
          compute(proba * prop.proba * ans.proba);
        }
        
        stateM[idMan]   = oldstateM;
        stateW[idWoman] = oldstateW;
        answer[idWoman] = oldanswer;
      }
    }
  }
  
  public:
  map<vector<int>,R> result;
  DeferredAcceptance(vector<Man> m, vector<Woman> w) : man(m), woman(w),
  stateM(m.size(), 0), stateW(w.size(), 0), answer(w.size(), -1)
  {
    compute(R(1));
  }
  
  void print()
  {
    for (auto match : result)
    {
      for (auto m : match.first)
        cout << m << " ";
      cout << match.second << endl;
    }
  }
};

int main()
{
  int nbMen=0, nbWomen=0;
  cin >> nbMen >> nbWomen;
  
  cerr << "read input" << endl;
  int popularity[nbMen][nbWomen];
  for (int idMan=0; idMan<nbMen; idMan++)
    for (int idWoman=0; idWoman<nbWomen; idWoman++)
      cin >> popularity[idMan][idWoman];
  
  cerr << "init men" << endl;
  vector<Man> man;
  for (int idMan=0; idMan<nbMen; idMan++)
  {
    vector<R> pop;
    for (int idWoman=0; idWoman<nbWomen; idWoman++)
      pop.push_back(R(popularity[idMan][idWoman]));
    man.push_back(pop);
  }
  
  cerr << "init women" << endl;
  vector<Woman> woman;
  for (int idWoman=0; idWoman<nbWomen; idWoman++)
  {
    vector<R> pop;
    for (int idMan=0; idMan<nbMen; idMan++)
      pop.push_back(R(popularity[idMan][idWoman]));
    woman.push_back(pop);
  }
  
  cerr << "deferred acceptance" << endl;
  DeferredAcceptance mosm(man, woman);
  mosm.print();
  
}
