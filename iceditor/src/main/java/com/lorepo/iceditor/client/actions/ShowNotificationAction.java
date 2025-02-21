package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationType;

public class ShowNotificationAction extends AbstractAction {
	
	private String text;
	private NotificationType type = NotificationType.notice;
	private boolean isClosable = false;

	public ShowNotificationAction(AppController controller) {
		super(controller);
	}
	
	public ShowNotificationAction setText(String text) {
		this.text = text;
		return this;
	}
	
	public ShowNotificationAction setType(NotificationType type) {
		this.type = type;
		return this;
	}
	
	public ShowNotificationAction setIsClosable(boolean isClosable) {
		this.isClosable = isClosable;
		return this;
	}
	
	@Override
	public void execute() {
		this.getNotifications().addMessage(this.text, this.type, this.isClosable);
	}
}
