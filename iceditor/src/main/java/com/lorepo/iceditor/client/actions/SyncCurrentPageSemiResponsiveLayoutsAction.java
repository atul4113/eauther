package com.lorepo.iceditor.client.actions;

import java.util.HashMap;
import java.util.List;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.ModuleList;
import com.lorepo.icplayer.client.model.layout.PageLayout;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.model.page.group.Group;
import com.lorepo.icplayer.client.module.api.IModuleModel;

public class SyncCurrentPageSemiResponsiveLayoutsAction extends AbstractAction {

	public SyncCurrentPageSemiResponsiveLayoutsAction(AppController controller) {
		super(controller);
	}
	
	@Override
	public void execute() {
		Page page = this.getCurrentPage();
		
		if (page == null) {
			return;
		}
		
		Content content = this.getModel();
		
		this.syncPage(page, content);
		
		if (page.hasHeader()) {
			Page header = content.getHeader(page);
			if (header != null) {
				this.syncPage(header, content);	
			}
		}
		
		if (page.hasFooter()) {
			Page footer = content.getFooter(page);
			if (footer != null) {
				this.syncPage(footer, content);	
			}
		}
	}
	
	private void syncPage(Page page, Content content) {		
		this.syncPageSizes(page, content);
		this.syncPageActualSize(page, content);
		page.syncSemiResponsiveStyles(content.getActualSemiResponsiveLayouts());
		this.syncPageModules(page, content);		
	}

	private void syncPageSizes(Page page, Content content) {
		page.syncPageSizes(content.getActualSemiResponsiveLayouts());
	}

	private void syncPageModules(Page page, Content content) {
		ModuleList moduleList = page.getModules();

		for (IModuleModel module : moduleList) {
			module.syncSemiResponsiveStyles(content.getActualSemiResponsiveLayouts());
			module.syncSemiResponsiveLayouts(content.getActualSemiResponsiveLayouts());
		}
		
		List<Group> groups = page.getGroupedModules(); 
		for(Group group : groups) {
			group.syncSemiResponsiveLayouts(content.getActualSemiResponsiveLayouts());
		}
	}
	
	private void syncPageActualSize(Page page, Content content) {
		HashMap<String, PageLayout> layouts = content.getLayouts();
		String layoutID = page.getSemiResponsiveLayoutID();
		
		if (!layouts.containsKey(layoutID)) {
			for(PageLayout pl : layouts.values()) {
				if(pl.isDefault()) {
					page.setSemiResponsiveLayoutID(pl.getID());
					break;
				}
			}
		}
		
	}
}
