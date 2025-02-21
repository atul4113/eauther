package com.lorepo.iceditor.client.actions;

import java.util.Iterator;

import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.widgets.content.PresentationWidget;
import com.lorepo.icplayer.client.module.api.IModuleModel;

public class UnlockModuleAction extends AbstractPageAction{
	public UnlockModuleAction(AppController controller) {
		super(controller);
	}

	@Override
	public void execute() {
		IAppController appController = getServices().getAppController();
		PresentationWidget presentation = appController.getAppFrame().getPresentation();
		Iterator<IModuleModel> modules = getSelectedModules();

		while(modules.hasNext()){
			IModuleModel module = modules.next();
			module.lock(false);
		}

		presentation.refreshView();
		appController.getModyficationController().setModified(true);
		saveUndoState();
	}

	public void execute(IModuleModel module) {
		module.lock(false);

		IAppController appController = getServices().getAppController();

		appController.getAppFrame().getPresentation().refreshView();
		appController.getModyficationController().setModified(true);
		saveUndoState();
	}
}
