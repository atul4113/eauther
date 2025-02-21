package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.widgets.modules.ModulesWidget;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.api.IModuleModel;

public class MoveModuleUpAction extends AbstractPageAction{
	public MoveModuleUpAction(AppController controller) {
		super(controller);
	}

	@Override
	public void execute() {
		IModuleModel module = getFirstSelectedModule();
		if (module == null) {
			return;
		}
		
		IAppController appController = getServices().getAppController();
		AppFrame appFrame = appController.getAppFrame();
		ModulesWidget modules = appFrame.getModules();
		Page selectedPage = getSelectedPage();
		
		selectedPage.getModules().moveModuleUp(module);
		modules.setPage(selectedPage);
		modules.setModule(module);
		appFrame.getPresentation().refreshView();
		appFrame.getPresentation().setModule(module);
		appController.getUndoManager().add(selectedPage.toXML());
	}
}
