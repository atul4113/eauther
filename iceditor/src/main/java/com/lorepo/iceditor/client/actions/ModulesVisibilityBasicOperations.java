package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.controller.AppController;

public class ModulesVisibilityBasicOperations extends AbstractPageAction{
	public ModulesVisibilityBasicOperations(AppController controller) {
		super(controller);
	}

	@Override
	public void execute() {

	}
	
	public void notifyEditorPageAboutModifyingModulesList() {
		getServices().getAppController().getModyficationController().setModified(true);
	}
}
