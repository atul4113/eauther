(function (window) {
    function PageEnterSizesTimeout () {}
    
    PageEnterSizesTimeout.run = function () {
        setTimeout(function () {
            var $page = $('.ic_page.ic_main');
            var width = parseInt($page.width(), 10);
            var height = parseInt($page.height(), 10);
            window.iceRefreshPageDimensionsOnEnter(width, height);
        }, 0);
    };

    window.iceEditorApplication = window.iceEditorApplication || {};
    window.iceEditorApplication.PageEnterSizesTimeout = window.iceEditorApplication.PageEnterSizesTimeout || PageEnterSizesTimeout;
})(window);