package com.lorepo.iceditor.client.semi.responsive;

import java.util.List;

import com.lorepo.icplayer.client.model.ModuleList;
import com.lorepo.icplayer.client.model.layout.Size;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.model.page.group.Group;
import com.lorepo.icplayer.client.module.api.IModuleModel;
import com.lorepo.icplayer.client.semi.responsive.SemiResponsiveStyles;


public class CopyPageLayoutTask {
	
	public void execute(Page page, String sourceLayoutID, String targetLayoutID) {	
		
		ModuleList moduleList = page.getModules();

		Size newSize = page.getSizes().get(sourceLayoutID);
		page.getSizes().put(targetLayoutID, new Size(targetLayoutID, newSize.getWidth(), newSize.getHeight()));
		
		String pageInlineStyle = page.getSemiResponsiveStyles().getInlineStyle(sourceLayoutID, targetLayoutID);
		String pageStyleClass = page.getSemiResponsiveStyles().getStyleClass(sourceLayoutID, targetLayoutID);
		page.getSemiResponsiveStyles().setInlineStyle(targetLayoutID, pageInlineStyle);
		page.getSemiResponsiveStyles().setStyleClass(targetLayoutID, pageStyleClass);
		
		for (IModuleModel module : moduleList) {
			module.copyConfiguration(sourceLayoutID);
			
			SemiResponsiveStyles styles = module.getSemiResponsiveStyles();
			String moduleInlineStyle = styles.getInlineStyle(sourceLayoutID, targetLayoutID);
			String moduleStyleClass = styles.getStyleClass(sourceLayoutID, targetLayoutID);
			styles.setInlineStyle(targetLayoutID, moduleInlineStyle);
			styles.setStyleClass(targetLayoutID, moduleStyleClass);
		}
		
		List<Group> groups = page.getGroupedModules(); 
		
		for(Group group:groups) {
			group.copyConfiguration(sourceLayoutID);
			SemiResponsiveStyles styles = group.getSemiResponsiveStyles();
			String moduleInlineStyle = styles.getInlineStyle(sourceLayoutID, targetLayoutID);
			String moduleStyleClass = styles.getStyleClass(sourceLayoutID, targetLayoutID);
			styles.setInlineStyle(targetLayoutID, moduleInlineStyle);
			styles.setStyleClass(targetLayoutID, moduleStyleClass);
		}
		
	}
	
}
