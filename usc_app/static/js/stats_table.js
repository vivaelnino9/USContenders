 function highlighting() {
   streak($("td.streak"));
   challenges($("td.challengeIn"));
   challenges($("td.challengeOut"));
   change("td.change");
   highestRank("td.highestRank");
 }

function streak (s){
  var streak = s.html()
  var streak_class = s.attr("class")
  if (streak>0)
    s.attr("class",streak_class + " positive")
  else if (streak<0)
    s.attr("class",streak_class + " negative")
  else{}
}
function challenges(c){
  var challenges = parseInt(c.html());
  var challenge_class = c.attr("class")
  if (challenges==2)
    c.attr("class",challenge_class + " negative")
  }
function change(c){
  var change = parseInt($(c).html());
  var change_class = $(c).attr("class")
  if (change>0)
    $(c).replaceWith('<td class="change positive">' + '▲' + ($(c).html()) + '</td>');
  else if (change<0)
    $(c).replaceWith('<td class="change negative">' + '▼' + String(Math.abs(change)) + '</td>');
}
function highestRank(h){
  var highestRank = parseInt($(h).html());
  var rank_class = $(h).attr("class");
  if (highestRank > 0 && highestRank < 6)
    $(h).attr("class",rank_class + " diamond")
  else if (highestRank > 6 && highestRank < 21)
    $(h).attr("class",rank_class + " gold")
  else if (highestRank > 21 && highestRank < 36)
    $(h).attr("class",rank_class + " silver")
  else if (highestRank>=36)
    $(h).attr("class",rank_class + " bronze")
  else{}


}
highlighting();
$("td.challengerStreak").each(function() {
  streak($(this));
});
$("td.challengerIn").each(function() {
  challenges($(this));
});
$("td.challengerOut").each(function() {
  challenges($(this));
});
