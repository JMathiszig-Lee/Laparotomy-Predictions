$(document).ready(function(){
  
  $('select').formSelect();

  //fixes error message for selecte
  $("select[required]").css({display: "block", height: 0, padding: 0, width: 0, position: 'absolute'});

});