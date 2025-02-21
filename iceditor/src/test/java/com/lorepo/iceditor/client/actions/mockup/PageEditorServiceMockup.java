package com.lorepo.iceditor.client.actions.mockup;

import com.lorepo.iceditor.client.actions.api.IPageEditor;
import com.lorepo.iceditor.client.actions.api.IServerService.IRequestListener;
import com.lorepo.icplayer.client.model.page.group.Group;
import com.lorepo.icplayer.client.module.api.IModuleModel;


public class PageEditorServiceMockup implements IPageEditor{

	@Override
	public void savePage() {
	}

	@Override
	public int getPageHeight() {
		// TODO Auto-generated method stub
		return 0;
	}

	@Override
	public void reloadPage() {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void setGrid(boolean enable, int gridSize) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void unGroupSelection(IModuleModel moduleModel) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void setModifiedFlag(boolean flag) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void undo() {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void redo() {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void saveUndoState() {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void savePage(IRequestListener ireql) {
		// TODO Auto-generated method stub
		
	}
	
	@Override
	public void hideSelectedWidgetModuleInEditor(String moduleID) {
		
	}
	
	@Override
	public void showSelectedWidgetModuleInEditor(String moduleID) {
		
	}
	
	@Override
	public void groupModules(Group group, boolean isPageToSave) {

	}
}
