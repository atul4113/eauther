package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.controller.AppController;

public class ChangeGridVisibilityAction extends AbstractPageAction {
	private AppController appController;
	
	public ChangeGridVisibilityAction(AppController controller) {
		super(controller);
		this.appController = controller;
	}

	public void execute(boolean isVisible) {
		getServices().getModel().setMetadataValue("useGrid", String.valueOf(isVisible));
		appController.getAppFrame().getSettings().setUseGridSelected(isVisible);
		appController.getModyficationController().setContentAsModified(true);
	}
}