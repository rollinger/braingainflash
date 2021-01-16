/* Project specific Javascript goes here. */

/*
All alert boxes with the class temporary-alert are fading up after
temporary_alert_fade_ms = 3500;
*/
temporary_alert_fade_ms = 3500;
$(".temporary-alert").fadeTo(temporary_alert_fade_ms, 500).slideUp(500, function(){
    $(".alert").slideUp(500);
});
