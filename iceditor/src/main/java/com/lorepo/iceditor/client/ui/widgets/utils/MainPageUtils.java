package com.lorepo.iceditor.client.ui.widgets.utils;

import com.google.gwt.dom.client.Style.Display;
import com.google.gwt.user.client.ui.Panel;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.widgets.content.WidgetLockerController;
import com.lorepo.iceditor.client.ui.widgets.modals.ModalsWidget;

public class MainPageUtils {
	public static AppFrame appFrame;
	
	public static void show(Panel panel) {
		closeAll();
		WidgetLockerController.show();
		panel.getElement().getStyle().setDisplay(Display.BLOCK);
	}
	
	public static void showWithoutLockers(Panel panel) {
		closeAll();
		panel.getElement().getStyle().setDisplay(Display.BLOCK);
		
		disableKeys();
	}
	
	private static native void disableKeys() /*-{
		$wnd.iceEditorApplication.PropertyValueHandler.disableKeysAction();
	}-*/;	
	
	private static native void closeAll() /*-{
		if(typeof $wnd.iceCloseAllMainPages == 'function') {	
			$wnd.iceCloseAllMainPages();	
		}
	}-*/;
	
	public static native void restore() /*-{
		if(typeof $wnd.iceCloseAllMainPages == 'function') {	
			$wnd.iceCloseAllMainPages();	
		}
		
		if (typeof $wnd.iceHideWidgetLocker == 'function') {
			$wnd.iceHideWidgetLocker();
		}
	}-*/;
	
	public static void updateScrollbars() {
		updatePerfectScrollbars();
	}
	
	public static void updateWidgetScrollbars(String widgetName) {
		updateWidgetPerfectScrollbars(widgetName);
	}
	
	private static native void updateWidgetPerfectScrollbars(String widgetName) /*-{
		if (typeof $wnd.iceUpdateWidgetScrollbars == 'function') {
			$wnd.iceUpdateWidgetScrollbars(widgetName);
		}
	}-*/;
	
	private static native void updatePerfectScrollbars() /*-{
		if (typeof $wnd.iceUpdateScrollbars == 'function') {
			$wnd.iceUpdateScrollbars();
		}
	}-*/;
	
	public static native void updatePageResizers() /*-{
		if (typeof $wnd.iceUpdatePageResizers == 'function') {
			$wnd.iceUpdatePageResizers();
		}
	}-*/;
	
	public static void executeOnPageSelection() {
		executeOnPageSelectionFunction();
	}
	
	private static native void executeOnPageSelectionFunction() /*-{
		if(typeof $wnd.iceOnPageSelected == 'function') {
			$wnd.iceOnPageSelected();
		}
	}-*/;
	
	public static native void executeOnHide() /*-{
		if(typeof $wnd.executeActionOnHide == 'function') {
			$wnd.executeActionOnHide();
		}
	}-*/;
	
	public static native void executeOnPreview() /*-{
		if(typeof $wnd.executeActionOnPreview == 'function') {
			$wnd.executeActionOnPreview();
		}
	}-*/;
	
	public static native void triggerApplyClick() /*-{
		$wnd.$('.mainPage:visible').find('#editorApply').trigger('click');
	}-*/;

	public static native void triggerSaveClick() /*-{
		$wnd.$('.mainPage:visible').find('#editorSave').trigger('click');
	}-*/;
	
	private static native void hideActivePanel() /*-{
		$wnd.$('.mainPage:visible').hide();
	}-*/;
	
	public static native boolean isWindowOpened(String id)/*-{
		// htmlEditorPage has id textEditorPage and vice versa
		if (id == "htmlEditorPage") {
			id = "textEditorPage";
		} else if (id == "textEditorPage") {
			id = "htmlEditorPage";
		}
		
		return $wnd.$('#' + id).is(":visible");
	}-*/;

	public static ModalsWidget getModals() {
		return appFrame.getModals();
	}
	
	public static AppFrame getAppFrame() {
		return appFrame;
	}
	
	// @param - selector e.g. #someId or .someClass
	public static native void addScrollBar(String selector)/*-{
		$wnd.iceAddScrollBar(selector);
	}-*/;
	
	public static native void updateScrollBar(String id)/*-{
		$wnd.iceUpdateWidgetScrollbars(id);
	}-*/;
}
