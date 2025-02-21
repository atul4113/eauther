package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.icplayer.client.module.api.IModuleModel;

/**
 * Action used when user selects module and we want to show selection
 * just for that module.
 */
public class UISingleModuleSelectedAction extends AbstractAction{
	
	public UISingleModuleSelectedAction(AppController controller) {
		super(controller);
	}

	public void execute(IModuleModel module) {
		getServices().getSelectionController().selectSingleModule(module);
	}
}