$(function() {
    function autoLeftNav() {
        $('.tpl-header-switch-button').on('click', function () {
            if ($('.left-sidebar').is('.active')) {
                if ($(window).width() > 1024) {
                    $('.tpl-content-wrapper').removeClass('active');
                }
                $('.left-sidebar').removeClass('active');
            } else {

                $('.left-sidebar').addClass('active');
                if ($(window).width() > 1024) {
                    $('.tpl-content-wrapper').addClass('active');
                }
            }
        })
        if ($(window).width() < 1024) {
            $('.left-sidebar').addClass('active');
        } else {
            $('.left-sidebar').removeClass('active');
        }
    }

    autoLeftNav();
    $(window).resize(function () {
        autoLeftNav();
    });
    // 侧边菜单
    $('.sidebar-nav-sub-title').on('click', function () {
        $(this).siblings('.sidebar-nav-sub').slideToggle(80)
            .end()
            .find('.sidebar-nav-sub-ico').toggleClass('sidebar-nav-sub-ico-rotate');
    })
})
