package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.controller.AppController;

public class EditChapterAction extends AbstractPageAction{

	public EditChapterAction(AppController controller) {
		super(controller);
	}

	@Override
	public void execute() {
		getServices().getAppController().getAppFrame().getPages().refreshSelectedNode();
	}
}
