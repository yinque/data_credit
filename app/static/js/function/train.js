$(function () {
    //编辑按钮
    $("#train_edit").click(function () {
        $("input").removeAttr("readonly");
        $("textarea").removeAttr("readonly");
        $("select").removeAttr("disabled");
    });
    // 保存按钮
    $("#train_submit").click(function () {
        //训练脑功能：
        var game_function = $("#game_function").val();
        //游戏名称：
        var game_name = $("#game_name").val();
        //训练时长：
        var game_time = $("#game_time").val();
        // 所属范围：
        var game_range = $("#game_range option:selected").val();
        //训练素材
        var game_fodder = $("#game_fodder").val();
        // 二级分类
        var game_twi = $("#game_twi").val();
        // 更新记录
        var game_record = $("#game_record").val();
        // 三级分类
        var game_thr = $("#game_thr").val();
        //描述
        var game_des = $("#game_des").val();
        if (game_function == '' || game_name == '' || game_time == '' || game_record == '' || game_fodder == '' || game_des == '') {
            alert("所有项都不能为空！")
        } else {
            console.log(game_function + game_name + game_range + game_range + game_fodder + game_twi + game_record + game_thr + game_des);
        }
    });
    // 新增游戏保存
    $("#train_submit_new").click(function () {
        // 数据库ID：
        var add_sql_id = $("#add_sql_id").val();
        // 所属范围：---训练方向
        var add_game_range = $("#add_game_range option:selected").val();
        // 模块ID：
        var add_module_id = $("#add_module_id").val();
        // 二级分类：
        var add_game_twi = $("#add_game_twi").val();
        // 模块名：
        var add_module_name = $("#add_module_name").val();
        // 三级分类：
        var add_game_thr = $("#add_game_thr").val();
        // 训练脑功能：---训练部位
        var add_game_function = $("#add_game_function").val();
        // 训练时长：
        var add_game_time = $("#add_game_time").val();
        // 训练素材：
        var add_game_fodder = $("#add_game_fodder").val();
        // 版本号
        var add_version_num = $("#add_version_num").val();
        // 内容描述：
        var add_game_des = $("#add_game_des").val();
        // var individuation = '{';
        // for (var i = 0; i < $(".personal-part").length; i++) {
        //     var key = $(".personal-part").eq(i).children("input").val();
        //     var value = $(".personal-part").eq(i).children("select").val();
        //     individuation = individuation + '"' + key + '":"' + value + '",'
        //     // individuation = individuation+"/"+key+"':"+"'"+value+"',"
        // }
        // individuation = individuation.slice(0, individuation.length - 1) + '}';
        // console.log(individuation);
        var individuation = {};
        for (var i = 0; i < $(".personal-part").length; i++) {
            var key = $(".personal-part").eq(i).children("input").val();
            var value = $(".personal-part").eq(i).children("select").val();
            individuation[key] = value
        }

        var post_data = {}
        post_data.database_id = add_sql_id;
        post_data.model_id = add_module_id;
        post_data.model_name = add_module_name;
        post_data.pattern = add_game_range;
        post_data.two_class = add_game_twi;
        post_data.three_class = add_game_thr;
        post_data.length = add_game_time;
        post_data.brain = add_game_function;
        post_data.content = add_game_des;
        post_data.attrs_struct = JSON.stringify(individuation);
        post_data.version = add_version_num;
        post_data.material = add_game_fodder;
        $.ajax({
            type: "post",//提交请求的方式
            // async: true,
            url: "/train_models/add_game",//访问servlet的路径
            data: JSON.stringify(post_data),
            contentType: 'application/json;charset=UTF-8',
            dataType: "json",//没有这个，将把后台放会的json解析成字符串
            success: function (result) {
                alert("新增成功!");
            },
            error: function () {
                alert("新增失败!");
            }
        })
    });
    $(".add_icon").click(function () {
        var num = $(".add_icon").attr("data-value");
        $(".personal_warp").prepend('<div class="personal-part">\
                <input type="text" value="" class="no-float personal" name="individuation_' + num + '">\
                <select class="no-float personal individuation_select" name="individuation_select_' + num + '">\
                    <option selected value="Integer">Integer</option>\
                    <option value="Boolean">Boolean</option>\
                    <option value="Float">Float</option>\
                    <option value="DateTime">DateTime</option>\
                    <option value="String">String</option>\
                </select>\
            </div>');
        num++;
        $(".add_icon").attr("data-value", num);
    });
    // 游戏管理-子分类
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
                myChart_12.hideLoading();
                myChart_12.setOption({
                    legend: {
                        orient: 'vertical',
                        x: 'left',
                        data: name_str
                    },
                    series: [
                        {
                            name: '',
                            type: 'pie',
                            radius: '60%',
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
                myChart_12.hideLoading();
            }
        })
    });
    //游戏管理搜索
    $("#user_train_btn_game").click(function () {
        var game_name = $("#game_name").val();
        var href_text = window.location.href;
        //截取浏览器没有参数的部分
        if (href_text.indexOf("?") != -1) {
            href_text = href_text.slice(0, href_text.indexOf("?"));
        }
        href_text = href_text + "?name=" + game_name;
        $("#user_train_btn_game").attr("href", href_text);

    });
    // 游戏管理详情---所属范围
    if ($("#hidden_span").length) {
        var hidden_span = $("#hidden_span").text();
        for (var i = 0; i < $("#game_range option").length; i++) {
            if ($("#game_range option").eq(i).val() == hidden_span) {
                $("#game_range option").eq(i).attr("selected", true);
            }
        }
    }
    //用户使用搜索
    $("#btn_game_user").click(function () {
        var train_start = $("#train_start").val();
        var train_end = $("#train_end").val();
        if (train_start == '' || train_end == '') {
            alert("请输入正确的时间段！")
        } else {
            var href_text = window.location.href;
            //截取浏览器没有参数的部分
            if (href_text.indexOf("?") != -1) {
                href_text = href_text.slice(0, href_text.indexOf("?"));
            }
            href_text = href_text + "?start_time=" + train_start + "&end_time=" + train_end;
            $("#btn_game_user").attr("href", href_text);
        }

    });
    //用户时间段筛选（今日，近一周）
    $(".em-radio").click(function () {
        var data_value = $(this).attr("data-value");
        var href_text = window.location.href
        //截取浏览器没有参数的部分
        if (href_text.indexOf("?") != -1) {
            href_text = href_text.slice(0, href_text.indexOf("?"));
        }
        href_text = href_text + "?args=" + data_value;
        $(".em-radio.active").attr("href", href_text);
    });
})
