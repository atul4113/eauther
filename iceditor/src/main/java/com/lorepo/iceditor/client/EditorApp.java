package com.lorepo.iceditor.client;

import java.util.List;

import com.google.gwt.user.client.ui.RootLayoutPanel;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.AppFrame;

public class EditorApp{

	private AppFrame 	appPanel;
	private AppController	appController;

	public EditorApp(EditorConfig config){
		EditorLanguage.setLanguage(config.lang);
		appPanel = new AppFrame(config);
	    appController = new AppController(appPanel, config);
	    RootLayoutPanel.get().add(appPanel);
	 }

	public void load(String url) {
	    appController.loadContent(url);
	}

	public void setNextUrl(String url) {
		appController.setNextURL(url);
	}
	
	public void setPreviewUrlInNewTab(String url) {
		appController.setPreviewUrlInNewTab(url);
		appController.getAppFrame().getHeaderMenu().showPreviewInNewTabButton();
	}
	
	
	public void setPreviewUrl(String url) {
		appController.setPreviewUrl(url);
	}

	public void setAbandonUrl(String url) {
		appController.setAbandonUrl(url);
		appController.getAppFrame().getHeaderMenu().showAbandonButton();
	}

	public void setEditorTitle(String title, String subTitle){
		appController.getAppFrame().getHeader().setTitle(title);
		appController.getAppFrame().getHeader().setSubTitle(subTitle);
	}
	
	public void setLogoUrl(String url) {
		appController.getAppFrame().getHeader().setImageLogo(url);
		appController.getAppFrame().getPresentationLoading().setLoadingLogo(url);
	}
	
	public void setRenderedView(boolean shouldRender) {
		appController.getAppFrame().getHTMLEditor().setRenderedView(shouldRender);
		appController.getAppFrame().getItemsEditor().setRenderedView(shouldRender);
	}

	public void saveShouldRenderURL(String url) {
		appController.setRenderURL(url);
	}

	public void setFavouriteModules(List<String> favouriteModules) {
		appController.prepareAndSetFavouriteModules(favouriteModules);
	}

	public void saveFavouriteModulesURL(String url) {
		appController.saveFavouriteModulesURL(url);
	}
}
