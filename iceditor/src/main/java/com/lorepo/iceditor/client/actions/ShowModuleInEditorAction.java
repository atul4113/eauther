package com.lorepo.iceditor.client.actions;

import java.util.Iterator;
import java.util.List;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.widgets.content.PresentationWidget;
import com.lorepo.icplayer.client.model.page.group.Group;
import com.lorepo.icplayer.client.module.api.IModuleModel;

public class ShowModuleInEditorAction extends ModulesVisibilityBasicOperations{
	public ShowModuleInEditorAction(AppController controller) {
		super(controller);
	}

	@Override
	public void execute() {
		PresentationWidget presentation = getServices().getAppController().getAppFrame().getPresentation();
		Iterator<IModuleModel> modules = getSelectedModules();

		while (modules.hasNext()) {
			IModuleModel module = modules.next();
			module.setModuleInEditorVisibility(true);
		}
		setGroupInEditorVisibility();
		presentation.refreshView();
		notifyEditorPageAboutModifyingModulesList();
		saveUndoState();
	}

	public void execute(IModuleModel module) {
		module.setModuleInEditorVisibility(true);
		setGroupInEditorVisibility(); 
		getServices().getAppController().getAppFrame().getPresentation().refreshView();
		notifyEditorPageAboutModifyingModulesList();
		saveUndoState();
	}
	
	private void setGroupInEditorVisibility() {
		List<Group> goups = getSelectedPage().getGroupedModules(); 
		for(Group group : goups) {
			group.setModuleInEditorVisibility(group.isVisibleModules());
		}
	}
}
