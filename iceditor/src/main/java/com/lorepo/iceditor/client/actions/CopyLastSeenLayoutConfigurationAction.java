package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.semi.responsive.SemiResponsiveModificationsHistory;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.ModuleList;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.api.IModuleModel;

public class CopyLastSeenLayoutConfigurationAction extends AbstractAction {
	
	private Page page;
	
	public CopyLastSeenLayoutConfigurationAction(AppController controller) {
		super(controller);
	}

	@Override
	public void execute() {
		this.page = this.getCurrentPage();
		
		if (this.page == null) {
			return;
		}
		
		Content content = this.getModel();

		String actualSemiResponsiveID = content.getActualSemiResponsiveLayoutID();
		String pageID = this.page.getId();
		
		boolean wasPageAdded = SemiResponsiveModificationsHistory.wasPageAdded(pageID);
		boolean wasLayoutAdded = SemiResponsiveModificationsHistory.wasAdded(actualSemiResponsiveID);
		boolean wasLayoutVisited = SemiResponsiveModificationsHistory.layoutWasVisited(pageID, actualSemiResponsiveID);
		
		boolean pageWasNotAddedAndLayoutWasAddedButNotVisited = !wasPageAdded && wasLayoutAdded && !wasLayoutVisited;
		boolean pageWasAddedAndLayoutNotVisited = wasPageAdded && !wasLayoutVisited;

		if (pageWasNotAddedAndLayoutWasAddedButNotVisited || pageWasAddedAndLayoutNotVisited) {
			String lastSeenLayout = SemiResponsiveModificationsHistory.getLastSeen(pageID);
			if (lastSeenLayout == null) {
				return;
			}
			
			this.copyPageModulesConfiguration(lastSeenLayout);
			this.page.copyConfiguration(lastSeenLayout);
		}
	}

	private void copyPageModulesConfiguration(String lastSeenLayout) {
		ModuleList moduleList = page.getModules();

		for (IModuleModel module : moduleList) {
			module.copyConfiguration(lastSeenLayout);
		}
	}
}
