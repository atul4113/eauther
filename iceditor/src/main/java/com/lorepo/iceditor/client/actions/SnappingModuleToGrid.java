package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.controller.AppController;

public class SnappingModuleToGrid extends AbstractPageAction {
	private AppController appController;
	
	public SnappingModuleToGrid(AppController controller) {
		super(controller);
		this.appController = controller;
	}
	
	public void execute(boolean shouldSnappingToGrid) {
		getServices().getModel().setMetadataValue("snapToGrid", String.valueOf(shouldSnappingToGrid));
		appController.getAppFrame().getSettings().setGridSnappingSelected(shouldSnappingToGrid);
		appController.getModyficationController().setContentAsModified(true);
	}
}
