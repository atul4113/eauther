package com.lorepo.iceditor.client.ui.widgets.content;

public class WidgetLockerController {
	public static native void show() /*-{
		if(typeof $wnd.iceShowWidgetLocker == 'function') {
			$wnd.iceShowWidgetLocker();
			try{
				$wnd.iceEditorApplication.PropertyValueHandler.disableKeysAction();
			}catch(err){}	
		}
	}-*/;
	
	public static native void hide() /*-{
		if(typeof $wnd.iceHideWidgetLocker == 'function') {
			$wnd.iceHideWidgetLocker();
			$wnd.iceEditorApplication.PropertyValueHandler.enableKeysAction();
		}
	}-*/;
	
	public static native boolean isVisible() /*-{
		if(typeof $wnd.iceIsWidgetLockerVisible == 'function') {
			return $wnd.iceIsWidgetLockerVisible();	
		}
		
		return false;
	}-*/;
	
	public static native void disableKeysAction() /*-{
		$wnd.iceEditorApplication.PropertyValueHandler.disableKeysAction();
	}-*/;
	
	public static native void enableKeysAction() /*-{
		$wnd.iceEditorApplication.PropertyValueHandler.enableKeysAction();
	}-*/;
}
