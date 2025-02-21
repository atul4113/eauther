package com.lorepo.iceditor.client.controller;

import java.util.ArrayList;
import java.util.List;

import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.model.page.group.Group;
import com.lorepo.icplayer.client.module.api.IModuleModel;

public class SelectionControllerUtils {
	public static boolean isGroupInSelectedModules(Group selectedGroup, AppController controller) {
		String pageId = controller.getCurrentPage().getId();
		List<Group> groupedModules = controller.getSelectionController().getPageGroups(pageId);

		if (groupedModules == null || groupedModules.isEmpty()) {
			return false;
		}
		
		for (IModuleModel selectedModule : selectedGroup) {
			for (Group group : groupedModules) {
				if (group.contains(selectedModule)) {
					return true;
				}
			}
		}

		return false;
	}
	
	public static boolean isGroupInSelectedModules(Group selectedGroup, List<Group> groupedModules) {
		if (groupedModules == null || groupedModules.isEmpty()) {
			return false;
		}
		
		for (IModuleModel selectedModule : selectedGroup) {
			for (Group group : groupedModules) {
				if (group.contains(selectedModule)) {
					return true;
				}
			}
		}

		return false;
	}
	
	public static boolean isSelectedModuleInGroup(IModuleModel module, List<Group> groupedModules) {
		if (groupedModules == null || groupedModules.isEmpty()) {
			return false;
		}
		
		for (Group group : groupedModules) {
			if (group.contains(module)) {
				return true;
			}
		}

		return false;
	}
	
	public static boolean isModuleInAnyGroup(IModuleModel module, Page currentPage) {
		List<Group> pageGroups = currentPage.getGroupedModules();
		Group groupWithModule = getGroupWithModule(module, pageGroups);
		if(groupWithModule != null && groupWithModule.size() == 1){
			return false;
		}

		return groupWithModule != null;
	}
	
	public static Group getGroupWithModule(IModuleModel module, List<Group> groupedModules) {
		if (groupedModules == null || groupedModules.isEmpty() || module == null) {
			return null;
		}
		
		for (Group group : groupedModules) {
			if (group.contains(module)) {
				return group;
			}
		}

		return null;
	}
	
	public static boolean isSelectionInOneGroup(List<IModuleModel> selectedModules, List<Group> groupedModules) {
		List<String> groups = new ArrayList<String>();

		if (selectedModules == null || selectedModules.isEmpty()) {
			return false;
		}
		
		for (IModuleModel module : selectedModules) {
			if (isSelectedModuleInGroup(module, groupedModules)) {
				groups.add(getGroupWithModule(module, groupedModules).getId());
			} else {
				groups.add("");
			}
		}
		
		for (int i = 0; i < groups.size() - 1; i++) {
			String item = groups.get(i);
			if (!item.equals(groups.get(i + 1)) || item.equals("")) {
				return false;
			}
		}
		
		return true;
	}
}
