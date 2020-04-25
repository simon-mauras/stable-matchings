#include <ostream>
#include <cassert>
#include <vector>
#include <queue>
#include <map>
using namespace std;
using vb = vector<bool>;
using vi = vector<int>;
using vvi = vector<vi>;
using pii = pair<int,int>;

class Matching;
class Visualization
{
  public:
  const int nbMen, nbWomen;
  const vector<string> &nameMen, &nameWomen;
  const vvi &prefMen, &prefWomen;
  vvi scoreMen, scoreWomen;
  
  vector<vector<pii>> rotationNodes;     // graph of rotations
  vvi edges, redges;
  
  vector<Matching> matchingNodes;        // graph of matchings
  vvi matchingEdges, matchingClosure;
  
  Visualization(const vector<string> &nameM,
                const vector<string> &nameW, 
                const vvi &prefM, const vvi &prefW,
                const vector<vector<pii>> &rot,
                vector<set<int>> edg)
  : nbMen(prefM.size()), nbWomen(prefW.size()),
    nameMen(nameM), nameWomen(nameW),
    prefMen(prefM), prefWomen(prefW),
    scoreMen(nbMen, vi(nbWomen,-1)),
    scoreWomen(nbWomen, vi(nbMen,-1)),
    rotationNodes(rot)
  {
    for (int idMan=0; idMan<nbMen; idMan++)
      for (int i=0; i<(int)prefMen[idMan].size(); i++)
        scoreMen[idMan][prefMen[idMan][i]] = i;
    
    for (int idWoman=0; idWoman<nbWomen; idWoman++)
      for (int i=0; i<(int)prefWomen[idWoman].size(); i++)
        scoreWomen[idWoman][prefWomen[idWoman][i]] = i;
    
    int R = rotationNodes.size();
    edges.resize(R);
    redges.resize(R);
    vector<vb> closure(R, vb(R, false));
    for (int i=0; i<R; i++)
    {
      closure[i][i] = true;
      for (auto it=edg[i].rbegin(); it!=edg[i].rend(); it++)
      {
        if (!closure[i][*it])
        {
          edges[i].push_back(*it);
          redges[*it].push_back(i);
          for (int j=0; j<R; j++)
            closure[i][j] = closure[i][j] | closure[*it][j];
        }
      }
    }
  }
  
  void enumerate();
  void print_data(ostream &&out);
  void print_rotations(ostream &&out);
  void print_matchings(ostream &&out);
  void print_preferences(ostream &&out);
};

struct Matching
{
  const Visualization &vis;
  int sumranks;
  vb downset;
  vi lastM;
  Matching (const Visualization &v) : vis(v)
  {
    sumranks = 0;
    lastM = vi(vis.nbMen, -1);
    downset = vb(vis.rotationNodes.size(), false);
    eliminate(0);
  }
  bool isExposed(int r) const
  { // return true iff r is exposed
    if (downset[r]) return false;
    for (auto e : vis.edges[r])
      if (!downset[e])
        return false;
    return true;
  }
  void eliminate(int r)
  {
    if (downset[r])
    { // reverse elimination
      for (auto e : vis.redges[r])
        if (downset[e])
          eliminate(e);
      downset[r] = false;
      pii prev = vis.rotationNodes[r].back();
      for (pii act : vis.rotationNodes[r])
      {
        pii p = {prev.first, act.second};
        sumranks += vis.scoreMen[p.first][p.second] - lastM[p.first];
        lastM[p.first] = vis.scoreMen[p.first][p.second];
        prev = act;
      }
    }
    else
    { // classical elimination
      for (auto e : vis.edges[r])
        if (!downset[e])
          eliminate(e);
      downset[r] = true;
      for (auto p : vis.rotationNodes[r])
      {
        sumranks += vis.scoreMen[p.first][p.second] - lastM[p.first];
        lastM[p.first] = vis.scoreMen[p.first][p.second];
      }
    }
  }
  bool operator<(const Matching &other) const
  {
    if (sumranks != other.sumranks)
      return sumranks < other.sumranks;
    return downset < other.downset;
  }
  void print()
  {
    cerr << sumranks << endl;
    for (auto x : downset)
      cerr << x << " ";
    cerr << endl;
  }
};


