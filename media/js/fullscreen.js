window.FullScreen = (function () {
    var onChangeCallbacks = [];

    function request ($element) {
        var DomElement = $element.get(0);
        var requestMethod = DomElement.requestFullscreen || DomElement.mozRequestFullScreen ||
            DomElement.msRequestFullscreen || DomElement.webkitRequestFullScreen || null;

        if (requestMethod) {
            requestMethod.call(DomElement);
        }
    }

    function exit () {
        var exitMethod = document.exitFullscreen || document.mozCancelFullScreen ||
            document.msExitFullscreen || document.webkitExitFullscreen || null;

        if (exitMethod) {
            exitMethod.call(document);
        }
    }

    function element () {
        var fullScreenElement = document.fullscreenElement ||    // alternative standard method
            document.mozFullScreenElement || document.webkitFullscreenElement ||
            document.msFullscreenElement || null;

        return fullScreenElement;
    }

    function support ($element) {
        var DomElement = $element.get(0),
            requestMethod = DomElement.requestFullscreen || DomElement.mozRequestFullScreen ||
                DomElement.msRequestFullscreen || DomElement.webkitRequestFullScreen || null,
            exitMethod = document.exitFullscreen || document.mozCancelFullScreen ||
                document.msExitFullscreen || document.webkitExitFullscreen || null;
        return !!requestMethod && !!exitMethod;
    }

    function onChanged (callback) {
        onChangeCallbacks.push(callback);
    }

    $(document).on('webkitfullscreenchange mozfullscreenchange fullscreenchange MSFullscreenChange', function () {
        onChangeCallbacks.forEach(function (callback) {
            callback(element());
        })
    });

    return {
        'request': request,
        'exit': exit,
        'element': element,
        'support': support,
        'onChanged': onChanged
    }
})();