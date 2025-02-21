package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.api.IModuleModel;

public class BringToFrontModuleAction extends AbstractPageAction{
	public BringToFrontModuleAction(AppController controller) {
		super(controller);
	}

	@Override
	public void execute() {
		IModuleModel module = getFirstSelectedModule(); 
		if (module == null) {
			return;
		}

		AppFrame appFrame = getServices().getAppController().getAppFrame();
		Page selectedPage = getSelectedPage();
		
		selectedPage.getModules().bringToFrontModule(module);
		appFrame.getModules().setPage(selectedPage);
		appFrame.getModules().setModule(module);
		appFrame.getPresentation().refreshView();
		appFrame.getPresentation().setModule(module);
		
		getServices().getAppController().getUndoManager().add(selectedPage.toXML());
	}
}