// Complexity: nbMatching * nbRotations ^ 2
void Visualization::enumerate()
{
  int nbRotations = rotationNodes.size();
  Matching start(*this); // default is man-optimal
  map<Matching, int> seen;
  seen[start] = -1;
  queue<Matching> bfs;
  bfs.push(start);
  while (!bfs.empty())
  {
    Matching act = bfs.front();
    bfs.pop();
    for (int idRotation=1; idRotation<nbRotations; idRotation++)
    {
      if (act.isExposed(idRotation))
      {
        Matching next = act;
        next.eliminate(idRotation);
        if (!seen.count(next))
        {
          seen[next] = -1;
          bfs.push(next);
        }
      }
    }
  }
  for (auto &m : seen)
  {
    m.second = matchingNodes.size();
    matchingNodes.push_back(m.first);
  }
  int nbMatchings = matchingNodes.size();
  matchingEdges.resize(nbMatchings);
  matchingClosure.resize(nbMatchings);
  for (int idMatching=0; idMatching<nbMatchings; idMatching++)
  {
    matchingClosure[idMatching] = vi(nbRotations, 0);
    const Matching &act = matchingNodes[idMatching];
    for (int idRotation=1; idRotation<nbRotations; idRotation++)
    {
      Matching next = act;
      next.eliminate(idRotation);
      int idNext = seen[next];
      matchingClosure[idMatching][idRotation] = idNext;
      if (act.isExposed(idRotation))
        matchingEdges[idMatching].push_back(idNext);
    }
  }
  
  cerr << "Nb stable matchings = " << matchingNodes.size() << endl;
}

void Visualization::print_data(ostream &&out)
{
  int nbMatchings = matchingNodes.size();
  int nbRotations = rotationNodes.size();
  out << "var nbMen = " << nbMen << ";" << endl;
  out << "var nbWomen = " << nbWomen << ";" << endl;
  out << "var nbMatchings = " << nbMatchings << ";" << endl;
  out << "var nbRotations = " << nbRotations << ";" << endl;
  
  out << "var downset = [\n";
  for (int idMatching=0; idMatching<nbMatchings; idMatching++)
  {
    if (idMatching > 0)
      out << "],\n";
    out << "[";
    for (int idRotation=0; idRotation<nbRotations; idRotation++)
    {
      if (idRotation > 0)
        out << ",";
      out << matchingNodes[idMatching].downset[idRotation];
    }
  }
  out << "]\n];" << endl;
  
  out << "var transition = [\n";
  for (int idMatching=0; idMatching<nbMatchings; idMatching++)
  {
    if (idMatching > 0)
      out << "],\n";
    out << "[";
    for (int idRotation=0; idRotation<nbRotations; idRotation++)
    {
      if (idRotation > 0)
        out << ",";
      out << matchingClosure[idMatching][idRotation];
    }
  }
  out << "]\n];" << endl;
  
  out << "var prefM = [\n";
  for (int idMatching=0; idMatching<nbMatchings; idMatching++)
  {
    if (idMatching > 0)
      out << "],\n";
    out << "[";
    for (int idMan=0; idMan<nbMen; idMan++)
    {
      if (idMan > 0)
        out << ",";
      out << matchingNodes[idMatching].lastM[idMan];
    }
  }
  out << "]\n];" << endl;
  
  out << "var prefW = [\n";
  for (int idMatching=0; idMatching<nbMatchings; idMatching++)
  {
    vi lastW(nbWomen, nbMen);
    for (int idMan=0; idMan<nbMen; idMan++)
    {
      int idProp = matchingNodes[idMatching].lastM[idMan];
      if (idProp >= 0)
      {
        int idWoman = prefMen[idMan][idProp];
        lastW[idWoman] = scoreWomen[idWoman][idMan];
      }
    }
    if (idMatching > 0)
      out << "],\n";
    out << "[";
    for (int idWoman=0; idWoman<nbWomen; idWoman++)
    {
      if (idWoman > 0)
        out << ",";
      out << lastW[idWoman];
    }
  }
  out << "]\n];" << endl;
  
  vvi couples(nbMen, vi(nbWomen, -1));
  for (int idRotation=0; idRotation<nbRotations; idRotation++)
    for (pii c : rotationNodes[idRotation])
      couples[c.first][c.second] = idRotation;
  
  out << "var stableM = [\n";
  for (int idMan=0; idMan<nbMen; idMan++)
  {
    if (idMan > 0)
      out << "],\n";
    out << "[";
    for (int idProp=0; idProp<nbWomen; idProp++)
    {
      if (idProp > 0)
        out << ",";
      int idRotation = -1;
      if (idProp < (int)prefMen[idMan].size())
        idRotation = couples[idMan][prefMen[idMan][idProp]];
      out << idRotation;
    }
  }
  out << "]\n];" << endl;
  
  out << "var stableW = [\n";
  for (int idWoman=0; idWoman<nbWomen; idWoman++)
  {
    if (idWoman > 0)
      out << "],\n";
    out << "[";
    for (int idProp=0; idProp<nbMen; idProp++)
    {
      if (idProp > 0)
        out << ",";
      int idRotation = -1;
      if (idProp < (int)prefWomen[idWoman].size())
        idRotation = couples[prefWomen[idWoman][idProp]][idWoman];
      out << idRotation;
    }
  }
  out << "]\n];" << endl;
}

