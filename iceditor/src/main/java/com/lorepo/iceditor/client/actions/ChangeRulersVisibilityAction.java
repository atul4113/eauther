package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.controller.AppController;

public class ChangeRulersVisibilityAction extends AbstractPageAction {
	private AppController appController;
	
	public ChangeRulersVisibilityAction(AppController controller) {
		super(controller);
		this.appController = controller;
	}
	
	public void execute(boolean isVisible) {
		getServices().getModel().setMetadataValue("useRulers", String.valueOf(isVisible));
		appController.getAppFrame().getSettings().setUseRulersSelected(isVisible);
		appController.getModyficationController().setContentAsModified(true);
	}
}