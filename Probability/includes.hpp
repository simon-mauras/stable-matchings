#ifndef INCLUDES_HPP
#define INCLUDES_HPP

#include <cassert>
#include <map>
#include <vector>
#include <iostream>
using namespace std;
#define ALL(t) t.begin(),t.end()

#include <boost/multiprecision/gmp.hpp>
#include <boost/rational.hpp>
using I = boost::multiprecision::mpz_int;
using R = boost::rational<I>;

// (value, probability, state)
struct Answer
{
  int value; R proba;  int state;
  Answer() : value(-1), proba(0), state(-1) { assert(false); }
  Answer(int v, R p, int s) : value(v), proba(p), state(s) {}
};

#endif
