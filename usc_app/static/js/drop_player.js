$("#drop_button").click(function(){
    if ($(".dropPlayer").css("display") == "none")
      $(".dropPlayer").css("display","inline-block")
    else
      $(".dropPlayer").css("display","none")
    $(this).blur();
});

$(".btn-sm").click(function(){
  event.preventDefault()
  var player = $(this).val()
  var title = "Are you sure you want to drop " + player + "?";
  swal({
    title: title ,
    type: "warning",
    showCancelButton: true,
    confirmButtonColor: "#DD6B55",
    confirmButtonText: "Confirm",
    closeOnConfirm: false
  },
  function(){
    var curr_href = window.location.pathname
    curr_href = curr_href.replace('team','drop')
    var href = curr_href+player;
    window.location.pathname = href;
    var message = player + " has been dropped from your team!";
    swal("Dropped!", message, "success");
  });
});
