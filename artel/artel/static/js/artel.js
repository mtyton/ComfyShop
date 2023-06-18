
// close all alerts after 2 seconds
$('.alert').fadeTo(2000, 500).slideUp(500, function(){
    $("#success-alert").slideUp(500);
});
