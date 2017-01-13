document.addEventListener('DOMContentLoaded', function () {
      document.querySelector('#g1_t1_score').addEventListener('change', submit);
      document.querySelector('#g1_t2_score').addEventListener('change', submit);
      document.querySelector('#g2_t1_score').addEventListener('change', submit);
      document.querySelector('#g2_t2_score').addEventListener('change', submit);
});
function submit(){
  g1t1=$('#g1_t1_score').val()
  g1t2=$('#g1_t2_score').val()
  g2t1=$('#g2_t1_score').val()
  g2t2=$('#g2_t2_score').val()
  if(g1t1 && g1t2 && g2t1 && g2t2){
    document.querySelector('#submit').style.display = 'inline-block';
  }
  else{
    document.querySelector('#submit').style.display = 'none';
  }
}
