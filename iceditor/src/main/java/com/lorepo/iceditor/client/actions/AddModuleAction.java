package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.widgets.content.WidgetLockerController;

public class AddModuleAction extends AbstractAction{
	public AddModuleAction(AppController controller) {
		super(controller);
	}
	
	@Override
	public void execute() {
		if (WidgetLockerController.isVisible()) {
			return;
		}

		AppFrame appFrame = getServices().getAppController().getAppFrame();
		
		appFrame.getAddModule().show();
		WidgetLockerController.show();
	}
}
