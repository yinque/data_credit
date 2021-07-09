$(function() {
    ifcookie();
    function ifcookie(){
        var href_text = window.location.href;
        if(href_text.indexOf("?") != -1){
            if(getCookie('models_start')){
                $("#train_start").attr("value",getCookie('models_start'));
                
            }
            if(getCookie('models_end')){
                $("#train_end").attr("value",getCookie('models_end'));
            }
        }
    }
    //训练记录时间start
    $("#train_start").datepicker({
        onSelect: function (dateText, inst) {
            $("#train_start").datepicker("option", "minDate", dateText);
        }
    });
    //训练记录时间end
    $("#train_end").datepicker({
        onSelect: function (dateText, inst) {
            $("#train_end").datepicker("option", "maxDate", dateText);
        }
    });
    //用户时间段筛选（今日，近一周）
    $(".em-radio").click(function(){
        var data_value = $(this).attr("data-value");
        var href_text = window.location.href
        //截取浏览器没有参数的部分
        if(href_text.indexOf("?") != -1){
            href_text = href_text.slice(0,href_text.indexOf("?"));
        }
        href_text = href_text+"?tag="+data_value;
        $(this).attr("href",href_text);
    });
    //用户使用搜索
    $("#trains_manage_btn").click(function(){
        var train_start = $("#train_start").val();
        var train_end = $("#train_end").val();
        if(train_start == '' || train_end == ''){
            alert("请输入正确的时间段！")
        }else{
            setCookie("models_start",train_start);
            setCookie("models_end",train_end);
            var href_text = window.location.href;
            //截取浏览器没有参数的部分
            if(href_text.indexOf("?") != -1){
                href_text = href_text.slice(0,href_text.indexOf("?"));
            }
            href_text = href_text+"?start_time="+train_start+"&end_time="+train_end;
            $("#trains_manage_btn").attr("href",href_text);
        }
    });
})
//读取cookie
function getCookie(objName) {//获取指定名称的cookie的值
    var arrStr = document.cookie.split("; ");
    for (var i = 0; i < arrStr.length; i++) {
        var temp = arrStr[i].split("=");
        if (temp[0] == objName) return unescape(temp[1]);
    }
    return "";
}
//写cookies，一个小时过期 
function setCookie(name, value) { 
    var exp = new Date(); 
    exp.setTime(exp.getTime() + 60 * 60 * 1000); 
    document.cookie = name + "=" + escape(value) + ";expires=" + exp.toGMTString() + ";path=/"; 
}
function delCookie(name){
    var exp = new Date();
    exp.setTime(exp.getTime() - 1);
    var cval=getCookie(name);
    if(cval!=null)
    document.cookie= name + "="+cval+";expires="+exp.toGMTString();
}