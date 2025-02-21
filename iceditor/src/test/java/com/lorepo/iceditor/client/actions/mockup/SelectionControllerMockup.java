package com.lorepo.iceditor.client.actions.mockup;

import java.util.Iterator;
import java.util.List;

import com.lorepo.iceditor.client.actions.api.ISelectionController;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.model.page.group.Group;
import com.lorepo.icplayer.client.module.api.IModuleModel;
import com.lorepo.icplayer.client.module.api.player.IContentNode;

public class SelectionControllerMockup implements ISelectionController {

	private IContentNode selection;
	
	@Override
	public void selectModule(IModuleModel module) {
		// TODO Auto-generated method stub

	}

	@Override
	public Iterator<IModuleModel> getSelectedModules() {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public IContentNode getSelectedContent() {
		return selection;
	}

	@Override
	public void setContentNode(IContentNode node) {
		// TODO Auto-generated method stub

	}

	@Override
	public void clearSelection() {
		// TODO Auto-generated method stub

	}

	public void setSelection(IContentNode node) {
		selection = node;
	}

	@Override
	public void deselectModule(IModuleModel module) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void addModule(IModuleModel module) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void clearSelectedModules() {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void addGroupedModules(String pageId, Group group) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public List<Group> getPageGroups(String id) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public Object getGroupById(Page currentPage, String name) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public void removeGroup(String id, Iterator<IModuleModel> group) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public Group findGroup(IModuleModel module) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public void selectSingleModule(IModuleModel module) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public List<IModuleModel> getSelectedModulesList() {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public Group getSelectedGroupOfModules() {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public void clearSelectedGroups() {
		// TODO Auto-generated method stub
		
	}

	@Override
	public List<Group> getSelectedGroups() {
		// TODO Auto-generated method stub
		return null;
	}

}