void Visualization::print_rotations(ostream &&out)
{
  int nbRotations = rotationNodes.size();
  out << "digraph rotations {" << endl;
  for (int idRotation=0; idRotation<nbRotations; idRotation++)
  {
    out << idRotation << "[id=\"r" << idRotation;
    out << "\",style=\"filled\",label=\"";
    if (idRotation > 0)
      for (auto r : rotationNodes[idRotation])
        out << "(" << nameMen[r.first] << "," << nameWomen[r.second] << ")";
    out << "\"];" << endl;
    for (auto e : redges[idRotation])
      out << idRotation << " -> " << e << ";" << endl;
  }
  out << "}" << endl;
}

void Visualization::print_matchings(ostream &&out)
{
  int nbMatchings = matchingNodes.size();
  out << "digraph matchings {" << endl;
  for (int idMatching=0; idMatching<nbMatchings; idMatching++)
  {
    out << idMatching << "[label=\"\",style=\"filled\",";
    out << "id=\"m" << idMatching << "\"]" << endl;
    for (auto e : matchingEdges[idMatching])
      out << idMatching << " -> " << e << ";" << endl;
  }
  out << "}" << endl;
}

void Visualization::print_preferences(ostream &&out)
{
  out << "<!DOCTYPE html>\n<html>\n<head>\n<style>" << endl;
  out << "table { width:100%;";
  out << "border: 1px solid black; border-collapse:collapse }";
  out << "html, body { width:100%; height:100%; margin:0; }" << endl;
  out << "td, th { text-align: center; font-size:20pt; }" << endl;
  out << "th { background-color:black; color:white; }" << endl;
  out << "</style>\n</head>\n<body>\n<table>\n<tr>\n" << endl;
    for (int idMan=0; idMan<nbMen; idMan++)
      out << "<th>" << nameMen[idMan] << "</th>";
  out << "</tr>" << endl;
  for (int i=0; i<nbWomen; i++)
  {
    out << "<tr>";
    for (int idMan=0; idMan<nbMen; idMan++)
    {
      out << "<td id=\"pM" << idMan << "-" << i << "\">";
      if (i < (int)prefMen[idMan].size())
        out << nameWomen[prefMen[idMan][i]];
      out << "</td>";
    }
    out << "</tr>" << endl;
  }
  out << "</table>\n<p/>\n<table>\n<tr>\n" << endl;
    for (int idWoman=0; idWoman<nbWomen; idWoman++)
      out << "<th>" << nameWomen[idWoman] << "</th>";
  out << "</tr>";
  for (int i=0; i<nbMen; i++)
  {
    out << "<tr>";
    for (int idWoman=0; idWoman<nbWomen; idWoman++)
    {
      out << "<td id=\"pW" << idWoman << "-" << i << "\">";
      if (i < (int)prefWomen[idWoman].size())
        out << nameMen[prefWomen[idWoman][i]];
      out << "</td>";
    }
    out << "</tr>" << endl;
  }
  out << "</body>\n</html>" << endl;
}
