$(function () {
    var $window = $(window),
        $body = $('body'),
        $header = $('header'),
        $search = $('.header-top-bar__search'),
        $searchBtn = $('#header-top-bar__search-btn'),
        $searchSecond = $('.header-menu-bar__search'),
        $searchBtnSecond = $('#header-top-bar__search-btn-second'),
        $userBtn = $('#header-top-bar-user-btn'),
        $userMenu = $('#header-top-bar__user-menu'),
        $userBtnSecond = $('#header-top-bar-user-btn-second'),
        $userMenuSecond = $('#header-top-bar__user-menu-second'),
        $userMenuItems = $('#header-top-bar__user-menu .mdl-menu__item'),
        $drawer = $('.mdl-layout__drawer'),
        $drawerMask = $('.mdl-layout__drawer-mask'),
        $drawerButton = $('.mdl-layout__drawer-button'),
        $helpBtn = $('#header-menu-bar__help'),
        $helpMenu = $('#header-top-bar__help-menu'),
        $projectsBtn = $('#header-menu-bar__projects'),
        $projectsMenu = $('#header-top-bar__projects-menu');

    resizeCallback();

    $window.scroll(function () {
        if( $window.scrollTop() > 64 ) {
            $header.addClass('is-compact');
            $drawerButton.addClass('is-compact');
            $body.addClass('is-header-compact');
        } else {
            $header.removeClass('is-compact');
            $drawerButton.removeClass('is-compact');
            $body.removeClass('is-header-compact');
        }

        if ($projectsMenu.hasClass('opened')) {
            var position = getMenuLeftTopPosition($projectsBtn);
            $projectsMenu.css('left', position.left + 'px');
            $projectsMenu.css('top', position.top + 'px');
        }
    });

    function resizeCallback() {
       if(window.screen.width !== window.innerWidth) {
           $header.addClass("is-smaller");
           $(".mdl-layout__drawer-button").css("display", "inherit");
           $(".header-menu-bar").css("padding-left", "64px");
       } else {
           $(".mdl-layout__drawer-button").css("display", "none");
           $(".header-menu-bar").css("padding-left", "16px");
           $header.removeClass("is-smaller");
       }
    }

    $window.resize(function() {
        resizeCallback();
    });

    $searchBtn.on('click', function () {
        $search.toggleClass('expanded');
    });

    $searchBtnSecond.on('click', function () {
        $searchSecond.toggleClass('expanded');
    });

    $projectsBtn.on('click', function () {
        var position = getMenuLeftTopPosition($projectsBtn);
        $projectsMenu.css('left', position.left + 'px');
        $projectsMenu.css('top', position.top + 'px');
        $projectsMenu.toggleClass('opened');
    });

    $helpBtn.on('click', function () {
        var position = getMenuLeftTopPosition($helpBtn);
        $helpMenu.css('left', position.left + 'px');
        $helpMenu.css('top', position.top + 'px');
        $helpMenu.toggleClass('opened');
    });

    $userBtn.on('click', function () {
        $userMenu.css('right', getMenuRightPosition($userBtn) + 'px');
        $userMenu.toggleClass('opened');
    });

    $userBtnSecond.on('click', function () {
        $userMenuSecond.css('right', getMenuRightPosition($userBtnSecond) + 'px');
        $userMenuSecond.toggleClass('opened');
    });

    $userMenuItems.on('click', function () {
        $userMenu.removeClass('opened');
    });

    $drawerButton.on('click', function () {
        $drawer.addClass('opened');
        $drawerMask.addClass('opened');
        $body.addClass('drawer-opened');
    });

    $drawerMask.on('click', function () {
        $drawer.removeClass('opened');
        $drawerMask.removeClass('opened');
        $body.removeClass('drawer-opened');
    });

    function getMenuRightPosition ($menuTrigger) {
        return $body.width() - ($menuTrigger.position().left + $menuTrigger.width());
    }

    function getMenuLeftTopPosition ($menuTrigger) {
        return {
            left: $menuTrigger.position().left,
            top: $menuTrigger.position().top + $menuTrigger.height()
        }
    }
});