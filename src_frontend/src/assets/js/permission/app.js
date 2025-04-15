/**
 *  Requires:
 *      - Mustache.js
 *      - jQuery
 *      - Mustache tags set to [[ ]]
  */



;(function () {
    function mapRoleName(role) {
        return role["name"];
    }

    function filterCheckedRoles(role) {
        return role["checked"];
    }

    function addPublicationsFlag(element) {
        element["have_publications"] = element["publications"].length > 0;
        return element;
    }

    function render($element, template, data) {
        $element.html(Mustache.to_html(template, data));
    }
    
    function hide($element) {
        var $dfd = new $.Deferred();

        $element.removeClass("active");
        $element.fadeOut(100, function () {
            $dfd.resolve();
        });

        return $dfd;
    }

    function show($element) {
        var $dfd = new $.Deferred();

        if ($element.hasClass("active")) {
            $element.fadeIn(0, function () {
               $dfd.resolve();
            });
            return $dfd
        } else {
            $element.addClass("active");
            $element.fadeIn(100, function () {
                $dfd.resolve();
            });

            return $dfd;
        }
    }

    function cleanAndCreateFailureMessage(msg) {
        window.Messages.clean();
        window.Messages.createFailureMessage(msg);
    }

    PermissionsApp.prototype.createInfoMessageOnce = function createInfoMessageOnce(msg) {
        if (!this.isCalculatinMessageWasOpened) {
            this.isCalculatinMessageWasOpened = true;
            window.Messages.clean();
            window.Messages.createInfoMessage(msg);
        }
    };

    function cleanAndCreateSuccessMessage(msg) {
        window.Messages.clean();
        window.Messages.createSuccessMessage(msg);
    }

    function cleanAndCreateServerErrorMessage() {
        window.Messages.clean();
        window.Messages.createFailureMessage("Server error, please contact with support.");
    }

    function getUserPanelRolePanelQuery($element, panelQuery) {
        return panelQuery + "[data-roles-panel=\"" + $element.data("roles-panel") + "\"]";
    }

    function getPanelCheckboxes($button, $table, panelQuery) {
        var $rolesPanel = $table.find(getUserPanelRolePanelQuery($button, panelQuery));
        return $.makeArray($rolesPanel.find("input[type=\"checkbox\"]")).map(function (element) {
            return $(element);
        });
    }

    function getUsersWithPermissionsView(companyUsers, usersPermissions, allRoles) {
        var permissionsHashMap = {};
        usersPermissions.forEach(function (user) {
            permissionsHashMap[user["id"]] = user["actual_roles"].map(function (actualRole) {
                return actualRole["id"];
            });
        });

        return companyUsers.map(function (companyUser, index) {
            return {
                "id": companyUser["userid"],
                "name": companyUser["name"],
                "user-index": index
            };
        }).map(function (userView) {
            var canRemovePermission = false;
            userView["roles"] = allRoles.map(function(role) {
                var isChecked = false;
                if (permissionsHashMap[userView["id"]]) {
                    isChecked = permissionsHashMap[userView["id"]].indexOf(role["id"]) != -1;
                }

                if (isChecked) {
                    canRemovePermission = true;
                }

                return {
                    "id": role["id"],
                    "name": role["name"],
                    "checked":  isChecked,
                };
            });

            userView["canRemovePermission"] = canRemovePermission;
            userView["roles-string"] = userView["roles"].filter(filterCheckedRoles).map(mapRoleName).join(",");
            return userView;
        });
    }

    function PermissionsApp (settings) {
        this.isCompanyAdmin = settings["is_company_admin"];

        this.shouldShowBackButton = false;

        this.roles = settings["roles"] || [];
        this.projects = settings["projects"] || [];
        this.company = settings["company"] || {"have": false};
        this.permissionsLevel = settings["permissions_level"] || {};
        this.permissions = settings["permissions"] || [];
        this.companyUsers = settings["companyUsers"] || [];
        this.$addUserRolesContainer = settings["addUserRolesContainer"] || null;
        this.$addRoleRolesContainer = settings["addRoleRolesContainer"] || null;
        this.$addUserToSpaceSelect = settings["addUserToSpaceSelect"] || null;
        this.$editRoleTable = settings["editRoleTable"] || null;
        this.$editRoleForm = settings["editRoleForm"] || null;
        this.$editRoleFormControls = settings["editRoleFormControls"] || null;
        this.$addRoleForm = settings["addRoleForm"] || null;
        this.$editRoleFormContent = settings["editRoleFormContent"] || null;
        this.$editRoleBackButtonContainer = settings["editRoleBackButtonContainer"] || null;
        this.$rolesPanelAddButton = settings["rolesPanelAddButton"] || null;
        this.$rolesPanelEditButton = settings["rolesPanelEditButton"] || null;
        this.$selectInUsersPanelContainer = settings["selectInUsersPanelContainer"] || null;
        this.$deleteUserButton = settings["deleteUserButton"] || null;
        this.$selectInProjectsPanel = settings["selectInProjectsPanel"] || null;
        this.$usersPanelTable = settings["usersPanelTable"] || null;
        this.$projectsPanelTable = settings["projectsPanelTable"] || null;
        this.templates = settings["templates"] || {
                editRoleTable: '',
                roles: '',
                projectsSelect: '',
                roleForm: '',
                editRoleForm: '',
                selectInUsersPanel: '',
                tableInUsersPanel: '',
                selectValues: '',
                tableInProjectsPanel: '',
                ajaxLoader: '',
        };

        this.$addUserUsernameInput = settings["addUserUsernameInput"] || null;
        this.$addRoleNameInput = settings["addRoleNameInput"] || null;
        this.$buttons = settings["buttons"] || {
            addRoleDiscard: null,
            addRoleSave: null,
            editRoleSave: null,
            editRoleDiscard: null,
            addUserToSpace: null
        };

        this.$usersPanelSelect = null;
        this.rolesHashmap = {};
        this.usersHashmap = {};
        this.projectsHashmap = {};

        this.$ajaxLoadersImages = settings["ajaxLoadersImages"] || {
            role: null,
            addUser: null,
            usersPanel: null,
            projectsPanel: null,
        };

        this.currentlyEditRoleID = undefined;
        this.currentlyUsersPanelID = undefined;
        this.firstOpen = true;
        this.isCalculatinMessageWasOpened = false;
    }

    PermissionsApp.prototype.defaults = {
        rolePermissionsGetUrl: "/permission/api/role/",
        rolePermissionsDeleteURL: "/permission/api/role/delete/",
        userProjectsGetUrl: "/permission/api/projects/company_user/",
        projectUsersGetUrl: "/permission/api/projects/project/",
        userPermissionURL: "/permission/api/user/permissions/",
        userPermissionEditURL: "/permission/api/user/edit/permissions/",
        userPermissionDeleteURL: "/permission/api/user/delete/permissions/",
        deleteCompanyUserURL: "permission/api/delete/company_user/",
        css: {
            usersPanelTableProjectRolePanel: ".roles-edit-panel.project-level",
            usersPanelTablePublicationRolePanel: ".roles-edit-panel.project-publication-level",
            usersPanelTablePublicationOnlyRolePanel: ".roles-edit-panel.publication-only-level",
            panelTableRemoveAccess: ".remove-access-button",
            usersPanelTableRemoveAccessPublicationLevel: ".publication-space-access-remove",

            usersPanelTablePublicationApply: ".publication-level-apply-button",
            usersPanelTablePublicationDiscard: ".publication-level-discard-button",

            notActiveLinkButton: "not-active-link-button",
            disabledLinkButton: "disabled",

            projectsPanelTableProjectUserPanel: ".roles-edit-panel.project-user-level",
            publicationsPanelTableProjectUserPanel: ".roles-edit-panel.publication-level",
        }
    };


    PermissionsApp.prototype.CONSTS = {
        ADD_ROLE_CHECK_ALL_INPUTS_PERMISSION_GROUP: "add-role-check-all-permission-group",
        ROLE_UNSUED_VALUE: "0",
        ERRORS: {
            ROLE_NAME_INVALID: "You have to type role name.",
            NO_ROLES_SELECTED: "You have to select permissions for role."
        }
    };

    PermissionsApp.prototype.init = function () {
        this.$editRoleFormControls.hide();
        this.$editRoleBackButtonContainer.hide();

        this.$addRoleRolesContainer.hide();
        this.$addRoleNameInput.hide();
        this.$addRoleForm.hide();
        this.hideAllAjaxLoaders();

        this.createProjectSelectView();
        this.createRolesView();
        this.createAddRolesView();
        this.createEditRoleTableView();
        this.renderUsersPanelSelect();
        this.createPanelProjectsSelect();

        this.connectHandlers();
    };

    PermissionsApp.prototype.hideAllAjaxLoaders = function () {
        $.each(this.$ajaxLoadersImages, function (_, $element) {
            $element.hide();
        });
    };

    PermissionsApp.prototype.createRolesView = function () {
        render(this.$addUserRolesContainer, this.templates.roles, {"roles": this.roles});
    };

    PermissionsApp.prototype.createProjectSelectView = function () {
        var data = {
            "company": this.company,
            "projects": this.projects.map(addPublicationsFlag),
            "have_projects": this.projects.length > 0,
            "isCompanyAdmin": this.isCompanyAdmin
        };

        render(this.$addUserToSpaceSelect, this.templates.projectsSelect, data);
    };

    PermissionsApp.prototype.createAddRolesView = function() {
        var data = this.permissions.map(function (permissionGroup) {
            permissionGroup.permissions = permissionGroup.permissions.map(function (permission) {
                var isCompany = this.permissionsLevel["company_level_only"].indexOf(permission) != -1;
                var isProject = this.permissionsLevel["project_level_only"].indexOf(permission) != -1;

                var data = {
                    "name": permission,
                    "level": "",
                    "group": permissionGroup.name
                };

                if (isCompany) {
                    data["level"] = "*";
                }

                if (isProject) {
                    data["level"] = "**";
                }

                return data;
            }, this);

            return permissionGroup;
        }, this);

        render(this.$addRoleRolesContainer, this.templates.roleForm, {
            "permissions": data
        });
    };

    PermissionsApp.prototype.createEditRoleTableView = function () {
        render(this.$editRoleTable, this.templates.editRoleTable, {
            "options": this.roles.filter(function (role) {
                return role.name !== "owner";
            })
        });

        this.$editRoleTable.find(".edit-role-edit-button").click(this.editRoleButtonHandler.bind(this));
        this.$editRoleTable.find(".edit-role-remove-button").click(this.editRoleDeleteHandler.bind(this));
    };

    PermissionsApp.prototype.connectHandlers = function () {
        this.rolePanelButtonsHandlers();
        this.$usersPanelSelect.on("change", this.usersPanelSelectHandler.bind(this));
        this.$selectInProjectsPanel.on("change", this.projectsPanelSelectHandler.bind(this));
        this.connectAddRoleHandlers();
        this.connectEditRoleHandlers();
        this.$buttons.addUserToSpace.click(this.addUserToSpaceHandler.bind(this));
        this.$editRoleBackButtonContainer.find(".edit-role-back-button").click(this.editRoleBackHandler.bind(this));
        this.$deleteUserButton.click(this.deleteUserHandler.bind(this));
    };

    PermissionsApp.prototype.addUserToSpaceHandler = function (event) {
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }
        var username = this.$addUserUsernameInput.val();
        var space = this.$addUserToSpaceSelect.val();
        var roles = $.makeArray(this.$addUserRolesContainer.find("input[type=\"checkbox\"]")).filter(function (input) {
                return $(input).prop("checked");
        }).map(function (input) {
            return $(input).val();
        });

        var data = {
            "user": username,
            "space": space,
            "roles": roles
        };

        var isCalculating = false;
        this.$ajaxLoadersImages.addUser.show();
        this.disableAddUserFormControls();
        $.when($.post(this.defaults.userPermissionURL, data)).then(function (responseData) {
            if (responseData.status == 200) {
                if (this.companyUsers.filter(function (user) {
                        return user["userid"] == responseData["user_id"]
                    }).length == 0) {

                    this.companyUsers.push({
                        "id": responseData["company_user_id"],
                        "name": responseData["company_username"],
                        "userid": responseData["user_id"]
                    });
                } else {
                    for(var i = 0; i < this.companyUsers.length; i++) {
                        if (this.companyUsers[i]["userid"] == responseData["user_id"]) {
                            this.companyUsers[i]["id"] = responseData["company_user_id"];
                        }
                    }
                }
                this.refreshUsersPanelSelect();
                this.$usersPanelSelect.val("none");
                this.$selectInProjectsPanel.val("none");
                this.projectsHashmap = {};
                this.usersHashmap = {};

                cleanAndCreateSuccessMessage(responseData["message"]);
                this.$usersPanelTable.css({
                    "display": "none"
                });

                this.$projectsPanelTable.css({
                    "display": "none"
                });
                this.isCalculatinMessageWasOpened = false;
            } else if (responseData.status == 202) {
                isCalculating = true;
                this.addUserToSpaceCalculatingCallback(responseData["message"]);
            } else {
                cleanAndCreateFailureMessage(responseData["message"]);
            }
        }.bind(this)).always(function () {
            if (!isCalculating) {
                this.isCalculatinMessageWasOpened = false;
                this.enableAddUserFormControls();
                this.$ajaxLoadersImages.addUser.hide();
            }
        }.bind(this)).fail(function () {
            cleanAndCreateServerErrorMessage();
        }.bind(this));
    };

    PermissionsApp.prototype.addUserToSpaceCalculatingCallback = function (msg){
        this.createInfoMessageOnce(msg);
        var self = this;
        setTimeout(function () {
            self.addUserToSpaceHandler();
        }, 5000);
    };

    PermissionsApp.prototype.rolePanelButtonsHandlers = function () {
        function toggle($currentButton, $currentForm, $oppositeButton, $oppositeForm) {
            if ($currentButton.hasClass("active")) {
                return;
            } else {
                $oppositeButton.removeClass("active btn-primary");
                $oppositeButton.addClass("btn-link");
                $oppositeForm.removeClass("active");
                $.when($oppositeForm.fadeOut(100)).then(function () {
                    $currentButton.addClass("active btn-primary");
                    $currentButton.removeClass("btn-link");
                    $currentForm.addClass("active");
                    $currentForm.fadeIn(100);
                });
            }
        }

        this.$rolesPanelEditButton.on("click", function () {
            toggle(this.$rolesPanelEditButton, this.$editRoleForm, this.$rolesPanelAddButton, this.$addRoleForm);
            if (this.shouldShowBackButton) {
                this.$editRoleBackButtonContainer.show();
            }
        }.bind(this));

        this.$rolesPanelAddButton.on("click", function () {

            if (this.firstOpen) {
                this.$addRoleRolesContainer.show();
                this.$addRoleNameInput.show();
                this.$addRoleForm.show();
                this.firstOpen = false;
            }

            toggle(this.$rolesPanelAddButton, this.$addRoleForm, this.$rolesPanelEditButton, this.$editRoleForm);
            this.$editRoleBackButtonContainer.hide();
        }.bind(this));
    };

    PermissionsApp.prototype.usersPanelSelectCallback = function (userID, data) {
         this.usersHashmap[userID] = data;
         this.renderUsersPanelTable(userID);
         this.showUsersPanelTable();
         this.enableUserDeleteButton();

    };

    PermissionsApp.prototype.enableUserDropDown = function () {
        this.$usersPanelSelect = $("#users-tab-select-for-user");
        this.$usersPanelSelect.removeAttr("disabled");
    };

    PermissionsApp.prototype.disableUserDropDown = function () {
        this.$usersPanelSelect = $("#users-tab-select-for-user");
        this.$usersPanelSelect.attr("disabled", "disabled");
    };

    PermissionsApp.prototype.getUsersResponseCallback = function (userID) {
        return function (data) {
            if (data["isCalculating"]) {
                this.showCalculatingMessage();
            } else {
                this.usersDataReicevedHandler(data, userID);
            }
        }.bind(this);
    };

    PermissionsApp.prototype.usersDataReicevedHandler = function (data, userID) {
        if (this.isCalculatinMessageWasOpened) {
            window.Messages.clean();
            window.Messages.createInfoMessage("User access rights recalculating is done.");
        }
        this.isCalculatinMessageWasOpened = false;
        this.usersPanelSelectCallback(userID, data);
        this.enableUserDropDown();
    };

    PermissionsApp.prototype.showCalculatingMessage = function () {
        if (!this.isCalculatinMessageWasOpened) {
            this.createInfoMessageOnce("User access rights are recalculated - this might take several minutes.")
            this.disableUserDropDown();
        }
        this.fireUsersPanelRefreshRequest();


    };

    PermissionsApp.prototype.usersPanelSelectHandler = function () {
        var userID = this.$usersPanelSelect.val();

        if(userID == "none") {
            this.hideUsersPanelTable();
            this.disableUserDeleteButton();
        } else {
            var url = this.defaults.userProjectsGetUrl + userID;
            this.currentlyUsersPanelID = userID;

            if (this.usersHashmap[userID] == undefined) {
                this.renderAjaxLoader(this.$usersPanelTable);

                $.when($.get(url))
                    .then(this.getUsersResponseCallback(userID))
                    .fail(function () {
                        cleanAndCreateServerErrorMessage();
                        this.disableUserDeleteButton();
                    }.bind(this));
            } else {
                this.renderUsersPanelTable(userID);
                this.showUsersPanelTable();
                this.enableUserDeleteButton();
            }
        }
    };

    PermissionsApp.prototype.fireUsersPanelRefreshRequest = function () {
        var self = this;
        setTimeout(function () {
            self.usersPanelSelectHandler();
        }, 5 * 1000);
    };

    PermissionsApp.prototype.deleteUserHandler = function (event) {
        if ($(event.target).attr("disabled")) {
            return;
        }

        var userID = this.$usersPanelSelect.val();
        if (userID !== "none") {
            var parsedUserID = parseInt(userID, 10);
            var username = this.companyUsers.filter(function (user) {
                return user["id"] == parsedUserID;
            })[0]["name"];
            var modal = new window.mCurriculumModal({
                acceptButtonClassName: "modal-button-footer-accept btn btn-large btn-danger",
                overrideAcceptButtonClass: true,
                closeButtonClassName: "btn btn-large btn-success",
                overrideCancelButtonClass: true,
                textContent: "Do you want to remove user: " + username + " from company?",
                acceptHandler: function () {
                    this.disableUsersPanelControls();
                    $.when($.post(this.defaults.deleteCompanyUserURL, {
                        "company_user_id": userID
                    })).then(function (responseData) {
                        if (responseData["status"] == 200) {
                            cleanAndCreateSuccessMessage(responseData["message"]);

                            this.companyUsers = this.companyUsers.filter(function (companyUser) {
                                return companyUser["id"] !== parsedUserID;
                            });
                            this.hideUsersPanelTable();
                            this.refreshUsersPanelSelect();
                        } else {
                            cleanAndCreateFailureMessage(responseData["message"]);
                        }
                    }.bind(this)).fail(function () {
                        cleanAndCreateServerErrorMessage();
                    }.bind(this)).always(function () {
                        this.enableUsersPanelControls();
                        this.disableUserDeleteButton();
                    }.bind(this));
                    modal.closeHandler();
                }.bind(this)
            });
            modal.open();
        }
    };

    PermissionsApp.prototype.projectsPanelSelectHandler = function () {
        var projectID = this.$selectInProjectsPanel.val();

        if(projectID == "none") {
            this.hideProjectsPanelTable();
        } else {
            var url = this.defaults.projectUsersGetUrl + projectID;

            if (this.projectsHashmap[projectID] == undefined) {
                this.renderAjaxLoader(this.$projectsPanelTable);
                $.when($.get(url)).then(function (responseData) {
                    if (responseData["status"] === 200) {
                        this.projectsHashmap[projectID] = responseData;
                        this.renderProjectsPanelTable(projectID);
                        this.showProjectsPanelTable();
                    } else {
                        cleanAndCreateFailureMessage(responseData["message"]);
                    }
                }.bind(this)).fail(function () {
                    cleanAndCreateServerErrorMessage();
                    this.showProjectsPanelTable();
                }.bind(this));
            } else {
                this.renderProjectsPanelTable(projectID);
                this.showProjectsPanelTable();
            }
        }
    };

    PermissionsApp.prototype.connectAddRoleHandlers = function () {
        this.$addRoleRolesContainer.on("change", "input", function (event) {
            this.roleInputHandler(this.$addRoleRolesContainer, event);
        }.bind(this));
        this.$buttons.addRoleDiscard.click(this.addRoleDiscardHandler.bind(this));
        this.$buttons.addRoleSave.click(this.addRoleSaveHandler.bind(this));
    };

    PermissionsApp.prototype.roleInputHandler = function ($container, event) {
        var $element = $(event.target);

        if ($element.hasClass(this.CONSTS.ADD_ROLE_CHECK_ALL_INPUTS_PERMISSION_GROUP)) {
            this.allCheckboxHandler($container, $element);
        } else {
            this.singleCheckboxHandler($container, $element);      
        }
    };
    
    PermissionsApp.prototype.allCheckboxHandler = function ($container, $element) {
        var selector = "input[data-group=\"" + $element.data("group-parent") + "\"]";
      
        if ($element.prop("checked")) {
            $container.find(selector).prop("checked", true);
        } else {
            $container.find(selector).prop("checked", false);
        }
    };

    PermissionsApp.prototype.singleCheckboxHandler = function ($container, $element) {
        function isChecked(element) {
            return $(element).prop("checked") == true;
        }

        var groupSelector = "input[data-group=\"" + $element.data("group") + "\"]";
        var parentSelector = "input[data-group-parent=\"" + $element.data("group") + "\"]";

        var allInputsElements = $.makeArray($container.find(groupSelector));
        $container.find(parentSelector).prop("checked", allInputsElements.every(isChecked));
    };

    PermissionsApp.prototype.addRoleDiscardHandler = function (event) {
        event.stopPropagation();
        event.preventDefault();
        this.$addRoleRolesContainer.find("input").prop("checked", false);
        this.$addRoleNameInput.val("");
    };

    PermissionsApp.prototype.addRoleSaveHandler = function (event) {
        event.stopPropagation();
        event.preventDefault();

        if ($(event.target).hasClass("disabled")) {
            return;
        }

        var roleData = this.getAddRoleData();
        if (roleData.isValid == false) {
            cleanAndCreateFailureMessage(roleData.errorMsg);
            return;
        }

        this.$ajaxLoadersImages.role.show();
        this.disableAddRoleControls();
        var $request = $.post(this.defaults.rolePermissionsGetUrl, roleData);

        $.when($request).then(function (responseData) {
            if (responseData.status == 200) {
                this.roles.push({
                    "id": responseData["role_id"],
                    "name": roleData["name"]
                });

                this.rolesHashmap[responseData["role_id"]] = responseData["role_permissions"];
                this.refreshRolesView();
                this.clearAddRoleForm();
                cleanAndCreateSuccessMessage(responseData["message"]);
            } else {
                cleanAndCreateFailureMessage(responseData["message"]);
            }
        }.bind(this)).always(function () {
            this.$ajaxLoadersImages.role.hide();
            this.enableAddRoleControls();
        }.bind(this)).fail(function (responseData) {
            if (responseData.status == 400) {
                cleanAndCreateFailureMessage(responseData["message"]);
            }
        });
    };

    PermissionsApp.prototype.refreshRolesView = function () {
        this.createRolesView();
        this.createEditRoleTableView();
        this.hideEditRoleFormContainer();
    };
    
    PermissionsApp.prototype.refreshUsersPanelSelect = function () {
        this.renderUsersPanelSelect();
        this.$usersPanelSelect.on("change", this.usersPanelSelectHandler.bind(this));
    };

    PermissionsApp.prototype.clearAddRoleForm = function () {
        this.$addRoleNameInput.val("");
        this.$addRoleRolesContainer.find("input").prop("checked", false);
    };

    PermissionsApp.prototype.getAddRoleData = function () {
        var roleName = this.$addRoleNameInput.val();
        var values = $.makeArray(this.$addRoleRolesContainer.find("input[type=\"checkbox\"]")).map(function (element) {
            var $element = $(element);
            if ($element.prop("checked")) {
                return $element.val();
            }

            return this.CONSTS.ROLE_UNSUED_VALUE;
        }, this).filter(function (value) {
            return value !== this.CONSTS.ROLE_UNSUED_VALUE;
        }, this);

        if (roleName.trim() == "") {
            return {
                isValid: false,
                errorMsg: this.CONSTS.ERRORS.ROLE_NAME_INVALID
            };
        }

        if (values.length == 0) {
            return {
                isValid: false,
                errorMsg: this.CONSTS.ERRORS.NO_ROLES_SELECTED
            };
        }

        return {
            "isValid": true,
            "name": roleName,
            "permissions": values
        };
    };

    PermissionsApp.prototype.disableAddRoleControls = function () {
        this.$buttons.addRoleDiscard.addClass("disabled");
        this.$buttons.addRoleDiscard.attr("disabled", true);

        this.$buttons.addRoleSave.addClass("disabled");
        this.$buttons.addRoleSave.attr("disabled", true);

        this.$addRoleRolesContainer.find("input").attr("disabled", true);
        this.$addRoleNameInput.attr("disabled", true);
    };

    PermissionsApp.prototype.disableAddUserFormControls = function () {
        this.$addUserRolesContainer.find("input[type=\"checkbox\"]").attr("disabled", true);
        this.$addUserUsernameInput.attr("disabled", true);
        this.$addUserToSpaceSelect.attr("disabled", true);

        this.$buttons.addUserToSpace.addClass("disabled");
        this.$buttons.addUserToSpace.attr("disabled", true);
    };

    PermissionsApp.prototype.enableAddUserFormControls = function () {
        this.$addUserRolesContainer.find("input[type=\"checkbox\"]").attr("disabled", false);
        this.$addUserUsernameInput.attr("disabled", false);
        this.$addUserToSpaceSelect.attr("disabled", false);

        this.$buttons.addUserToSpace.removeClass("disabled");
        this.$buttons.addUserToSpace.attr("disabled", false);
    };

    PermissionsApp.prototype.enableAddRoleControls = function () {
        this.$buttons.addRoleDiscard.removeClass("disabled");
        this.$buttons.addRoleDiscard.attr("disabled", false);

        this.$buttons.addRoleSave.removeClass("disabled");
        this.$buttons.addRoleSave.attr("disabled", false);

        this.$addRoleRolesContainer.find("input").attr("disabled", false);
        this.$addRoleNameInput.attr("disabled", false);
    };

    PermissionsApp.prototype.disableUserDeleteButton = function () {
        this.$deleteUserButton.attr("disabled", true);
    };

    PermissionsApp.prototype.enableUserDeleteButton = function () {
        this.$deleteUserButton.attr("disabled", false);
    };

    PermissionsApp.prototype.connectEditRoleHandlers = function () {
        this.$editRoleFormContent.on("change", "input", function (event) {
            this.roleInputHandler(this.$editRoleFormContent, event);
        }.bind(this));


        this.$buttons.editRoleDiscard.click(this.editRoleDiscardHandler.bind(this));
        this.$buttons.editRoleSave.click(this.editRoleSaveHandler.bind(this));
    };

    PermissionsApp.prototype.editRoleButtonHandler = function (event) {
        var $button = $(event.target);
        var roleID = $button.data("roleid");

        $.when(hide(this.$editRoleTable)).then(function () {
            this.currentlyEditRoleID = roleID;

            if (this.rolesHashmap[roleID] == undefined) {
                var url = this.defaults.rolePermissionsGetUrl + roleID;
                this.$editRoleFormControls.hide();
                this.renderAjaxLoader(this.$editRoleFormContent);
                this.showEditRoleFormContainer(true);
                $.when($.get(url)).then(function (responseData) {
                    if (responseData["status"] === 200) {
                        this.rolesHashmap[roleID] = responseData["role_permissions"];
                        this.renderEditRoleForm(this.rolesHashmap[roleID]);
                        this.showEditRoleFormContainer(false);
                    } else {
                        cleanAndCreateFailureMessage(responseData["message"]);
                    }
                }.bind(this)).fail(function () {
                    cleanAndCreateServerErrorMessage();
                });
            } else {
                this.renderEditRoleForm(this.rolesHashmap[roleID]);
                this.showEditRoleFormContainer(false);
            }
        }.bind(this));

        this.$editRoleBackButtonContainer.show();
        this.shouldShowBackButton = true;
    };

    PermissionsApp.prototype.editRoleBackHandler = function (event) {
        event.preventDefault();
        event.stopPropagation();
        $.when(this.hideEditRoleFormContainer()).then(function () {
            show(this.$editRoleTable);
        }.bind(this));
        this.shouldShowBackButton = false;
    };
    
    PermissionsApp.prototype.editRoleSaveHandler = function (event) {
        event.preventDefault();
        event.stopPropagation();
        
        if ($(event.target).hasClass("disabled")) {
            return;
        }
        
        this.disableEditRoleControls();
        this.$ajaxLoadersImages.role.show();
        var url = this.defaults.rolePermissionsGetUrl + this.currentlyEditRoleID;

        $.when($.post(url, this.getEditRoleData())).then(function (responseData) {
            if (responseData.status == 200) {
                this.rolesHashmap[this.currentlyEditRoleID] = responseData["role_permissions"];
                cleanAndCreateSuccessMessage(responseData["message"]);
            } else {
                cleanAndCreateFailureMessage(responseData["message"]);
            }
        }.bind(this)).fail(function () {
            cleanAndCreateServerErrorMessage();
        }).always(function () {
            this.enableEditRoleControls();
            this.$ajaxLoadersImages.role.hide();
        }.bind(this));
    };

    PermissionsApp.prototype.editRoleDeleteHandler = function (event) {
        var $element = $(event.target);
        var roleID = $element.data("roleid");
        var roleName = $element.data("rolename");
        var url = this.defaults.rolePermissionsDeleteURL + roleID;

        var modal = new window.mCurriculumModal({
            acceptButtonClassName: "modal-button-footer-accept btn btn-large btn-danger",
            overrideAcceptButtonClass: true,
            closeButtonClassName: "btn btn-large btn-success",
            overrideCancelButtonClass: true,
            textContent: "Do you want to delete role: " + roleName + "?",
            acceptHandler: function () {
                this.$ajaxLoadersImages.role.show();
                this.disableEditRoleTableControls();
                $.when($.post(url)).then(function (responseData) {
                    if (responseData["status"] == 200) {
                        this.roles = this.roles.filter(function (element) {
                            return element["id"] !== roleID;
                        });
                        this.createEditRoleTableView();
                        cleanAndCreateSuccessMessage(responseData["message"]);
                    } else {
                        cleanAndCreateFailureMessage(responseData["message"]);
                    }
                }.bind(this)).fail(function () {
                    cleanAndCreateServerErrorMessage();
                }).always(function () {
                    this.$ajaxLoadersImages.role.hide();
                    this.enableEditRoleTableControls();
                }.bind(this));
                modal.closeHandler();
            }.bind(this)
        });
        modal.open();
    };

    PermissionsApp.prototype.getEditRoleData = function () {
        var values = $.makeArray(this.$editRoleFormContent.find("input[type=\"checkbox\"]")).map(function (element) {
            var $element = $(element);
            if ($element.prop("checked")) {
                return $element.val();
            }

            return this.CONSTS.ROLE_UNSUED_VALUE;
        }, this).filter(function (value) {
            return value !== this.CONSTS.ROLE_UNSUED_VALUE;
        }, this);

        return {
            "permissions": values
        };
    };
    
    PermissionsApp.prototype.disableEditRoleControls = function () {
        this.$buttons.editRoleDiscard.addClass("disabled");
        this.$buttons.editRoleDiscard.attr("disabled", true);

        this.$buttons.editRoleSave.addClass("disabled");
        this.$buttons.editRoleSave.attr("disabled", true);

        this.$editRoleFormContent.find("input").attr("disabled", true);
    };

    PermissionsApp.prototype.enableEditRoleControls = function () {
        this.$buttons.editRoleDiscard.removeClass("disabled");
        this.$buttons.editRoleDiscard.attr("disabled", false);

        this.$buttons.editRoleSave.removeClass("disabled");
        this.$buttons.editRoleSave.attr("disabled", false);

        this.$editRoleFormContent.find("input").attr("disabled", false);
    };

    PermissionsApp.prototype.disableEditRoleTableControls = function () {
        this.$editRoleTable.find(".clickable-user-role-link").attr("disabled", true);
    };

    PermissionsApp.prototype.enableEditRoleTableControls = function () {
        this.$editRoleTable.find(".clickable-user-role-link").attr("disabled", false);
    };


    PermissionsApp.prototype.editRoleDiscardHandler = function (event) {
        event.preventDefault();
        event.stopPropagation();

        if (this.currentlyEditRoleID) {
            this.renderEditRoleForm(this.rolesHashmap[this.currentlyEditRoleID]);
        }
    };

    PermissionsApp.prototype.renderEditRoleForm = function (permissionsHashMap) {
        var data = $.extend([], this.permissions);

        for(var i = 0, len = data.length; i < len; i++) {
            var permissionGroup = data[i].name;
            data[i].permissions = data[i].permissions.map(function (element) {

                element["checked"] = permissionsHashMap[permissionGroup] && permissionsHashMap[permissionGroup][element.name];

                element["group"] = permissionGroup;
                return element;
            });
            
            data[i]["checked"] = data[i].permissions.every(function (element) {
                return element["checked"];
            });
        }

        render(this.$editRoleFormContent, this.templates.editRoleForm, {
            "permissions": data
        });

        this.$editRoleBackButtonContainer.show();
    };
    
    PermissionsApp.prototype.hideEditRoleFormContainer = function () {
        this.$editRoleFormControls.hide();
        this.$editRoleBackButtonContainer.hide();
        return hide(this.$editRoleFormContent);
    };
    
    PermissionsApp.prototype.showEditRoleFormContainer = function (isAjax) {
        if (!isAjax) {
            this.$editRoleFormControls.show();
        }
        this.$editRoleBackButtonContainer.show();
        return show(this.$editRoleFormContent);
    };

    PermissionsApp.prototype.hideUsersPanelTable = function () {
        hide(this.$usersPanelTable);
    };

    PermissionsApp.prototype.showUsersPanelTable = function () {
        show(this.$usersPanelTable);
    };

    PermissionsApp.prototype.hideProjectsPanelTable = function () {
        hide(this.$projectsPanelTable);
    };

    PermissionsApp.prototype.showProjectsPanelTable = function () {
        show(this.$projectsPanelTable);
    };

    PermissionsApp.prototype.renderUsersPanelSelect = function () {
        render(this.$selectInUsersPanelContainer, this.templates.selectInUsersPanel, {
            users: this.companyUsers
        });
        this.$usersPanelSelect = $("#users-tab-select-for-user");
    };

    PermissionsApp.prototype.renderUsersPanelTable = function (userID) {
        var data = this.usersHashmap[userID];

        data["publications"] = data["publications"].map(function (publication, index) {
            publication["row-index"] = index;
            publication["roles"] = this.roles.map(function (role) {
                return {
                    "checked":  (publication["actual_roles"].indexOf(role["id"]) != -1),
                    "id": role["id"],
                    "name": role["name"]
                };
            });


            publication["roles-string"] = publication["roles"].filter(filterCheckedRoles).map(mapRoleName).join(",");
            return publication;
        }, this);


        for (var i = 0, projects_len = data["projects"].length; i < projects_len; i++) {
            data["projects"][i]["row-index"] = i;
            data["projects"][i]["have-publications"] = data["projects"][i]["publications"].length > 0;

            data["projects"][i]["roles"] = this.roles.map(function (role) {
                return {
                    "checked":  (data["projects"][i]["actual_roles"].indexOf(role["id"]) != -1),
                    "id": role["id"],
                    "name": role["name"]
                };
            });            

            data["projects"][i]["roles-string"] = data["projects"][i]["roles"].filter(filterCheckedRoles).map(mapRoleName).join(",");

            data["projects"][i]["publications"] = data["projects"][i]["publications"].map(function (publication, index) {
                publication["row-index"] = i;
                publication["roles-row-index"] = index;
                publication["project_space_access_level"] = data["projects"][i]["project_space_access_level"];

                var publicationID = publication["id"];
                var publicationAccess = data["publications"].filter(function (pub) {
                    return pub["id"] == publicationID
                });

                if (publicationAccess.length > 0) {
                    publication["roles"] = publicationAccess[0]["roles"];
                } else {
                    publication["roles"] = this.roles.map(function (role) {
                        return {
                            "checked":  data["projects"][i]["actual_roles"].indexOf(role["id"]) != -1,
                            "id": role["id"],
                            "name": role["name"]
                        };
                    });

                    publication["roles-string"] = publication["roles"].filter(filterCheckedRoles).map(mapRoleName).join(",");
                }

                return publication;
            }, this);
        }

        if (data["projects"].length == 0 && data["publications"].length == 0) {
            data["have-no-data"] = true;
        } else {
            data["have-no-data"] = false;
        }

        render(this.$usersPanelTable, this.templates.tableInUsersPanel, data);
        this.connectUsersPanelTableHandlers();
    };

    PermissionsApp.prototype.connectUsersPanelTableHandlers = function () {
        this.$usersPanelTable.find(".project-level-discard-button").click(function (event) {
            var $checkboxes = getPanelCheckboxes($(event.target), this.$usersPanelTable, this.defaults.css.usersPanelTableProjectRolePanel);
            this.tableRolesDiscardHandler($checkboxes);
        }.bind(this));

        this.$usersPanelTable.find(".project-publication-level-discard-button").click(function (event) {
            var $checkboxes = getPanelCheckboxes($(event.target), this.$usersPanelTable, this.defaults.css.usersPanelTablePublicationRolePanel);
            this.tableRolesDiscardHandler($checkboxes);
        }.bind(this));

        this.$usersPanelTable.find(".publication-level-discard-button").click(function (event) {
            var $checkboxes = getPanelCheckboxes($(event.target), this.$usersPanelTable, this.defaults.css.usersPanelTablePublicationOnlyRolePanel);
            this.tableRolesDiscardHandler($checkboxes);
        }.bind(this));

        this.$usersPanelTable.find(".project-level-apply-button").click(function (event) {
            var $button = $(event.target);
            var projectID = $button.data("projectid");
            var $checkboxes = getPanelCheckboxes($button, this.$usersPanelTable, this.defaults.css.usersPanelTableProjectRolePanel);
            this.usersPanelApplyHandler($checkboxes, this.getUsersPanelUserData(), projectID);
        }.bind(this));
        this.$usersPanelTable.find(".project-publication-level-apply-button").click(function (event) {
            var $button = $(event.target);
            var projectID = $button.data("publicationid");
            var $checkboxes = getPanelCheckboxes($button, this.$usersPanelTable, this.defaults.css.usersPanelTablePublicationRolePanel);
            this.usersPanelApplyHandler($checkboxes, this.getUsersPanelUserData(), projectID);
        }.bind(this));
        
        this.$usersPanelTable.find(".project-space-access-remove").click(function (event) {
            var $button = $(event.target);
            var projectID = $button.data("projectid");
            var user = this.getUsersPanelUserData();

            var $dfdWork = this.usersPanelProjectRemoveAccessHandler($button, user, projectID);
            $.when($dfdWork).done(function () {
                this.usersHashmap[user["id"]]["projects"] = this.usersHashmap[user["id"]]["projects"].filter(function (project) {
                    return project["id"] != projectID;
                });
                this.renderUsersPanelTable(user["id"]);
            }.bind(this));
        }.bind(this));

        this.$usersPanelTable.find(this.defaults.css.usersPanelTableRemoveAccessPublicationLevel).click(function(event) {
            var $button = $(event.target);
            var user = this.getUsersPanelUserData();
            var publicationID = $button.data("publicationid");
            var $dfdWork = this.usersPanelProjectRemoveAccessHandler($button, user, publicationID);
            $.when($dfdWork).done(function () {
                this.usersHashmap[user["id"]]["publications"] = this.usersHashmap[user["id"]]["publications"].filter(function (project) {
                    return project["id"] != publicationID;
                });
                this.renderUsersPanelTable(user["id"]);
            }.bind(this));
        }.bind(this));
    };

    PermissionsApp.prototype.usersPanelProjectRemoveAccessHandler = function ($button, user, spaceID) {
        var $dfd = new $.Deferred();
        if ($button.hasClass("disabled")) {
            $dfd.reject();
            return $dfd;
        }

        var data = {
            "user_id": user["id"],
            "space_id": spaceID
        };

        this.disableUsersPanelControls();
        this.$ajaxLoadersImages.usersPanel.show();

        $.when($.post(this.defaults.userPermissionDeleteURL, data)).then(function (responseData) {
            if (responseData["status"] == 200) {
                cleanAndCreateSuccessMessage(responseData["message"]);
                $dfd.resolve();
            } else {
                cleanAndCreateFailureMessage(responseData["message"]);
                $dfd.reject();
            }
        }).fail(function () {
            cleanAndCreateServerErrorMessage();
            $dfd.reject();
        }).always(function () {
            this.enableUsersPanelControls();
            this.$ajaxLoadersImages.usersPanel.hide();
        }.bind(this));

        return $dfd;
    };

    PermissionsApp.prototype.getUsersPanelUserData = function () {
        var userID = this.$selectInUsersPanelContainer.find("select").val();
        var username = this.companyUsers.filter(function (element) {
            return element["id"] == userID;
        })[0]["name"];

        return {
            "id": userID,
            "name": username
        };
    };

    PermissionsApp.prototype.usersPanelApplyHandler = function ($checkboxes, user, spaceID) {
        var rolesIDs = $checkboxes.filter(function ($element) {
            return $element.prop("checked");
        }).map(function ($element) {
            return $element.data("value");
        });

        var data = {
            "user": user["name"],
            "space": spaceID,
            "roles": rolesIDs
        };

        this.$ajaxLoadersImages.usersPanel.show();
        this.disableUsersPanelControls();
        $.when($.post(this.defaults.userPermissionEditURL, data)).then(function (responseData) {
            if (responseData.status == 200) {
                cleanAndCreateSuccessMessage(responseData["message"]);
            } else {
                cleanAndCreateFailureMessage(responseData["message"]);
            }
        }.bind(this)).always(function () {
            this.$ajaxLoadersImages.usersPanel.hide();
            this.enableUsersPanelControls();
        }.bind(this)).fail(function () {
            cleanAndCreateServerErrorMessage();
        });
    };

    PermissionsApp.prototype.tableRolesDiscardHandler = function ($checkboxes) {
        $checkboxes.forEach(function ($element) {
            $element.prop("checked", false);
        });

        $checkboxes.filter(function ($element) {
            return $element.data("actualrole");
        }).forEach(function ($element) {
            $element.prop("checked", true);
        });
    };

    PermissionsApp.prototype.disableUsersPanelControls = function () {
        this.$usersPanelSelect.attr("disabled", true);
        this.$usersPanelTable.find("button").attr("disabled", true);
        this.$usersPanelTable.find("input[type=\"checkbox\"]").attr("disabled", true);
        this.$usersPanelTable.find(this.defaults.css.panelTableRemoveAccess)
            .addClass(this.defaults.css.notActiveLinkButton)
            .addClass(this.defaults.css.disabledLinkButton);
        this.$deleteUserButton.attr("disabled", true);
    };

    PermissionsApp.prototype.enableUsersPanelControls = function () {
        this.$usersPanelSelect.attr("disabled", false);
        this.$usersPanelTable.find("button").attr("disabled", false);
        this.$usersPanelTable.find("input[type=\"checkbox\"]").attr("disabled", false);
        this.$usersPanelTable.find(this.defaults.css.panelTableRemoveAccess)
            .removeClass(this.defaults.css.notActiveLinkButton)
            .removeClass(this.defaults.css.disabledLinkButton);
        this.$deleteUserButton.attr("disabled", false);
    };

    PermissionsApp.prototype.disableProjectsPanelControls = function () {
        this.$projectsPanelTable.attr("disabled", true);
        this.$projectsPanelTable.find("button").attr("disabled", true);
        this.$projectsPanelTable.find("input[type=\"checkbox\"]").attr("disabled", true);
        this.$projectsPanelTable.find(this.defaults.css.panelTableRemoveAccess)
            .addClass(this.defaults.css.notActiveLinkButton)
            .addClass(this.defaults.css.disabledLinkButton);
    };

    PermissionsApp.prototype.enableProjectsPanelControls = function () {
        this.$projectsPanelTable.attr("disabled", false);
        this.$projectsPanelTable.find("button").attr("disabled", false);
        this.$projectsPanelTable.find("input[type=\"checkbox\"]").attr("disabled", false);
        this.$projectsPanelTable.find(this.defaults.css.panelTableRemoveAccess)
            .removeClass(this.defaults.css.notActiveLinkButton)
            .removeClass(this.defaults.css.disabledLinkButton);
    };

    PermissionsApp.prototype.createPanelProjectsSelect = function () {
        var data = {
            "options": this.projects.map(function (project) {
                return {
                    "id": project.id,
                    "name": project.name
                };
            })
        };

        render(this.$selectInProjectsPanel, this.templates.selectValues, data);
    };

    PermissionsApp.prototype.renderProjectsPanelTable = function (projectID) {
        var data = this.projectsHashmap[projectID];
        var allRoles = this.roles;

        data["project-id"] = data["id"];

        data["publications"] = data["publications"].map(function (publication, index) {
            publication["publication-id"] = publication["id"];
            publication["publication-index"] = index;

            publication["usersView"] = getUsersWithPermissionsView(this.companyUsers, publication["users"], allRoles);
            return publication;
        }, this);
        
        data["project_usersView"] = getUsersWithPermissionsView(this.companyUsers, data["project_users"], allRoles);

        render(this.$projectsPanelTable, this.templates.tableInProjectsPanel, data);
        this.connectProjectsPanelTableHandlers();
    };

    PermissionsApp.prototype.connectProjectsPanelTableHandlers = function () {
        this.$projectsPanelTable.find(".project-user-discard-button").click(function (event) {
            var $checkboxes = getPanelCheckboxes($(event.target), this.$projectsPanelTable, this.defaults.css.projectsPanelTableProjectUserPanel);
            this.tableRolesDiscardHandler($checkboxes);
        }.bind(this));

        this.$projectsPanelTable.find(".publication-project-discard-button").click(function (event) {
            var $checkboxes = getPanelCheckboxes($(event.target), this.$projectsPanelTable, this.defaults.css.publicationsPanelTableProjectUserPanel);
            this.tableRolesDiscardHandler($checkboxes);
        }.bind(this));

        this.$projectsPanelTable.find(".project-user-apply-button").click(function (event) {
            var $button = $(event.target);
            var $checkboxes = getPanelCheckboxes($button, this.$projectsPanelTable, this.defaults.css.projectsPanelTableProjectUserPanel);
            this.projectsPanelApplyHandler($checkboxes, {
                "id": $button.data("userid"),
                "name": $button.data("username")
            }, $button.data("projectid"));
        }.bind(this));

        this.$projectsPanelTable.find(".publication-project-apply-button").click(function (event) {
            var $button = $(event.target);
            var $checkboxes = getPanelCheckboxes($button, this.$projectsPanelTable, this.defaults.css.publicationsPanelTableProjectUserPanel);
            this.projectsPanelApplyHandler($checkboxes, {
                "id": $button.data("userid"),
                "name": $button.data("username")
            }, $button.data("publicationid"));
        }.bind(this));

        this.$projectsPanelTable.find(".project-user-remove-access-button.remove-access-button").click(function (event) {
            var $button = $(event.target);
            var username = $button.data("username");
            var userID = $button.data("userid");
            var projectID = $button.data("projectid");
            var userCompanyID = this.companyUsers.filter(function (user) {
                    return user["name"] == username;
                })[0]["id"];

            var $dfdWork = this.projectsPanelRemoveAccessHandler($button, {
                "id": userCompanyID
            }, projectID);

            $.when($dfdWork).done(function () {
                this.projectsHashmap[projectID]["project_users"] = this.projectsHashmap[projectID]["project_users"].filter(function (user) {
                    return user["id"] !== userID;
                });
                this.renderProjectsPanelTable(projectID);
            }.bind(this));
        }.bind(this));

        this.$projectsPanelTable.find(".project-publication-remove-access-button.remove-access-button").click(function (event) {
            var $button = $(event.target);
            var username = $button.data("username");
            var publicationID = $button.data("publicationid");
            var projectID = $button.data("projectid");
            var userID = $button.data("userid");
            var userCompanyID = this.companyUsers.filter(function (user) {
                    return user["name"] == username;
            })[0]["id"];

            var $dfdWork = this.projectsPanelRemoveAccessHandler($button, {
                "id": userCompanyID
            }, publicationID);

            $.when($dfdWork).done(function () {
                var pubIndex;
                this.projectsHashmap[projectID]["publications"].filter(function (pub, index) {
                    if (pub["id"] == publicationID) {
                        pubIndex = index;
                        return true;
                    }

                    return false;
                });

                this.projectsHashmap[projectID]["publications"][pubIndex]["users"] = this.projectsHashmap[projectID]["publications"][pubIndex]["users"].filter(function (user) {
                    return user["id"] !== userID;
                });
                this.renderProjectsPanelTable(projectID);
            }.bind(this));

        }.bind(this));
    };
    
    PermissionsApp.prototype.projectsPanelApplyHandler = function ($checkboxes, user, spaceID) {
        var rolesIDs = $checkboxes.filter(function ($element) {
            return $element.prop("checked");
        }).map(function ($element) {
            return $element.data("value");
        });

        var data = {
            "user": user["name"],
            "space": spaceID,
            "roles": rolesIDs
        };

        this.$ajaxLoadersImages.projectsPanel.show();
        this.disableProjectsPanelControls();
        $.when($.post(this.defaults.userPermissionEditURL, data)).then(function (responseData) {
            if (responseData.status == 200) {
                cleanAndCreateSuccessMessage(responseData["message"]);
            } else {
                cleanAndCreateFailureMessage(responseData["message"]);
            }
        }.bind(this)).always(function () {
            this.$ajaxLoadersImages.projectsPanel.hide();
            this.enableProjectsPanelControls();
        }.bind(this)).fail(function () {
            cleanAndCreateServerErrorMessage();
        });
    };

    PermissionsApp.prototype.projectsPanelRemoveAccessHandler = function ($button, user, spaceID) {
        var $dfd = new $.Deferred();
        if ($button.hasClass("disabled")) {
            $dfd.reject();
            return $dfd;
        }

        var data = {
            "user_id": user["id"],
            "space_id": spaceID
        };

        this.$ajaxLoadersImages.projectsPanel.show();
        this.disableProjectsPanelControls();
        $.when($.post(this.defaults.userPermissionDeleteURL, data)).then(function (responseData) {
            if (responseData["status"] == 200) {
                cleanAndCreateSuccessMessage(responseData["message"]);
                $dfd.resolve();
            } else {
                cleanAndCreateFailureMessage(responseData["message"]);
                $dfd.reject();
            }
        }).fail(function () {
            cleanAndCreateServerErrorMessage();
            $dfd.reject();
        }).always(function () {
            this.$ajaxLoadersImages.projectsPanel.hide();
            this.enableProjectsPanelControls();
        }.bind(this));

        return $dfd;
    };

    PermissionsApp.prototype.renderAjaxLoader = function ($element) {
        render($element, this.templates.ajaxLoader, {});
    };

    window.lorepo = window.lorepo || {};
    window.lorepo.Permissions = window.lorepo.Permissions || PermissionsApp;
})(window);