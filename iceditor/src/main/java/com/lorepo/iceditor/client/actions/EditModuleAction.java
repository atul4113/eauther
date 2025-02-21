package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.controller.AppController;

public class EditModuleAction extends AbstractPageAction{
	public EditModuleAction(AppController controller) {
		super(controller);
	}
	
	public void execute() {
		getServices().getAppController().getAppFrame().getPresentation().refreshView();
	}
}