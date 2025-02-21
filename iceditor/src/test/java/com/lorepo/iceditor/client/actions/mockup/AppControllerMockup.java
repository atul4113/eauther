package com.lorepo.iceditor.client.actions.mockup;

import java.util.Collection;
import java.util.HashMap;

import com.lorepo.iceditor.client.actions.ActionFactory;
import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.actions.api.ISelectionController;
import com.lorepo.iceditor.client.actions.api.IServerService.IRequestListener;
import com.lorepo.iceditor.client.controller.ContentModyficationController;
import com.lorepo.iceditor.client.controller.IUndoManager;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.dlg.ModuleInfo;
import com.lorepo.icf.utils.ILoadListener;
import com.lorepo.icplayer.client.model.addon.AddonDescriptor;
import com.lorepo.icplayer.client.model.addon.AddonEntry;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.api.player.IChapter;

public class AppControllerMockup implements IAppController {

	private Page currentPage;
	private String	contentURL;
	
	public AppControllerMockup(Content content){
	}
	
	
	@Override
	public void close() {
	}

	@Override
	public void abandon() {
	}

	@Override
	public void saveContent() {
	}

	@Override
	public void switchToPage(Page page, boolean isPageSelect) {

		currentPage = page;
	}

	@Override
	public Page getCurrentPage() {
		return currentPage;
	}


	@Override
	public void addAddon(AddonDescriptor descriptor) {
		// TODO Auto-generated method stub
		
	}
	

	@Override
	public void refreshStyles(String style) {
		// TODO Auto-generated method stub
		
	}


	@Override
	public void setThemeURL(String themeUrl, ILoadListener l) {
		// TODO Auto-generated method stub
		
	}


	@Override
	public String getAddonURL(String addonId) {
		// TODO Auto-generated method stub
		return null;
	}


	@Override
	public ActionFactory getActionFactory() {
		// TODO Auto-generated method stub
		return null;
	}


	@Override
	public Collection<AddonEntry> getAddonList() {
		// TODO Auto-generated method stub
		return null;
	}


	@Override
	public void switchToPage(Page page, ILoadListener listener, boolean isPageSelect) {
		currentPage = page;
		if(listener != null){
			listener.onFinishedLoading(page);
		}
	}


	@Override
	public void switchToChapter(IChapter currentNode) {
		// TODO Auto-generated method stub
	}
	
	@Override
	public void switchPageSemiResponsiveLayout(Page page, boolean isPageSelected) {
		// TODO Auto-generated method stub
	}


	@Override
	public void serverErrorMessage(int status_code, String unsuccessful_action_label) {
		// TODO Auto-generated method stub
		
	}


	@Override
	public void saveContent(IRequestListener ireql) {
		// TODO Auto-generated method stub
		
	}
	
	public void loadContent(String url){
		contentURL = url;
	}


	@Override
	public String getContentUrl() {
		return contentURL;
	}


	@Override
	public void savePage(IRequestListener ireq2) {
		// TODO Auto-generated method stub
		
	}


	@Override
	public void previewInNewTab() {
		// TODO Auto-generated method stub
		
	}


	@Override
	public void saveCurrentPageAndContent() {
		// TODO Auto-generated method stub
		
	}


	@Override
	public AppFrame getAppFrame() {
		// TODO Auto-generated method stub
		return null;
	}


	@Override
	public int getCurrentPageIndex() {
		// TODO Auto-generated method stub
		return 0;
	}


	@Override
	public String getPreviewUrl() {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public ContentModyficationController getModyficationController() {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public ISelectionController getSelectionController() {
		// TODO Auto-generated method stub
		return null;
	}


	@Override
	public IUndoManager getUndoManager() {
		// TODO Auto-generated method stub
		return null;
	}


	@Override
	public void initEditorOptions() {
		// TODO Auto-generated method stub
		
	}


	@Override
	public int getCommonPageIndex(String pageId) {
		// TODO Auto-generated method stub
		return 0;
	}


	@Override
	public void setFavouriteModules(HashMap<String, ModuleInfo> favouriteModules) {
		// TODO Auto-generated method stub
		
	}


	@Override
	public void updateFavouriteModules() {
		// TODO Auto-generated method stub
		
	}


	@Override
	public String getPreviewUrlInNewTab() {
		// TODO Auto-generated method stub
		return null;
	}


	@Override
	public boolean isAllowClose() {
		// TODO Auto-generated method stub
		return false;
	}


	@Override
	public void setIsAllowClose(boolean isClose) {
		// TODO Auto-generated method stub
		
	}


	@Override
	public boolean isSavingStyles() {
		// TODO Auto-generated method stub
		return false;
	}


	@Override
	public void setIsSavingStyles(boolean isSavingStyles) {
		// TODO Auto-generated method stub
		
	}


}
