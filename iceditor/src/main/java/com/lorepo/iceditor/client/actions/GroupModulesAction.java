package com.lorepo.iceditor.client.actions;

import java.util.Iterator;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.controller.SelectionControllerUtils;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationType;
import com.lorepo.icf.properties.IProperty;
import com.lorepo.icf.properties.IPropertyListener;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.model.page.group.Group;
import com.lorepo.icplayer.client.module.api.IModuleModel;


public class GroupModulesAction extends AbstractPageAction{

	private AppController controller;
	private Group group;
	
	public GroupModulesAction(AppController controller) {
		super(controller);
		this.controller = controller;
	}

	@Override
	public void execute() {
		group = new Group(controller.getCurrentPage());
		group.setId(createUniqueID());
		group.addPropertyListener(propertyListener);

		Iterator<IModuleModel> modules = getSelectedModules();
		String pageId = getSelectedPage().getId();

		if (modules.hasNext() && SelectionControllerUtils.isGroupInSelectedModules(getSelectedGroupOfModules(), controller)) {
			controller.getAppFrame().getNotifications().addMessage(DictionaryWrapper.get("module_belongs_to_group"), NotificationType.error, false);

			return;
		}

	    while(modules.hasNext()){
			group.add(modules.next());
		}
		
		if (!group.isEmpty()) {
			controller.getSelectionController().addGroupedModules(pageId, group);
			getServices().getAppController().getAppFrame().getPresentation().groupModules(group, true);
		}
		getServices().getAppController().getModyficationController().setModified(true);
		getServices().getAppController().getAppFrame().getProperties().setGroup(group);
		controller.getCurrentPage().addGroupModules(group);
		group.initGroupPropertyProvider();
		refreshModulesFromGroup(group);
		saveUndoState();
	}
	
	public String createUniqueID() {
		Page currentPage = controller.getCurrentPage();
		int iterator = 0;
		
		while(true) {
			final String name = DictionaryWrapper.get("Group") + iterator;
			if (controller.getSelectionController().getGroupById(currentPage, name) == null) {
				return name;
			}
			
			iterator++;
		}
	}
	
	private IPropertyListener propertyListener = new IPropertyListener() {
		public void onPropertyChanged(IProperty property) {
			getServices().getAppController().getModyficationController().setModified(true);
		}
	};
}