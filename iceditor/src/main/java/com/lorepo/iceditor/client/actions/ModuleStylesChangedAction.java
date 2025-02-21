package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.widgets.content.PresentationWidget;

public class ModuleStylesChangedAction extends AbstractAction{
	public ModuleStylesChangedAction(AppController controller) {
		super(controller);
	}

	@Override
	public void execute() {
		IAppController appController = getServices().getAppController();
		AppFrame appFrame = appController.getAppFrame();
		PresentationWidget presentation = appFrame.getPresentation();
		
		presentation.setPropertiesWidget(appFrame.getProperties());
		presentation.refreshView();
		
		appController.getUndoManager().add(appController.getCurrentPage().toXML());
	}
}
