/**
 * Add property value handler,
 * function to add handlers for properties inputs, neccesary to block moving with arrows modules while editing properties
 */

(function (window) {
    function disableKeys() {
        window.iceEditorApplication.PropertyValueHandler.keysEnabled = false;
    }

    function enableKeys() {
        window.iceEditorApplication.PropertyValueHandler.keysEnabled = true;
    }

    var PropertyValueHandler = {
        keysEnabled: true,
		enableKeysAction: enableKeys,
        disableKeysAction: disableKeys
    };

    window.iceEditorApplication = window.iceEditorApplication || {};
    window.iceEditorApplication.PropertyValueHandler = window.iceEditorApplication.PropertyValueHandler || PropertyValueHandler;
})(window);