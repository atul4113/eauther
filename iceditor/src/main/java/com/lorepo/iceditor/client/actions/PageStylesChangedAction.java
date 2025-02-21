package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.controller.AppController;

public class PageStylesChangedAction extends AbstractAction{
	public PageStylesChangedAction(AppController controller) {
		super(controller);
	}

	@Override
	public void execute() {
		IAppController appController = getServices().getAppController();

		appController.getAppFrame().getPresentation().refreshView();
	}
}
