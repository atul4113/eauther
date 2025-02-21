package com.lorepo.iceditor.client.actions;

import java.util.List;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.ModuleList;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.model.page.group.Group;
import com.lorepo.icplayer.client.module.api.IModuleModel;

public class ChangePageSemiResponsiveLayoutID extends AbstractAction {

	public ChangePageSemiResponsiveLayoutID(AppController controller) {
		super(controller);
	}
	
	@Override
	public void execute() {
		Page page = this.getCurrentPage();
		if (page == null) {
			return;
		}
		
		List<Group> groups = page.getGroupedModules();
		ModuleList modulesList = page.getModules();
		Content model = this.getModel();
		
		String actualLayoutID = model.getActualSemiResponsiveLayoutID();
		
		for(Group group : groups) {
			group.setSemiResponsiveLayoutID(actualLayoutID);
		}

		for(IModuleModel module : modulesList) {
			module.setSemiResponsiveLayoutID(actualLayoutID);
		}
	
		page.setSemiResponsiveLayoutID(actualLayoutID);
	}
}
