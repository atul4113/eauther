package com.lorepo.iceditor.client.ui.widgets.modals;

import static com.google.gwt.query.client.GQuery.$;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;

public class ModalQuestionBoxWidget extends Composite {

	private static ModalQuestionBoxWidgetUiBinder uiBinder = GWT
			.create(ModalQuestionBoxWidgetUiBinder.class);

	interface ModalQuestionBoxWidgetUiBinder extends
			UiBinder<Widget, ModalQuestionBoxWidget> {
	}
	
	@UiField HTMLPanel panel;

	public ModalQuestionBoxWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		updateElementsTexts();
	}

	private Element getRootElement() {
		return panel.getElement();
	}
	
	private com.google.gwt.dom.client.Element getAcceptElement() {
		return $(getRootElement()).find(".accept").get(0);
	}
	
	private com.google.gwt.dom.client.Element getDeclineElement() {
		return $(getRootElement()).find(".decline").get(0);
	}
	
	public void setMessage(String message) {
		$(getRootElement()).find("span").html(message);
	}
	
	public void setListener(final QuestionModalListener listener) {
		if (listener == null) {
			return;
		}
		
		com.google.gwt.dom.client.Element acceptElement = getAcceptElement();
		Event.sinkEvents(acceptElement, Event.ONCLICK);
		Event.setEventListener(acceptElement, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				event.preventDefault();
				event.stopPropagation();
				
				listener.onAccept();
			}
		});
		
		com.google.gwt.dom.client.Element declineElement = getDeclineElement();
		Event.sinkEvents(declineElement, Event.ONCLICK);
		Event.setEventListener(declineElement, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				event.preventDefault();
				event.stopPropagation();
				
				listener.onDecline();
			}
		});
	}
	
	public void updateElementsTexts() {
		$(getRootElement()).find("a.accept").text(DictionaryWrapper.get("confirm_yes").toUpperCase());
		$(getRootElement()).find("a.decline").text(DictionaryWrapper.get("confirm_no").toUpperCase());

	}
}
