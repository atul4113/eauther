package com.lorepo.iceditor.client.ui.widgets.utils;

public class PresentationUtils {
	public static native void hideModuleSelectors() /*-{
		if(typeof $wnd.iceHideModuleSelectors == 'function') {
			$wnd.iceHideModuleSelectors();	
		}
	}-*/;
}
