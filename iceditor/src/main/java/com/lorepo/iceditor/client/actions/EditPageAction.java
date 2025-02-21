package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.AppFrame;

public class EditPageAction extends AbstractPageAction{

	public EditPageAction(AppController controller) {
		super(controller);
	}

	@Override
	public void execute() {
		AppFrame appFrame = getServices().getAppController().getAppFrame();
		
		appFrame.getPresentation().refreshView();
		appFrame.getPages().refreshSelectedNode();
	}

}
