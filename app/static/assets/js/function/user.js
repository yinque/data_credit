$(function () {
    ifcookie();

    function ifcookie() {
        var href_text = window.location.href;
        if (href_text.indexOf("?") != -1) {
            if (getCookie('user_name')) {
                $("#screen_name").val(getCookie('user_name'));
            }
            if (getCookie('user_sex')) {
                for (var i = 0; i < $("#screen_sex option").length; i++) {
                    if ($("#screen_sex option").eq(i).val() == getCookie('user_sex')) {
                        $("#screen_sex option").eq(i).attr("selected", true);
                    }
                }
            }
            if (getCookie('user_marital')) {
                for (var i = 0; i < $("#screen_marital option").length; i++) {
                    if ($("#screen_marital option").eq(i).val() == getCookie('user_marital')) {
                        $("#screen_marital option").eq(i).attr("selected", true);
                    }
                }
            }
            if (getCookie('user_education')) {
                for (var i = 0; i < $("#screen_education option").length; i++) {
                    if ($("#screen_education option").eq(i).val() == getCookie('user_education')) {
                        $("#screen_education option").eq(i).attr("selected", true);
                    }
                }
            }
            if (getCookie('user_age')) {
                $("#screen_age").val(getCookie('user_age'));
            }
            if (getCookie('train_start')) {
                $("#train_start").attr("value", getCookie('train_start'));
            }
            if (getCookie('train_end')) {
                $("#train_end").attr("value", getCookie('train_end'));
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
    $(".em-radio").click(function () {
        $(this).addClass("active").siblings(".em-radio").removeClass("active");
    });

    //点击用户搜索
    $("#user_screen_btn").click(function () {
        var name = $("#screen_name").val();
        var sex = $("#screen_sex option:selected").val();//1是男，0是女
        var age = $("#screen_age").val();
        var tel = $("#screen_tel").val();
        var email = $("#screen_email").val();
        var marital = $("#screen_marital option:selected").val();
        var education = $("#screen_education option:selected").val();
        var data = Object();
        if (name != '') {
            data.name = name;
        }
        if (age != '') {
            data.age = age;
        }
        if (sex != '') {
            data.sex = sex;
        }
        if (marital != '') {
            data.marital = marital;
        }
        if (education != '') {
            data.education = education;
        }
        if (tel != '') {
            data.tel = tel;
        }
        if (email != '') {
            data.email = email;
        }
        pag.setData(data);
        pag.turnPage(1);
    });
    //训练记录搜索
    $("#user_train_btn").click(function () {
        var train_start = $("#train_start").val();
        var train_end = $("#train_end").val();
        if (train_start == '' || train_end == '') {
            alert("请输入正确的时间段！")
        } else {
            setCookie("train_start", train_start);
            setCookie("train_end", train_end);
            var href_text = window.location.href;
            //截取浏览器没有参数的部分
            if (href_text.indexOf("?") != -1) {
                href_text = href_text.slice(0, href_text.indexOf("?"));
            }
            href_text = href_text + "?start_time=" + train_start + "&end_time=" + train_end;
            $("#user_train_btn").attr("href", href_text);
        }
    });
    //用户时间段筛选（今日，近一周）
    $(".em-radio").click(function () {
        var data_value = $(this).attr("data-value");
        if (data_value === "") {
            pag.cleanData()
        }
        else {
            pag.setData({'tag': data_value});
        }
        pag.turnPage(1);
    });
    $("#screen_class").change(function () {
        var child_class = $("#screen_class option:selected").val();
        $.ajax({
            type: "GET",//提交请求的方式
            async: true,
            url: "/train_models/num_of_model_two_class/" + child_class,//访问servlet的路径
            dataType: "json",//没有这个，将把后台放会的json解析成字符串
            success: function (result) {
                var name_str = [];
                var content_str = [];
                for (var j = 0; j < result.data.length; j++) {
                    name_str.push(result.data[j].name);
                    content_str.push({
                        value: result.data[j].count,
                        name: result.data[j].name
                    });
                }
                myChart_6.hideLoading();
                myChart_6.setOption({
                    legend: {
                        orient: 'vertical',
                        x: 'left',
                        data: name_str
                    },
                    series: [
                        {
                            name: '',
                            type: 'pie',
                            rradius: '60%',
                            center: ['50%', '60%'],
                            avoidLabelOverlap: false,
                            label: {
                                normal: {
                                    show: false,
                                    position: 'center'
                                },
                                emphasis: {
                                    show: false,
                                    textStyle: {
                                        fontSize: '24',
                                        fontWeight: 'bold'
                                    }
                                }
                            },
                            labelLine: {
                                normal: {
                                    show: false
                                }
                            },
                            data: content_str
                        }
                    ]
                });
            },
            error: function () {
                alert("图表请求数据失败!");
                myChart_6.hideLoading();
            }
        })
    });
    //效果筛选
    $("#user_screen_btn2").click(function () {
        var screen_education = $("#screen_education option:selected").val();
        alert(screen_education);
        var href_text = window.location.href
        //截取浏览器没有参数的部分
        if (href_text.indexOf("?") != -1) {
            href_text = href_text.slice(0, href_text.indexOf("?"));
        }
        href_text = href_text + "?pattern=" + screen_education;
        // $("#user_screen_btn2").attr("href",href_text);
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