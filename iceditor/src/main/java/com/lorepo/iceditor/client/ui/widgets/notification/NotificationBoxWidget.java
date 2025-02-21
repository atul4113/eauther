package com.lorepo.iceditor.client.ui.widgets.notification;

import static com.google.gwt.query.client.GQuery.$;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.AnchorElement;
import com.google.gwt.query.client.Function;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;

public class NotificationBoxWidget extends Composite {

	private static NotificationBoxWidgetUiBinder uiBinder = GWT
			.create(NotificationBoxWidgetUiBinder.class);

	interface NotificationBoxWidgetUiBinder extends UiBinder<Widget, NotificationBoxWidget> {
	}
	
	@UiField HTMLPanel panel;
	@UiField AnchorElement closeButton;
	@UiField AnchorElement plainCloseButton;
	@UiField AnchorElement notShowButton;
	
	private String messageId;
	private boolean shouldSetPortalMessageCookie = false;
	
	public NotificationBoxWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		
		$(getRootElement()).css("display", "block");
		
	}
	
	private void attachClickEvent(AnchorElement el, EventListener listener){
		Event.sinkEvents(el, Event.ONCLICK);
		Event.setEventListener(el, listener);
	}
	
	public void setListener(final NotificationsWidget notificationFactory) {
		
		final NotificationBoxWidget self = this;
		
		EventListener plainClose = new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				notificationFactory.removeMessage(self);
				if (shouldSetPortalMessageCookie) {
					setPortalMessageCookie();
				}
			}
		};
		attachClickEvent(closeButton, plainClose);
		attachClickEvent(plainCloseButton, plainClose);
		attachClickEvent(notShowButton,  new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				notificationFactory.removeMessage(self);
				if (messageId != null) {
					NotificationsCookies.setForLesson(messageId);
				}
			}
		});

	}
	public void setMessage(String message) {
		$(getRootElement()).find("span").html(message);
	}
	
	private void setButtonText(String btn_class, String text) {
		$(getRootElement()).find("."+btn_class).html(text);
	}
	
	public void setClosable(boolean isClosable, boolean isPermanentlyClosable) {
		if (isClosable) {
			panel.addStyleName("closeable");
			if (isPermanentlyClosable){
				setButtonText("plainCloseNotificationBtn", DictionaryWrapper.get("notification_plainCloseButton"));
				setButtonText("notShowNotificationBtn", DictionaryWrapper.get("notification_notShowButton"));
			} else {
				$(getRootElement()).find(".plainCloseNotificationBtn").remove();
				$(getRootElement()).find(".notShowNotificationBtn").remove();
			}
		} else {
			$(getRootElement()).find(".closeNotificationBtn").remove();
			$(getRootElement()).find(".plainCloseNotificationBtn").remove();
			$(getRootElement()).find(".notShowNotificationBtn").remove();
		}
	}
	
	public void setShowOnceOnPortal() {
		shouldSetPortalMessageCookie = true;
	}
	
	public void setMessageId(String messageId) {
		this.messageId = messageId;
	}
	
	public String getMessageId() {
		return this.messageId;
	}
	
	private void setPortalMessageCookie () {
		if (this.messageId != null) {
			NotificationsCookies.setForPortal(this.messageId);
		}
	}
	
	private Element getRootElement() {
		return panel.getElement();
	}

	public void setType(String type) {
		panel.addStyleName(type);
	}
}
