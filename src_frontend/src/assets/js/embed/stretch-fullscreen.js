// 1. required libraries:
//      (1) CheckBrowser     <script src="/media/js/check-browser.js"></script>
//      (2) FullScreen       <script src="/media/js/fullscreen.js"></script>
// 2. required HTML structure:
//      body
//        #content-view (view wrapper - will be displayed in full screen mode and scaled in stretch to window size mode)
//          #content    (content wrapper)
//            iframe    (content)
// 3. required buttons:
//      (1) #display-fit-to-window-btn      (turn on/off fit to window width mode)
//      (2) #display-full-screen-btn        (turn on/off full screen mode)
// 4. exposes window.isStretchOrFullScreenMode which indicates if stretch to windows size or full screen mode is on
$(function () {
    var $body = $('body'),
        $frame = $('iframe#content-iframe'),
        embedWindow = $frame[0].contentWindow || $frame[0].contentDocument,
        $contentView = $('#content-view'),
        $content = $('#content'),
        $fitToWindowBtn = $('#display-fit-to-window-btn'),
        $fullScreenBtn = $('#display-full-screen-btn'),
        isFitToWindow = false,
        isFullScreen = false,
        isFullScreenSupported = window.FullScreen.support($contentView),
        frameInitialSize;

    function _resizeContentToWindow (retry) {
        var frameWidth = $frame.outerWidth(), frameHeight = $frame.outerHeight(),
            windowWidth = window.innerWidth,
            windowHeight = window.innerHeight,
            bodyWidth = $body.innerWidth(),
            bodyHeight = $body.innerHeight(),
            zoom = bodyWidth / frameWidth,
            scale;

        window.fitToWindowScale = zoom;

        if (!frameInitialSize) {
            frameInitialSize = {
                'width': frameWidth,
                'height': frameHeight
            };
        }

        scale = 'scale(' + zoom + ')';

        $frame.css({
            'position': 'relative',
            'left': 0,
            'top': 0,
            '-moz-transform': scale,
            '-webkit-transform': scale,
            '-o-transform': scale,
            '-ms-transform': scale,
            'transform': scale
        });
        
        if (zoom > 1) {
            $frame.css({
                "transform-origin": "center top",
                "-webkit-transform-origin": "center top"
            });
        } else if (zoom < 1) {
            $frame.css({
                "transform-origin": "left top",
                "-webkit-transform-origin": "left top"
            });
        }

        $contentView.css({
            'width': frameWidth * zoom + 'px',
            'max-width': frameWidth * zoom + 'px'
        });

        $content.css({
            'width': frameWidth * zoom + 'px',
            'height': frameHeight * zoom + 'px'
        });

        //if content is lower than window then resizing lesson to window width will cause scrollbar appearance,
        //scrollbar causes window width shrinking -- we need to resize content again to smaller window width.
        if (!retry && bodyWidth == windowWidth && windowHeight >= bodyHeight) {
            _resizeContentToWindow(true);
        }
    }

    function _clearAfterResizeToWindow () {
        $frame.css({
            'width': frameInitialSize.width + 'px',
            'height': frameInitialSize.height + 'px',
            'position': '',
            'left': '',
            'top': '',
            '-moz-transform': '',
            '-webkit-transform': '',
            '-o-transform': '',
            '-ms-transform': '',
            'transform': ''
        });

        $content.css({
            'width': '',
            'height': ''
        });

        $contentView.css({
            'width': '',
            'max-width': ''
        });
    }

    function _openFullScreen () {
        if (isFullScreenSupported) {
            window.FullScreen.request($contentView);
            $contentView.css({
                'width': screen.width,
                'max-width': screen.width,
                'height': screen.height,
                'overflow-y': 'auto',
                'overflow-x': 'hidden',
                'display': 'block',
                'position': 'absolute',
                'top': 0,
                'left': 0
            });
            $content.css({
                'overflow': 'hidden'
            });
            _resizeContentToWindow();
        }
    }

    function _closeFullScreen () {
        if (isFullScreenSupported) {
            window.FullScreen.exit();
            $contentView.css({
                'width': '',
                'height': '',
                'overflow-y': '',
                'overflow-x': '',
                'max-width': '',
                'display': '',
                'position': '',
                'top': '',
                'left': ''
            });
            $content.css({
                'overflow': ''
            });
            _clearAfterResizeToWindow();
        }
    }

    function _toggleBtnState ($btn) {
        if ($btn.hasClass('active')) {
            _clearBtnState($btn);
        } else {
            $btn.addClass('active');
            $btn.text('Original size');
        }
    }

    function _clearBtnState ($btn) {
        $btn.removeClass('active');
        $btn.text($btn.data('text'));
    }

    function _toggleFitToWindowBtnState () {
        _toggleBtnState($fitToWindowBtn);
    }

    function _toggleFullScreenBtnState () {
        _toggleBtnState($fullScreenBtn);
    }

    function onFitToWindowBtnClick () {
        _toggleFitToWindowBtnState();
        if (isFitToWindow) {
            isFitToWindow = false;
            window.isStretchOrFullScreenMode = false;
            _clearAfterResizeToWindow();
        } else {
            isFitToWindow = true;
            window.isStretchOrFullScreenMode = true;
            if (isFullScreen) {
                isFullScreen = false;
                _closeFullScreen();
                _toggleFullScreenBtnState();
            }
            _resizeContentToWindow();
        }
        $(this).blur();
    }

    function onFullScreenBtnClick () {
        _toggleFullScreenBtnState();
        if (isFullScreen) {
            isFullScreen = false;
            window.isStretchOrFullScreenMode = false;
            _closeFullScreen();
        } else {
            isFullScreen = true;
            window.isStretchOrFullScreenMode = true;
            if (isFitToWindow) {
                isFitToWindow = false;
                _clearAfterResizeToWindow();
                _toggleFitToWindowBtnState();
            }
            _openFullScreen();
        }
        $(this).blur();
    }

    function onWindowResize () {
        if (isFitToWindow || isFullScreen) {
            _resizeContentToWindow();
        }
    }

    function onMessageReceived (event) {
        var data = event.data, size, width, height;
        if (data.indexOf('RESIZE:') === 0) {
            size = data.substring('RESIZE:'.length).split(';');
            width = parseInt(size[0]);
            height = parseInt(size[1]);

            frameInitialSize = {
                'width': width,
                'height': height
            };

            $frame.css({
                'width': width + 'px',
                'height': height + 'px'
            });

            if (isFitToWindow || isFullScreen) {
                _resizeContentToWindow();
            }
        }
    }

    function onFullScreenChanged (fullScreenElement) {
        if (!fullScreenElement) {
            isFullScreen = false;
            window.isStretchOrFullScreenMode = false;
            _closeFullScreen();
            _clearAfterResizeToWindow();
            _clearBtnState($fullScreenBtn);
        } else if(isFullScreen) {
            _resizeContentToWindow();
        }
    }


    if (window.CheckBrowser.mobileAndTabletCheck()) {
        $fitToWindowBtn.hide();
        $fullScreenBtn.hide();
    } else {
        window.addEventListener('message', onMessageReceived, false);
        $(window).resize(onWindowResize);

        $fitToWindowBtn.click(onFitToWindowBtnClick);

        if (isFullScreenSupported) {
            $fullScreenBtn.click(onFullScreenBtnClick);
            window.FullScreen.onChanged(onFullScreenChanged);
        } else {
            $fullScreenBtn.hide();
        }
    }
});