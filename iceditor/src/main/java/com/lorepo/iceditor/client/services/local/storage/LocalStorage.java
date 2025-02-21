package com.lorepo.iceditor.client.services.local.storage;

import com.google.gwt.core.client.JavaScriptObject;

public class LocalStorage {
	
	public static native void write(String pageXML, String pageIcon, String isReportable, JavaScriptObject semiResponsiveConfiguration)  /*-{
		if(typeof(Storage) != "undefined"){
			localStorage.page = pageXML;
			localStorage.pageIcon = pageIcon;
			localStorage.pageIsReportable = isReportable;
			localStorage.semiResponsiveConfiguration = JSON.stringify(semiResponsiveConfiguration);
		}
	}-*/;
	
	public static native String readPageXml()  /*-{
			if (typeof(Storage) == "undefined") {
				return null;
		}
			
		return localStorage.page;
	}-*/; 

	public static native String readPageIcon()  /*-{
			if (typeof(Storage) == "undefined") {
				return null;
		}
	
		return localStorage.pageIcon;
	}-*/; 

	public static native String readPageIsReportable()  /*-{
			if (typeof(Storage) == "undefined") {
				return true;
		}
	
		return localStorage.pageIsReportable;
	}-*/; 

	public static native SemiResponsiveConfigurationJS readSemiResponsiveConfiguration () /*-{
		if (typeof(Storage) == "undefined") {
			return {};
		}
		
		return JSON.parse(localStorage.semiResponsiveConfiguration);
	}-*/;
}
