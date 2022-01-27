$(function () {
    ifcookie();

    function ifcookie() {
        var href_text = window.location.href;
        if (href_text.indexOf("?") != -1) {
            if (getCookie('manage_start')) {
                $("#trains_start").attr("value", getCookie('manage_start'));
            }
            if (getCookie('manage_end')) {
                $("#trains_end").attr("value", getCookie('manage_end'));
            }
        }
    }

    //训练记录时间start
    $("#trains_start").datepicker({
        onSelect: function (dateText, inst) {
            $("#train_start").datepicker("option", "minDate", dateText);
        }
    });
    //训练记录时间end
    $("#trains_end").datepicker({
        onSelect: function (dateText, inst) {
            $("#train_end").datepicker("option", "maxDate", dateText);
        }
    });
});

