(function (window) {
    var subscriber,
        $header,
        $footer,
        $window;

    var TYPES = {
        DELIMETER: ":",
        RESIZE: "mCurriculum_RESIZE",
        INITIALIZED: 'INITIALIZED'
    };

    function ResizeIframeSubscriber(iframeID) {
        subscriber = this;
        subscriber.iframe = document.getElementById(iframeID);
        subscriber.init();
    }

    ResizeIframeSubscriber.prototype.init = function () {
        $header = window.$('#home_header');
        $footer = window.$('.footer');
        $window = $(window);
        window.addEventListener("message", subscriber, false);
        window.addEventListener("resize", subscriber.sendInitMsg, false);
        subscriber.sendInitMsg();
    };

    ResizeIframeSubscriber.prototype.sendInitMsg = function () {
        var msg = TYPES.INITIALIZED + TYPES.DELIMETER;
        subscriber.iframe.contentWindow.postMessage(msg, "*");
    };

    ResizeIframeSubscriber.prototype.handleEvent = function (event) {
        if (event.type == "message") {
            subscriber.receiveMessage(event);
        }
    };

    ResizeIframeSubscriber.prototype.receiveMessage = function (event) {
        var data = event['data'].split(TYPES.DELIMETER);
        switch(data[0]) {
            case TYPES.RESIZE:
                subscriber.resizeCallback(data[1], data[2]);
                break;
        }
    };

    ResizeIframeSubscriber.prototype.resizeCallback = function (width, height) {
        var parsedHeight = Number(height);
        var minimalHeight = $window.height() - $header.height() - $footer.height() - 16;
        subscriber.iframe.height = Math.max(parsedHeight, minimalHeight);
    };

    window.mCurriculum = window.mCurriculum || {};
    window.mCurriculum.ResizeIframeSubscriber = window.mCurriculum.ResizeIframeSubscriber || ResizeIframeSubscriber;
})(window);