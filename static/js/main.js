/**
 * Created by Angelos Roussakis on 17/07/16.
 */


$( function() {
    $(document).tooltip({
        position: {my: "left top", at: "right-260 top"}
    })
} );


$( function() {
    tinymce.init({
        selector: '#content',
        menubar: false,
        theme: 'modern',
        height: 400
    } )
} );


 $(document).ready(function () {
    $( "#dialog" ).click( function() {
       $( "#dialog" ).dialog({
            showText: true,
            modal: true,
            buttons: {
                Ok: function() {
                    $( this ).dialog( "close" );
                }
            }
        });
    } )
 } );


 $(document).ready(function () {
     $( "a[id^='commentButton']" ).click( function() {
         var strID = $(this).attr("id")
         id = strID.split("-")[1]
         str = "#comment-form-" + id
         $(str).toggle()
     });
 });

$(document).ready(function () {
    $("[id^='comments-area']").keydown(function(e) {
        var key = e.which;
        if (key == 13 && !e.shiftKey) {
           $(this).submit(); }

    });
});

 $(document).ready(function () {
    $( ".devname, .devtitle" ).click( function() {
        document.location.href = "/"
    });
 });

