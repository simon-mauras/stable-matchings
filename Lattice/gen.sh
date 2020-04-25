FOLDER="result"
mkdir -p $FOLDER
cd $FOLDER
cp ../template.html index.html
g++ -std=c++14 -Wall -Wextra -O2 ../main.cpp -o main
./main 10 10 1 1
dot -Tsvg rotations.dot > rotations.svg
dot -Tsvg matchings.dot > matchings.svg
