// this library requires div element with id: messages

//http://getbootstrap.com/2.3.2/components.html#alerts
(function () {
    var $messages = undefined;

    function Messages() {}

    Messages.TYPES = {
        DEFAULT: "",
        ERROR: "alert-danger",
        INFO: "alert-info",
        SUCCESS: "alert-success",
        WARNING: "alert-warning"
    };

    Messages._checkMessagesBox = function _checkMessagesBox() {
        if ($messages === undefined) {
            $messages = $("#messages");
        }
    };

    Messages.createMessage = function createMessage(type, msg) {
        Messages._checkMessagesBox();

        var $msg = $('<div class="system-message alert ' + type + ' alert-dismissable alert-narrow"><span class="close">&times;</span>' + msg + '</div>');
        $messages.append($msg);
        $msg.slideDown();
        $msg.find('.close').click(function () {
            $(this).parent().fadeOut('slow');
        });
    };
    
    Messages.createQuestion = function createQuestion(type, msg, $okDeferred, $cancelDeferred) {
        Messages._checkMessagesBox();

        var buttonsString = '<div class="actions-container" style="margin-top: 5px;"><button class="btn btn-link ok-button" type="button">Ok</button><button class="btn btn-link cancel-button" type="button">Cancel</button></div>';
        var $msg = $('<div class="system-message alert ' + type + ' alert-dismissable alert-narrow"><span class="close">&times;</span>' + msg + buttonsString + '</div>');
        $messages.append($msg);
        $msg.slideDown();
        $msg.find(".ok-button").click(function (event) {
            $(this).parent().parent().fadeOut('slow');
            $okDeferred.resolve();
        });
        $msg.find(".cancel-button").click(function (event) {
            $(this).parent().parent().fadeOut('slow');
            $cancelDeferred.resolve();
        });
        $msg.find('.close').click(function () {
            $(this).parent().fadeOut('slow');
        });
    };

    Messages.clean = function clean(){
        Messages._checkMessagesBox();
        $messages.children().remove();
    };

    Messages.createFailureMessage = function createFailureMessage(msg) {
        Messages.createMessage(Messages.TYPES.ERROR, msg);
    };

    Messages.createSuccessMessage = function createSuccessMessage (msg) {
        Messages.createMessage(Messages.TYPES.SUCCESS, msg);
    };    
    
    Messages.createWarningMessage = function createFailureMessage(msg) {
        Messages.createMessage(Messages.TYPES.WARNING, msg);
    };
    
    Messages.createWarningQuestionMessage = function (msg, $okDeffered, $cancelDeferred) {
        Messages.createQuestion(Messages.TYPES.WARNING, msg, $okDeffered, $cancelDeferred);
    };

    Messages.createInfoMessage = function createSuccessMessage (msg) {
        Messages.createMessage(Messages.TYPES.INFO, msg);
    };

    window.Messages = window.Messages || Messages;
})(window);