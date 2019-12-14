#include <iostream>
#include <fstream>
#include <functional>
#include <algorithm>
#include <cassert>
#include <cmath>
#include <vector>
#include <random>
using namespace std;

#include "generate_preferences.cpp"
#include "deferred_acceptance.cpp"
#include "visualization.cpp"

const bool randomness = false;

int main(int argc, char** argv)
{
  int nbMen = 0, nbWomen = 0;
  vvi prefMen, prefWomen;
  
  if (randomness)
  {
    double lambdaMen = 1, lambdaWomen = 1;
    bool ok = false;
    if (argc == 5)
    {
      nbMen = atoi(argv[1]);
      nbWomen = atoi(argv[2]);
      lambdaMen = atof(argv[3]);
      lambdaWomen = atof(argv[4]);
      if (1 <= nbMen && nbMen <= 10000)
      if (1 <= nbWomen && nbWomen <= 10000)
      if (0 < lambdaMen && lambdaMen <= 1)
      if (0 < lambdaWomen && lambdaWomen <= 1)
        ok = true;
    }
    
    if (!ok)
    {
      cerr << "Usage: " << argv[0] << " nbMen nbWomen lambdaMen lambdaWomen" << endl;
      cerr << "- 0 < lambdaMen <= 1" << endl;
      cerr << "- 0 < lambdaWomen <= 1" << endl;
      return 1;
    }
  
    mt19937 generator(54);
    
    cerr << "Generation of preferences..." << endl;
    
    prefMen.resize(nbMen);
    for (int i=0; i<nbMen; i++)
      prefMen[i] = generateGeometric(generator, nbWomen, lambdaWomen);
    prefWomen.resize(nbWomen);
    for (int i=0; i<nbWomen; i++)
      prefWomen[i] = generateGeometric(generator, nbMen, lambdaMen);
  }
  else
  {
    //tie(prefMen, prefWomen) = generateExample();
    //tie(prefMen, prefWomen) = generateBounded();
    //tie(prefMen, prefWomen) = generateCycle(10);
    tie(prefMen, prefWomen) = generateWorstCase(3);
    //tie(prefMen, prefWomen) = generateCycleRand(generator, 20);
    //random_shuffle(prefMen.begin(), prefMen.end());
    //random_shuffle(prefWomen.begin(), prefWomen.end());
    //tie(prefMen, prefWomen) = generateRotationPerfect(5);
  }
  
  nbMen = prefMen.size();
  nbWomen = prefWomen.size();
  
  cerr << "Computing rotations" << endl;
  
  GaleShapley gs(prefMen, prefWomen);
  gs.computeSolution();
  
  cerr << "Output results" << endl;
  
  vector<string> nameMen, nameWomen;
  for (int i=1; i<=nbMen; i++)
    nameMen.push_back(to_string(i));
  for (int i=0; i<nbWomen; i++) // works when nbWomen <= 26
    nameWomen.push_back(string(1, 'A' + i % 26));
  
  Visualization vis(nameMen, nameWomen, prefMen, prefWomen, gs.rotation, gs.edges);
  vis.enumerate();
  vis.print_data(ofstream("data.js"));
  vis.print_rotations(ofstream("rotations.dot"));
  vis.print_matchings(ofstream("matchings.dot"));
  vis.print_preferences(ofstream("preferences.html"));
}
