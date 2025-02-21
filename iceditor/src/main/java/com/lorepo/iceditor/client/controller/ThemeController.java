package com.lorepo.iceditor.client.controller;

import com.google.gwt.user.client.Random;
import com.lorepo.iceditor.client.actions.api.IThemeController;
import com.lorepo.icf.utils.ILoadListener;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.xml.IProducingLoadingListener;
import com.lorepo.icplayer.client.xml.IXMLFactory;
import com.lorepo.icplayer.client.xml.content.ContentFactory;

public class ThemeController implements IThemeController {

	private Content themeContent;
	private AppController appController;
	
	public ThemeController(AppController application){
		this.appController = application;
	}
	

	@Override
	public String getPageUrlByNameOrFirst(String pageName) {
		
		String url = "";
		
		if(pageName == null){
			pageName = "";
		}
		
		if(themeContent != null && themeContent.getPages().getTotalPageCount() > 0){
			
			Page page;
			int index = 0;
			index = themeContent.getPages().findPageIndexByName(pageName);
			if(index >= 0){
				page = themeContent.getPages().getAllPages().get(index);
			}
			else{
				index = themeContent.getCommonPages().findPageIndexByName(pageName);
				if(index >= 0){
					page = themeContent.getCommonPages().getAllPages().get(index);
				}
				else{
					page = themeContent.getPages().getAllPages().get(0);
				}
			}

			if(page.getHref().startsWith("/")){
				url = page.getHref();
			}
			else{
				url = themeContent.getBaseUrl() + page.getHref();
			}
		}
		
		return url;
	}
	
	
	protected void setTheme(Content content){
		this.themeContent = content;
	}

	
	public void loadTheme(String themeUrl, final ILoadListener listener) {
		if(themeUrl != null && !themeUrl.isEmpty()){
			IXMLFactory contentFactory = ContentFactory.getInstanceWithAllPages();

			contentFactory.load(this.getURLWithAntiCaching(themeUrl), new IProducingLoadingListener() {
				@Override
				public void onFinishedLoading(Object obj) {
					themeContent = (Content) obj;
					listener.onFinishedLoading(ThemeController.this);
				}
				
				@Override
				public void onError(String error) {
					appController.showLoadingErrorMessage("theme", error);
				}
			});
		}
	}
	
	private String getURLWithAntiCaching(String themeUrl) {
		return themeUrl + "?" + Random.nextInt();
	}

	@Override
	public Content getTheme(){
		return themeContent;
	}
}
