package com.lorepo.iceditor.client.actions.api;

import com.google.gwt.event.shared.HandlerRegistration;
import com.lorepo.iceditor.client.controller.Handlers;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationsWidget;
import com.lorepo.icplayer.client.model.Content;

public interface IActionService {
	public IAppController getAppController();
	public Content getModel();
	public IAppView getAppView();
	public IThemeController getThemeController();
	public IServerService getServerService();
	public ISelectionController getSelectionController();
	public IClipboard getClipboard();
	public void showMessage(String string);
	public void registerHandler(Handlers key, HandlerRegistration handler);
	public void removeHandler(Handlers key);
	public NotificationsWidget getNotifiacatonFactory();
	public void validatePageLimit();
}
