package com.lorepo.iceditor.client.actions;

import java.util.Iterator;
import java.util.List;

import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.widgets.content.PresentationWidget;
import com.lorepo.iceditor.client.ui.widgets.utils.PresentationUtils;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.model.page.group.Group;
import com.lorepo.icplayer.client.module.api.IModuleModel;
import com.lorepo.icplayer.client.module.api.player.IContentNode;

public abstract class AbstractPageAction extends AbstractAction{

	public AbstractPageAction(AppController controller){
		super(controller);
	}
	
	protected Iterator<IModuleModel> getSelectedModules(){
		return getServices().getSelectionController().getSelectedModules();
	}
	
	protected Group getSelectedGroupOfModules() {
		return getServices().getSelectionController().getSelectedGroupOfModules();
	}

	protected List<Group> getSelectedGroups() {
		return getServices().getSelectionController().getSelectedGroups();
	}

	protected IModuleModel getFirstSelectedModule(){
		Iterator<IModuleModel> modules = getServices().getSelectionController().getSelectedModules();

		return modules.hasNext() ? modules.next() : null;
	}
	
	
	public Page getSelectedPage(){
		IContentNode node = getServices().getAppController().getSelectionController().getSelectedContent();
		
		return node instanceof Page ? (Page) node : null;
	}
	
	public void saveUndoState() {
		IAppController appController = getServices().getAppController();

		appController.getUndoManager().add(appController.getCurrentPage().toXML());
	}
	
	void refreshModulesFromGroup(Group group) {
		PresentationWidget presentation = getServices().getAppController().getAppFrame().getPresentation();
		
		if (!group.isEmpty()) {
			presentation.refreshView();
			PresentationWidget.adjustSelectionBox(true);

			PresentationUtils.hideModuleSelectors();
		}
	}
}
