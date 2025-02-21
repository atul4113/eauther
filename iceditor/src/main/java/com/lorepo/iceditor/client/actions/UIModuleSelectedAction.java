package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.actions.api.ISelectionController;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.icplayer.client.module.api.IModuleModel;

/**
 * Action used when user selects module and we want to show selection
 * for all modules related (via grouping) with it.
 */
public class UIModuleSelectedAction extends AbstractAction{
	
	public UIModuleSelectedAction(AppController controller) {
		super(controller);
	}

	public void execute(IModuleModel module, boolean clearSelection) {
		ISelectionController controller = getServices().getSelectionController();

		if (clearSelection) {
			controller.clearSelectedModules();
		}

		controller.selectModule(module);
	}
}