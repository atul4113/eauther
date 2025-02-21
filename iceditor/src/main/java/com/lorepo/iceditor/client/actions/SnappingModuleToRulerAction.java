package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.controller.AppController;

public class SnappingModuleToRulerAction extends AbstractPageAction {
	private AppController appController;
	
	public SnappingModuleToRulerAction(AppController controller) {
		super(controller);
		this.appController = controller;
	}

	public void execute(boolean shouldSnappingToRulers) {
		getServices().getModel().setMetadataValue("snapToRulers", String.valueOf(shouldSnappingToRulers));
		appController.getAppFrame().getSettings().setRulersSnappingSelected(shouldSnappingToRulers);
		appController.getModyficationController().setContentAsModified(true);
	}
}