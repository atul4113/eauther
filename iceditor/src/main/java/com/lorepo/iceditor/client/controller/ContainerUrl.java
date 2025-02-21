package com.lorepo.iceditor.client.controller;

public class ContainerUrl {
	private String contentURL = "";
	private String nextURL = "/";
	private String previewURLInNewTab = "";
	private String abandonUrl = "";
	private String previewUrl = ""; 
	private String favouriteModulesURL = "/save_favourite_modules";
	
	public ContainerUrl() {
		
	}
	
	public void setContentURL(String contentURL) {
		this.contentURL = contentURL; 
	}
	
	public void setNextURL(String nextURL) {
		this.nextURL = nextURL; 
	}
	
	public void setPreviewURLInNewTab(String previewURLInNewTab) {
		this.previewURLInNewTab = previewURLInNewTab; 
	}
	
	public void setAbandonUrl(String abandonUrl) {
		this.abandonUrl = abandonUrl; 
	}
	
	public void setPreviewUrl(String previewUrl) {
		this.previewUrl = previewUrl;  
	}
	
	public void setFavouriteModulesURL(String favouriteModulesURL) {
		this.favouriteModulesURL = favouriteModulesURL;
	}
	
	public String getContentURL() {
		return contentURL; 
	}
	
	public String getNextURL() {
		return nextURL; 
	}
	
	public String getAbandonUrl() {
		return abandonUrl; 
	}
	
	public String getPreviewURLInNewTab() {
		return previewURLInNewTab; 
	}
	
	public String getPreviewUrl() {
		return previewUrl; 
	}
	
	public String getFavouriteModulesURL() {
		return favouriteModulesURL;
	}
	
	
}
