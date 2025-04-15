(function (window) {
    $(document).ready(function () {
        function is(type, obj) {
            var clas = Object.prototype.toString.call(obj).slice(8, -1);
            return obj !== undefined && obj !== null && clas === type;
        }

        function checkIsString(value) {
            return is("String", value);
        }

        function receiveMessage(event) {
            var re, match;

            function resizeLesson(width, height) {
                $('#lesson-iframe').css({
                    width: width + 'px',
                    height: height + 'px'
                });

                // Before preview is opened, presentation loading screen is displayed.
                // We're hiding it here in case Preview action doesn't do it.
                $('#presentationLoadingPage').css('display', 'none');
            }

            if (!checkIsString(event.data)) {
                return;
            }
            if (event.data.indexOf("RESIZE:") == 0) { // mAuthor
                re = new RegExp('RESIZE:(\\d+);(\\d+)');
            } else if (event.data.indexOf("resize:") == 0) { // mInstructor
                re = new RegExp('resize: width=(\\d+)px;height=(\\d+)px');
            } else {
                $('#presentationLoadingPage').css('display', 'none');
                return;
            }

            match = re.exec(event.data.toString());

            resizeLesson(match[1], match[2]);
        }

        window.addEventListener("message", receiveMessage, false);
    });
})(window);