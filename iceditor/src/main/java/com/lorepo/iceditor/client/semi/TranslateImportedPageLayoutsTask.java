package com.lorepo.iceditor.client.semi;

import java.util.HashMap;
import java.util.List;
import java.util.Set;

import com.lorepo.icplayer.client.model.layout.PageLayout;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.model.page.group.Group;
import com.lorepo.icplayer.client.module.api.IModuleModel;

public class TranslateImportedPageLayoutsTask {
	
	public Page execute(SemiResponsiveConfiguration importedPageConfiguration, Page pageToSync, Set<PageLayout> actualConfiguration) {
		HashMap<String, String> translationMap = this.createTranslationMap(importedPageConfiguration, actualConfiguration);
		
		for(IModuleModel module : pageToSync.getModules()) {
			module.translateSemiResponsiveIDs(translationMap);
		}
		
		for(Group group: pageToSync.getGroupedModules()) {
			group.translateSemiResponsiveIDs(translationMap);
		}
		
		pageToSync.translateSemiResponsiveIDs(translationMap);
		
		return pageToSync;
	}
	
	private HashMap<String, String> createTranslationMap(SemiResponsiveConfiguration importedPageConfiguration, Set<PageLayout> actualConfiguration) {
		HashMap<String, String> translationMap = new HashMap<String, String>();
		
		List<String> keys = importedPageConfiguration.keys();
		for(String key : keys) {
			String importedName = importedPageConfiguration.getName(key);
			int importedThreshold = importedPageConfiguration.getThreshold(key);
			
			for(PageLayout pageLayout : actualConfiguration) {
				if (pageLayout.getID().compareTo(key) == 0) {
					continue;
				}
				
				if (pageLayout.getName().compareTo(importedName) == 0 || pageLayout.getThreshold() == importedThreshold) {
					translationMap.put(key, pageLayout.getID());
					break;
				}
			}
		}
		
		return translationMap;
	}
}
