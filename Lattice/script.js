var matchings = [];
var rotations = [];
var preferences = [[],[]];
var currentMatching;

var color_active = "steelblue"
var color_inactive = "#d4dfed"

function fill(group, color) {
  group.getElementsByTagName("ellipse")[0].setAttribute("fill", color);
}

function callback_matching(idMatching) {
  // change the current matching
  var idRotation;
  for (idRotation=1; idRotation<nbRotations; idRotation++) {
    var color = downset[idMatching][idRotation] ? color_active : color_inactive;
    fill(rotations[idRotation], color);
  }
  var idMan, idWoman, color;
  for (idMan=0; idMan<nbMen; idMan++) {
    for (idWoman=0; idWoman<nbWomen; idWoman++) {
      color = stableM[idMan][idWoman] == -1 ? "white" : color_inactive;
      if (idWoman == prefM[idMatching][idMan]) color = color_active;
      preferences[0][idMan][idWoman].style.backgroundColor = color;
      color = stableW[idWoman][idMan] == -1 ? "white" : color_inactive;
      if (idMan == prefW[idMatching][idWoman]) color = color_active;
      preferences[1][idWoman][idMan].style.backgroundColor = color;
    }
  }
  fill(matchings[currentMatching], color_inactive);
  currentMatching = idMatching;
  fill(matchings[currentMatching], color_active);
}

function callback_rotation(idRotation) {
  // switch state of rotation, with a minimal number of changes
  callback_matching(transition[currentMatching][idRotation]);
}

function callback_man(idMan, idProp) {
  // match idMan with idProp, with a minimal number of changes
  var idRotation = stableM[idMan][idProp];
  if (idRotation == -1) return;
  if (prefM[currentMatching][idMan] == idProp) return;
  if (prefM[currentMatching][idMan] > idProp)
    do idRotation = stableM[idMan][++idProp];
    while (idRotation == -1);
  callback_rotation(idRotation);
}

function callback_woman(idWoman, idProp) {
  // match idWoman with idProp, with a minimal number of changes
  var idRotation = stableW[idWoman][idProp];
  if (idRotation == -1) return;
  if (prefW[currentMatching][idWoman] == idProp) return;
  if (prefW[currentMatching][idWoman] < idProp)
    do idRotation = stableW[idWoman][--idProp];
    while (idRotation == -1);
  callback_rotation(idRotation);
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
    fill(matchings[idMatching], color_inactive);
  }
  for (idRotation=1; idRotation<nbRotations; idRotation++) {
    rotations[idRotation] = r.getElementById("r" + idRotation);
    rotations[idRotation].onclick = function(id)
    {return function() { callback_rotation(id);}}(idRotation);
    fill(rotations[idRotation], color_inactive);
  }
  for (idMan=0; idMan<nbMen; idMan++) {
    preferences[0][idMan] = []
    for (idProp=0; idProp<nbWomen; idProp++) {
      var id = "pM" + idMan + "-" + idProp;
      preferences[0][idMan][idProp] = p.getElementById(id);
      preferences[0][idMan][idProp].onclick = function (idM, idP)
      {return function() { callback_man(idM, idP);}}(idMan, idProp);
    }
  }
  for (idWoman=0; idWoman<nbWomen; idWoman++) {
    preferences[1][idWoman] = []
    for (idProp=0; idProp<nbMen; idProp++) {
      var id = "pW" + idWoman + "-" + idProp;
      preferences[1][idWoman][idProp] = p.getElementById(id);
      preferences[1][idWoman][idProp].onclick = function (idW, idP)
      {return function() { callback_woman(idW, idP);}}(idWoman, idProp);
    }
  }
  currentMatching = 0;
  callback_matching(0);
  document.onkeydown = callback_keydown;
  m.onkeydown = callback_keydown;
  r.onkeydown = callback_keydown;
  p.onkeydown = callback_keydown;
}
