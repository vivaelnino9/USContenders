function menu(){
  if ($(".dropdown-menu").css("display")=="none")
   $(".dropdown-menu").css("display","inline-block");
  else
   $(".dropdown-menu").css("display","none")
 }
 var avoid = ['rosters','team','player','results']
 for (var i in avoid){
   var href = location.pathname
   if (href.includes(avoid[i])){
      $("#home").attr("class","nav-link")
    }
 }
