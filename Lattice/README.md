# Lattice of Stable Matchings

To vizualize the lattice structure of the set of stable matchings,
this tool generates animations in HTML+SVG+Javascript.

* This tool requires dot (package graphviz on linux): https://www.graphviz.org/
* To generate an animation, just run `bash gen.sh` in a linux command line.
* Then open the file `result/index.html` with a web browser (for example Firefox). 
With some web browsers (for example Google Chrome), the animation won't work if the
html is opened in local, without an http request.
To solve this issue, start a http server (for example `python3 -m http.server`)
and access the page at `http://localhost`. 
