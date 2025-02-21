package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.icplayer.client.module.api.IModuleModel;

public class UIShowModuleDefaultPropertyEditorAction extends AbstractAction{
	
	public UIShowModuleDefaultPropertyEditorAction(AppController controller) {
		super(controller);
	}

	public void execute(IModuleModel module) {
		getServices().getAppController().getAppFrame().getProperties().showModuleDefaultPropertyEditor(module);
	}
}