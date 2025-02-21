package com.lorepo.iceditor.client.ui.widgets.notification;

import static com.google.gwt.query.client.GQuery.$;

import java.util.HashMap;
import java.util.Map;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.Element;
import com.google.gwt.query.client.Function;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;

public class NotificationsWidget extends Composite {
	private static NotificationsWidgetUiBinder uiBinder = GWT
			.create(NotificationsWidgetUiBinder.class);

	interface NotificationsWidgetUiBinder extends
			UiBinder<Widget, NotificationsWidget> {
	}

	@UiField HTMLPanel wrapper;

	private Map <String, NotificationBoxWidget> uniqueIDList = new HashMap<String, NotificationBoxWidget>();
	
	public NotificationsWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		
		wrapper.getElement().setId("notificationsWrapper");
	}
	
	private void addTimer (final NotificationBoxWidget notificationBox) {
		Timer timeToDelete = new Timer () {
			@Override
			public void run() {
				removeMessage(notificationBox);
			}
		};
		timeToDelete.schedule(2000);		
	}
	
	public void addMessage(String message, NotificationType type, boolean isClosable) {
		final NotificationBoxWidget notificationBox = new NotificationBoxWidget();
		
		notificationBox.setMessage(message);
		notificationBox.setClosable(isClosable, false);
		notificationBox.setType(type.toString());
		notificationBox.setListener(this);
		
		if(!isClosable)
			addTimer(notificationBox);
		
		wrapper.add(notificationBox);
	}
	
	public void removeMessage (final NotificationBoxWidget widget) {
		$(widget).slideUp(300, new Function () {
			@Override
			public void f(Element e){
				wrapper.remove(widget);
				if (widget.getMessageId() != null) {
					uniqueIDList.remove(widget.getMessageId());
				}
			}
		});
	}
	
	public void removeMessage (NotificationMessageID messageID) {
		if (uniqueIDList.containsKey(messageID.toString())){
			removeMessage(uniqueIDList.get(messageID.toString()));
		}
	}
	
	public void addUniqueMessage(String message, NotificationType type, NotificationMessageID messageID, boolean isClosable) {
		
		if (NotificationsCookies.get(messageID.toString()) != null){
			return;
		}
		if (uniqueIDList.containsKey(messageID.toString())) {
			return;
		}
		final NotificationBoxWidget notificationBox = new NotificationBoxWidget();
		
		notificationBox.setMessage(message);
		notificationBox.setClosable(isClosable, true);
		notificationBox.setType(type.toString());
		notificationBox.setMessageId(messageID.toString());
		notificationBox.setListener(this);
		
		uniqueIDList.put(messageID.toString(), notificationBox);
		wrapper.add(notificationBox);
		
		if(!isClosable) {
			addTimer(notificationBox);
		}
			
	}
	
	public void addOneTimeMessage(String message, NotificationType type, boolean isClosable, String messageId) {
		if (NotificationsCookies.get(messageId) == null) {
			NotificationBoxWidget notificationBox = new NotificationBoxWidget();

			notificationBox.setMessage(message);
			notificationBox.setClosable(isClosable, false);
			notificationBox.setShowOnceOnPortal();
			notificationBox.setType(type.toString());
			notificationBox.setListener(this);
			
			wrapper.add(notificationBox);
			
			if(!isClosable) {
				addTimer(notificationBox);
			}
			
			notificationBox.setMessageId(messageId);
		} else {
			NotificationsCookies.update(messageId);
		}
	}
	
}
