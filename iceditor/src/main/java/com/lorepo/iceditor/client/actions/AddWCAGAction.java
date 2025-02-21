package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.actions.ActionFactory.ActionType;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.widgets.content.WidgetLockerController;

public class AddWCAGAction extends AbstractAction{
	
	public AddWCAGAction(AppController controller) {
		super(controller);
	}
	
	@Override
	public void execute() {
		if (WidgetLockerController.isVisible()) {
			return;
		}
		
		AppFrame appFrame = getServices().getAppController().getAppFrame();
		getActionFactory().getAction(ActionType.loadMissingWCAGProperties).execute();
		appFrame.getAddWCAG().show();
		WidgetLockerController.show();
	}

}
