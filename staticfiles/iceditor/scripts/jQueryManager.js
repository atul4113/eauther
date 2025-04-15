(function (window) {
    function jQueryManager () {
        this.selectors = [];
        this.selectedModule;
    }

    jQueryManager.prototype.add = function ($selector) {
        this.selectors.push($selector);
    };

    jQueryManager.prototype.clean = function () {
        this.selectors.map(function ($selector) {
            $selector.off();
            $selector.draggable('destroy');
            $selector.resizable('destroy');
        });
    };

    jQueryManager.prototype.cleanAll = function () {
        this.clean();

        this.selectors.forEach(function ($selector) {
            $selector = null;
        });

        this.selectors.length = 0;
        this.selectedModule = null;
    };

    jQueryManager.prototype.setSelectedModule = function($module) {
        this.selectedModule = $module;
    };

    jQueryManager.prototype.getSelectedModule = function() {
        return this.selectedModule;
    };
    
    window.iceEditorApplication = window.iceEditorApplication || {};
    window.iceEditorApplication.jQueryManager = window.iceEditorApplication.jQueryManager || jQueryManager;
})(window);