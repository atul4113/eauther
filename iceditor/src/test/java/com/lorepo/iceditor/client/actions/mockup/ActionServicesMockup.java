package com.lorepo.iceditor.client.actions.mockup;

import com.google.gwt.event.shared.HandlerRegistration;
import com.lorepo.iceditor.client.actions.api.IActionService;
import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.actions.api.IAppView;
import com.lorepo.iceditor.client.actions.api.IClipboard;
import com.lorepo.iceditor.client.actions.api.ISelectionController;
import com.lorepo.iceditor.client.actions.api.IServerService;
import com.lorepo.iceditor.client.actions.api.IThemeController;
import com.lorepo.iceditor.client.controller.Clipboard;
import com.lorepo.iceditor.client.controller.Handlers;
import com.lorepo.iceditor.client.controller.ThemeController;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationMessageID;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationType;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationsWidget;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.page.Page;

public class ActionServicesMockup implements IActionService {

	private String historyToken;
	private AppControllerMockup appController;
	private Content	contentModel;
	private ServerServiceMockup serverService;
	private ThemeController		themeController;
	private IClipboard	clipboard = new Clipboard();
	private SelectionControllerMockup selectionController;
	
	
	public ActionServicesMockup(){
	
		contentModel = new Content();
		appController = new AppControllerMockup(contentModel);
		serverService = new ServerServiceMockup();
		themeController = new ThemeController(null);
		selectionController = new SelectionControllerMockup();
		
		Page page1 = new Page("Page 1", "");
		contentModel.getPages().add(page1);
		contentModel.getPages().add(new Page("Page 2", ""));
		appController.switchToPage(page1, false);
		selectionController.setSelection(page1);
	}
	
	
	@Override
	public IAppController getAppController() {
		return appController;
	}	
	
	
	public String getHistoryToken(){
		return historyToken;
	}


	@Override
	public Content getModel() {
		return contentModel;
	}


	@Override
	public IServerService getServerService() {
		return serverService;
	}


	@Override
	public IThemeController getThemeController() {
		return themeController;
	}


	@Override
	public void showMessage(String string) {
		System.out.println("ALERT: " + string);
	}

	@Override
	public ISelectionController getSelectionController() {
		return selectionController;
	}


	@Override
	public IClipboard getClipboard() {
		return clipboard;
	}


	@Override
	public IAppView getAppView() {
		return null;
	}

	@Override
	public void registerHandler(Handlers key, HandlerRegistration handler) {
	}

	@Override
	public void removeHandler(Handlers key) {
	}
	
	@Override
	public NotificationsWidget getNotifiacatonFactory(){
		return getAppController().getAppFrame().getNotifications();
	}


	@Override
	public void validatePageLimit() {
		if (getModel().isPageLimitExceeded()) {
			getNotifiacatonFactory().addUniqueMessage(DictionaryWrapper.get("to_many_pages_warning"), 
				NotificationType.warning, NotificationMessageID.too_many_pages, true);
			}
	}
}
