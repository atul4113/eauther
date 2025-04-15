(function (window) {
    /*
        based on: https://scotch.io/tutorials/building-your-own-javascript-modal-plugin
     */

    function Modal (options) {
        this.closeButton = null;
        this.acceptButton = null;
        this.modal = null;
        this.overlay = null;
        this.footer = null;
        this.contentHolder = null;
        this.loginLinkHolder = null;
        this.loginAnchor = null;

        this.options = Modal._internal.extendDefaultOptions(Modal._internal.getDefaultOptions(), options);

        this.transitionEnd = Modal._internal.transitionSelect();

        this.options = Modal._internal.addHandlers.call(this, this.options);
    }

    Modal._internal = {};

    Modal._internal.getDefaultOptions = function () {
        return {
            className: "mCurriculum-fade-and-drop",
            closeButton: true,
            closeButtonText: "Cancel",
            closeButtonClassName: "mCurriculum-close-button",
            overrideCancelButtonClass: false,
            closeHandler: null,
            acceptButton: true,
            acceptButtonText: "Accept",
            acceptButtonClassName: "mCurriculum-accept-button",
            overrideAcceptButtonClass: false,
            acceptHandler: null,
            maxWidth: 560,
            minWidth: 321,
            maxHeight: 600,
            minHeight: 200,
            footer: true,
            overlay: true,
            overlayHandler: null,
            textContent: "This is default text.",
            contentClassName: "mCurriculum-content",
            openClassName: "mCurriculum-open",
            anchoredClassName: "mCurriculum-anchored",
            overlayClassName: "mCurriculum-overlay",
            footerClassName: "mCurriculum-footer",
            linkHolderClassName: "mCurriculum-login-link"
        };
    };

    Modal._internal.addHandlers = function (options) {
        if (options.closeHandler === null) {
            options.closeHandler = Modal.prototype.closeHandler.bind(this);
        }

        if (options.acceptHandler === null) {
            options.acceptHandler = Modal.prototype.acceptHandler.bind(this);
        }

        if (options.overlayHandler === null) {
            options.overlayHandler = Modal.prototype.closeHandler.bind(this);
        }

        return options;
    };

    Modal._internal.extendDefaultOptions = function (source, properties) {
        var property;
        for (property in properties) {
            if (properties.hasOwnProperty(property)) {
                source[property] = properties[property];
            }
        }

        return source;
    };

    Modal._internal.build = function () {
        var documentFragment = document.createDocumentFragment();

        this.modal = document.createElement("div");
        this.modal.className = "mCurriculum-modal " + this.options.className;
        this.modal.style.minWidth = this.options.minWidth + "px";
        this.modal.style.maxWidth = this.options.maxWidth + "px";

        this.contentHolder = document.createElement("div");
        this.contentHolder.className = this.options.contentClassName;
        this.contentHolder.innerHTML = this.options.textContent;
        this.modal.appendChild(this.contentHolder);

        this.loginLinkHolder = document.createElement("div");
        this.loginLinkHolder.className = this.options.linkHolderClassName;
        this.loginLinkHolder.style.display = "none";
        this.modal.appendChild(this.loginLinkHolder);


        if (this.options.closeButton === true) {
            this.closeButton = document.createElement("button");

            if (this.options.overrideCancelButtonClass) {
                this.closeButton.className = this.options.closeButtonClassName;
            } else {
                this.closeButton.className = this.options.closeButtonClassName + " mCurriculum-button";
            }


            this.closeButton.innerHTML = this.options.closeButtonText;
        }


        if (this.options.acceptButton === true) {
            this.acceptButton = document.createElement("button");
            if (this.options.overrideAcceptButtonClass) {
                this.acceptButton.className = this.options.acceptButtonClassName;
            } else {
                this.acceptButton.className = this.options.acceptButtonClassName + " mCurriculum-button";
            }
            this.acceptButton.innerHTML = this.options.acceptButtonText;
        }

        if (this.options.footer === true) {
            this.footer = document.createElement("div");
            this.footer.className = this.options.footerClassName;
            if (this.options.acceptButton === true) {
                this.footer.appendChild(this.acceptButton);
            }
            this.footer.appendChild(this.closeButton);
            this.modal.appendChild(this.footer);
        } else  {
            if (this.closeButton) {
                this.modal.appendChild(this.closeButton);
            }

            if (this.acceptButton) {
                this.modal.appendChild(this.acceptButton);
            }
        }


        if (this.options.overlay === true) {
            this.overlay = document.createElement("div");
            this.overlay.className = this.options.overlayClassName + " " + this.options.className;
            documentFragment.appendChild(this.overlay);
        }

        documentFragment.appendChild(this.modal);

        document.body.appendChild(documentFragment);
    };

    Modal._internal.connectEvents = function () {
        if (this.closeButton) {
            this.closeButton.addEventListener('click', this.options.closeHandler.bind(this));
        }

        if (this.overlay) {
            this.overlay.addEventListener('click', this.options.overlayHandler.bind(this));
        }

        if (this.acceptButton) {
            this.acceptButton.addEventListener('click', this.options.acceptHandler.bind(this));
        }
    };

    Modal._internal.transitionSelect = function () {
        var el = document.createElement("div");

        if (el.style.WebkitTransition) return "webkitTransitionEnd";

        if (el.style.OTransition) return "oTransitionEnd";

        return 'transitionend';
    };

    Modal.prototype.open = function () {
        Modal._internal.build.call(this);

        Modal._internal.connectEvents.call(this);

        /*
         * After adding elements to the DOM, use getComputedStyle
         * to force the browser to recalc and recognize the elements
         * that we just added. This is so that CSS animation has a start point
        */
        window.getComputedStyle(this.modal).height;

        /*
         * Add our open class and check if the modal is taller than the window
         * If so, our anchored class is also applied
        */

        var anchoredClass = this.options.openClassName + this.options.anchoredClassName;

        if (this.modal.offsetHeight > window.innerHeight) {
            this.addCssClassNameToModal(anchoredClass);
        } else {
            this.addCssClassNameToModal(this.options.openClassName);
        }
        
        this.addCssClassNameToOverlay(this.options.openClassName);
    };

    Modal.prototype.closeHandler = function () {
        var _ = this;

        this.removeCssClassNameFromModal(this.options.openClassName);
        this.removeCssClassNameFromOverlay(this.options.openClassName);

        this.modal.addEventListener(this.transitionEnd, function () {
            _.modal.parentNode.removeChild(_.modal);
        });

        this.overlay.addEventListener(this.transitionEnd, function () {
            if (_.overlay.parentNode) _.overlay.parentNode.removeChild(_.overlay);
        })
    };

    Modal.prototype.acceptHandler = function () {
        this.closeHandler.call(this);
    };

    Modal.prototype.addCssClassNameToModal = function (className) {
        this.modal.className = this.modal.className + " " + className;
    };

    Modal.prototype.addCssClassNameToOverlay = function (className) {
        this.overlay.className = this.overlay.className + " " + className;
    };

    Modal.prototype.removeCssClassNameFromModal = function (className) {
        var removable = " " + className;
        this.modal.className = this.modal.className.replace(removable, "");
    };

    Modal.prototype.removeCssClassNameFromOverlay = function (className) {
        var removable = " " + className;
        this.overlay.className = this.overlay.className.replace(removable, "");
    };

    Modal.prototype.changeText = function (text) {
        this.contentHolder.innerHTML = text;
    };

    Modal.prototype.addLoginURL = function (login_label) {
        this.loginAnchor = document.createElement('a');
        var linkText = document.createTextNode(login_label);
        this.loginAnchor.appendChild(linkText);
        this.loginAnchor.href = '/accounts/login/';
        this.loginAnchor.target = "_blank";

        this.loginLinkHolder.appendChild(this.loginAnchor);
        this.loginLinkHolder.style.display = "block";
    };

    Modal.prototype.hideLoginURL = function () {
        if (this.loginAnchor) {
            this.loginLinkHolder.removeChild(this.loginAnchor);
            this.loginAnchor = null;
        }
        this.loginLinkHolder.style.display = "none";
    };

    window.mCurriculumModal = window.mCurriculumModal || Modal;
})(window);