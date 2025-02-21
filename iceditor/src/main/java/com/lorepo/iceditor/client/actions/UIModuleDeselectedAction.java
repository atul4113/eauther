package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.icplayer.client.module.api.IModuleModel;

public class UIModuleDeselectedAction extends AbstractAction{
	
	public UIModuleDeselectedAction(AppController controller) {
		super(controller);
	}

	public void execute(IModuleModel module) {
		getServices().getAppController().getSelectionController().deselectModule(module);
	}
}