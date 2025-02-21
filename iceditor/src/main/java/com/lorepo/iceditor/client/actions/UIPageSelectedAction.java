package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.widgets.utils.MainPageUtils;
import com.lorepo.icplayer.client.model.page.Page;

public class UIPageSelectedAction extends AbstractAction{
	public UIPageSelectedAction(AppController controller) {
		super(controller);
	}

	@Override
	public void execute() {
		IAppController appController = getServices().getAppController();
		AppFrame appFrame = appController.getAppFrame();
		Page page = (Page) appController.getSelectionController().getSelectedContent();

		appFrame.getPresentation().onPageSelected();

		MainPageUtils.executeOnPageSelection();

		appFrame.getProperties().setPage(page);
		appFrame.getModules().setPage(page);
		appFrame.getStyles().setPage(page);
	}
}
