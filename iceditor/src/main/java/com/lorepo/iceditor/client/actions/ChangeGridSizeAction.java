package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.controller.AppController;

public class ChangeGridSizeAction extends AbstractPageAction {
	private AppController appController;

	public ChangeGridSizeAction(AppController controller) {
		super(controller);
		this.appController = controller;
	}

	public void execute(int size) {
		getServices().getModel().setMetadataValue("gridSize", String.valueOf(size));
		appController.getAppFrame().getSettings().setGridSize(String.valueOf(size));
		appController.getModyficationController().setContentAsModified(true);
	}
}
