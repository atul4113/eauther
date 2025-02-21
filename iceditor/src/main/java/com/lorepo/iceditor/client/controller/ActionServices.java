package com.lorepo.iceditor.client.controller;

import java.util.HashMap;
import java.util.Map;

import com.google.gwt.event.shared.HandlerRegistration;
import com.lorepo.iceditor.client.actions.api.IActionService;
import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.actions.api.IAppView;
import com.lorepo.iceditor.client.actions.api.IClipboard;
import com.lorepo.iceditor.client.actions.api.ISelectionController;
import com.lorepo.iceditor.client.actions.api.IServerService;
import com.lorepo.iceditor.client.actions.api.IThemeController;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationMessageID;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationType;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationsWidget;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.Content;

public class ActionServices implements IActionService {

	private AppController appController;
	private ServerService serverService;
	private Clipboard	clipboard = new Clipboard();
	private Map<Handlers, HandlerRegistration> handlerRegistry;
	
	public ActionServices(AppController application){
		this.appController = application;

		serverService = new ServerService();
		serverService.setAppController(this.appController);

		handlerRegistry = new HashMap<Handlers, HandlerRegistration>();
	}
	
	
	@Override
	public IAppController getAppController() {
		return appController;
	}


	@Override
	public Content getModel() {
		return appController.getModel();
	}


	@Override
	public IServerService getServerService() {
		return serverService;
	}


	@Override
	public IThemeController getThemeController() {
		return appController.getTheme();
	}


	@Override
	public void showMessage(String text) {
		appController.getAppFrame().showMessage(text);
	}

	@Override
	public ISelectionController getSelectionController() {
		return appController.getSelectionController();
	}


	@Override
	public IClipboard getClipboard() {
		return clipboard;
	}


	@Override
	public IAppView getAppView() {
		return appController.getAppFrame();
	}

	@Override
	public void registerHandler(Handlers key, HandlerRegistration handler) {
		handlerRegistry.put(key, handler);
	}

	@Override
	public void removeHandler(Handlers key) {
		HandlerRegistration handler = handlerRegistry.remove(key);
		if (handler != null) {
			handler.removeHandler();
		}
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
