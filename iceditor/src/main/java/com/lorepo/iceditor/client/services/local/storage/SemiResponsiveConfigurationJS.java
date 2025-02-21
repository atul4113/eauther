package com.lorepo.iceditor.client.services.local.storage;

import java.util.List;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArrayString;
import com.lorepo.iceditor.client.semi.SemiResponsiveConfiguration;
import com.lorepo.icf.utils.JavaScriptUtils;

public class SemiResponsiveConfigurationJS extends JavaScriptObject implements SemiResponsiveConfiguration {
	protected SemiResponsiveConfigurationJS() {};
	
	public final native int length() /*-{
		return Object.keys(this).length;
	}-*/;
	
	public final List<String> keys() {
		return JavaScriptUtils.convertJsArrayToArrayList(this.getKeys());
	}
	
	public final native int getThreshold(String layoutID) /*-{
		return this[layoutID]["threshold"];
	}-*/;
	
	public final native String getName(String layoutID) /*-{
		return this[layoutID]["name"];
	}-*/;
	
	private final native JsArrayString getKeys() /*-{
		return Object.keys(this);
	}-*/;
}
