package com.lorepo.iceditor.client.actions.api;

import java.util.Iterator;
import java.util.List;

import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.model.page.group.Group;
import com.lorepo.icplayer.client.module.api.IModuleModel;
import com.lorepo.icplayer.client.module.api.player.IContentNode;

public interface ISelectionController {

	public void selectModule(IModuleModel module);
	public void selectSingleModule(IModuleModel module);
	public void deselectModule(IModuleModel module);
	public Iterator<IModuleModel> getSelectedModules();
	public IContentNode getSelectedContent();
	public void setContentNode(IContentNode node);
	public void clearSelection();
	public void addModule(IModuleModel module);
	public void clearSelectedModules();
	public Group getSelectedGroupOfModules();
	public void addGroupedModules(String pageId, Group group);
	public List<Group> getPageGroups(String id);
	public Object getGroupById(Page currentPage, String name);
	public void removeGroup(String id, Iterator<IModuleModel> modules);
	public Group findGroup(IModuleModel module);
	List<IModuleModel> getSelectedModulesList();
	public List<Group> getSelectedGroups();
	void clearSelectedGroups();
}
