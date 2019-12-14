var matchings = [];
var rotations = [];
var preferences = [[],[]];
var currentMatching;

function fill(group, color) {
  group.getElementsByTagName("ellipse")[0].setAttribute("fill", color);
}

function callback_matching(idMatching) {
  var idRotation;
  for (idRotation=0; idRotation<nbRotations; idRotation++) {
    var color = downset[idMatching][idRotation] ? "lightgray" : "white";
    fill(rotations[idRotation], color);
  }
  var idMan, idWoman, color;
  for (idMan=0; idMan<nbMen; idMan++) {
    for (idWoman=0; idWoman<nbWomen; idWoman++) {
      color = idWoman <= prefM[idMatching][idMan] ? "lightgray" : "white";
      preferences[0][idMan][idWoman].style.backgroundColor = color;
      color = idMan >= prefW[idMatching][idWoman] ? "lightgray" : "white";
      preferences[1][idWoman][idMan].style.backgroundColor = color;
    }
  }
  fill(matchings[currentMatching], "white");
  currentMatching = idMatching;
  fill(matchings[currentMatching], "lightgray");
}

function callback_rotation(idRotation) {
  callback_matching(transition[currentMatching][idRotation]);
}

function callback_keydown(e) {
  if (e.keyCode == 39 && currentMatching+1 < nbMatchings)
    callback_matching(currentMatching+1);
  if (e.keyCode == 37 && currentMatching > 0)
    callback_matching(currentMatching-1);
}

function init() {
  var idMatching, idRotation, idMan, idWoman;
  var m = document.getElementById("matchings").contentDocument;
  var r = document.getElementById("rotations").contentDocument;
  var p = document.getElementById("preferences").contentDocument;
  for (idMatching=0; idMatching<nbMatchings; idMatching++)
  {
    matchings[idMatching] = m.getElementById("m" + idMatching);
    matchings[idMatching].onclick = function(id)
    {return function() { callback_matching(id);}}(idMatching);
    fill(matchings[idMatching], "white");
  }
  for (idRotation=0; idRotation<nbRotations; idRotation++) {
    rotations[idRotation] = r.getElementById("r" + idRotation);
    rotations[idRotation].onclick = function(id)
    {return function() { callback_rotation(id);}}(idRotation);
    fill(rotations[idRotation], "white");
  }
  for (idMan=0; idMan<nbMen; idMan++) {
    preferences[0][idMan] = []
    for (idWoman=0; idWoman<nbWomen; idWoman++) {
      var id = "pM" + idMan + "-" + idWoman;
      preferences[0][idMan][idWoman] = p.getElementById(id);
    }
  }
  for (idWoman=0; idWoman<nbWomen; idWoman++) {
    preferences[1][idWoman] = []
    for (idMan=0; idMan<nbMen; idMan++) {
      var id = "pW" + idWoman + "-" + idMan;
      preferences[1][idWoman][idMan] = p.getElementById(id);
    }
  }
  currentMatching = 0;
  callback_matching(0);
  document.onkeydown = callback_keydown;
  m.onkeydown = callback_keydown;
  r.onkeydown = callback_keydown;
  p.onkeydown = callback_keydown;
}
