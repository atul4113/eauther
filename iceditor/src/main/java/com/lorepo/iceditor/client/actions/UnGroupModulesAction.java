package com.lorepo.iceditor.client.actions;

import java.util.Iterator;
import java.util.List;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.icplayer.client.model.page.group.Group;
import com.lorepo.icplayer.client.module.api.IModuleModel;

public class UnGroupModulesAction extends AbstractPageAction{

	private AppController controller;
	public UnGroupModulesAction(AppController controller) {
		super(controller);
		this.controller = controller;
	}

	@Override
	public void execute() {
		Iterator<IModuleModel> modules = getSelectedModules();
		
		List<Group> groups = getSelectedGroups();
		for(Group group : groups) {
			if(group != null) {

				group.closeGroupPropertyProvider();
	
				getServices().getSelectionController().removeGroup(getSelectedPage().getId(), modules);
				getServices().getAppController().getAppFrame().getPresentation().removeGroupModules(group);
				controller.getCurrentPage().getGroupedModules().remove(group);
				refreshModulesFromGroup(group);
			}
		}
		getServices().getSelectionController().clearSelection();
		getServices().getAppController().getModyficationController().setModified(true);
		getServices().getAppController().getAppFrame().getProperties().clear();
		getServices().getSelectionController().clearSelectedGroups(); 
		saveUndoState();
	}
}