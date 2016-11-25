for (var i = 1; i < 38; i++){
  var id = 'R' + String(i), color;
  if (i < 6)
    color = "#9fc5e8";
  else if (i >= 6 && i < 21)
    color = "#ffe38e";
  else if (i >= 21 && i < 36)
    color = "#dddddd";
  else
    color = "#eab786";

  document.getElementById(id).style.backgroundColor = color;
}
