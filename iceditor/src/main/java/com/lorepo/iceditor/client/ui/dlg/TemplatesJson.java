package com.lorepo.iceditor.client.ui.dlg;

import com.google.gwt.core.client.JavaScriptObject;


public class TemplatesJson extends JavaScriptObject{

	public static final native TemplatesJson parse(String json) /*-{
		return eval('(' + json + ')');
	}-*/;
	
	
	public final native String getVersion() /*-{ 
   		return this.version;
	}-*/;
	
	
	public final native int getItemCount() /*-{ 
		return this.items.length;
	}-*/;


	public final native String getItemName(int index) /*-{ 
		return this.items[index].name;
	}-*/;

	public final native String getItemIcon(int index) /*-{ 
		return this.items[index].icon_url;
	}-*/;

	public final native String getThemeUrl(int index) /*-{ 
		return this.items[index].theme_url;
	}-*/;

	public final native String getCategory(int index) /*-{ 
		return this.items[index].category;
	}-*/;


	/**
	 * Protected constructor
	 */
	protected TemplatesJson(){
		
	}
	
}