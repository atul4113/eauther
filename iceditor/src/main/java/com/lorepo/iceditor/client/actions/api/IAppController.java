package com.lorepo.iceditor.client.actions.api;

import java.util.Collection;
import java.util.HashMap;

import com.lorepo.iceditor.client.actions.ActionFactory;
import com.lorepo.iceditor.client.actions.api.IServerService.IRequestListener;
import com.lorepo.iceditor.client.controller.ContentModyficationController;
import com.lorepo.iceditor.client.controller.IUndoManager;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.dlg.ModuleInfo;
import com.lorepo.icf.utils.ILoadListener;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.model.addon.AddonDescriptor;
import com.lorepo.icplayer.client.model.addon.AddonEntry;
import com.lorepo.icplayer.client.module.api.player.IChapter;

public interface IAppController {

	public void switchToPage(Page page, boolean isPageSelect);
	public void switchToPage(Page page, ILoadListener listener, boolean isPageSelect);
	public void switchPageSemiResponsiveLayout(Page page, boolean isPageSelected);
	public void saveContent();
	public void saveContent(IRequestListener ireql);
	public void savePage(IRequestListener ireq2);
	public void close();
	public void abandon();
	public Page getCurrentPage();
	public int getCurrentPageIndex();
	public void addAddon(AddonDescriptor descriptor);
	public void refreshStyles(String style);
	public void setThemeURL(String themeURL, ILoadListener l);
	public String getAddonURL(String addonId);
	public ActionFactory getActionFactory();
	public Collection<AddonEntry> getAddonList();
	public void switchToChapter(IChapter currentNode);
	public void serverErrorMessage(int status_code, String unsuccessful_action_label);
	public String getContentUrl();
	public void previewInNewTab();
	public void saveCurrentPageAndContent();
	public AppFrame getAppFrame();
	String getPreviewUrlInNewTab();
	String getPreviewUrl(); 
	public ContentModyficationController getModyficationController();
	public ISelectionController getSelectionController();
	public IUndoManager getUndoManager();
	public void initEditorOptions();
	public int getCommonPageIndex(String pageId);
	public void setFavouriteModules(HashMap<String, ModuleInfo> favouriteModules);
	public void updateFavouriteModules();
	public boolean isAllowClose(); 
	public void setIsAllowClose(boolean isClose);
	public boolean isSavingStyles();
	public void setIsSavingStyles(boolean isSavingStyles);
}
