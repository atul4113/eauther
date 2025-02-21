package com.lorepo.iceditor.client.actions.api;

import com.lorepo.iceditor.client.actions.api.IServerService.IRequestListener;
import com.lorepo.icplayer.client.model.page.group.Group;
import com.lorepo.icplayer.client.module.api.IModuleModel;

public interface IPageEditor {

	public void savePage();
	public void savePage(IRequestListener ireql);
	public int getPageHeight();
	public void reloadPage();
	void setGrid(boolean enable, int gridSize);
	public void groupModules(Group group, boolean isPageToSave);
	public void unGroupSelection(IModuleModel moduleModel);
	public void setModifiedFlag(boolean flag);
	public void saveUndoState();
	public void undo();
	public void redo();
	public void showSelectedWidgetModuleInEditor(String moduleID);	
	public void hideSelectedWidgetModuleInEditor(String moduleID);
}
