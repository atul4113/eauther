package com.lorepo.iceditor.client.ui.widgets.modals;

import static com.google.gwt.query.client.GQuery.$;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.InputElement;
import com.google.gwt.dom.client.SpanElement;
import com.google.gwt.event.dom.client.KeyCodes;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;

public class PromptWidget extends Composite {

	private static ModalQuestionBoxWidgetUiBinder uiBinder = GWT
			.create(ModalQuestionBoxWidgetUiBinder.class);

	interface ModalQuestionBoxWidgetUiBinder extends
			UiBinder<Widget, PromptWidget> {
	}
	
	@UiField HTMLPanel panel;
	@UiField SpanElement textBefore;
	@UiField SpanElement textAfter;
	@UiField InputElement heightValue;
	
	private String promptTextBefore = "";
	private String promptTextAfter = "";

	public PromptWidget() {
		initWidget(uiBinder.createAndBindUi(this));
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
		$(getRootElement()).find("span").get(0).setInnerText(message);
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
		
		Event.sinkEvents(heightValue, Event.ONKEYUP);
		Event.setEventListener(heightValue, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONKEYUP != event.getTypeInt()) {
					return;
				}
				
				if(event.getKeyCode() == KeyCodes.KEY_ENTER){
					event.preventDefault();
					event.stopPropagation();
					
					listener.onAccept();
					return;
				}

				event.preventDefault();
				event.stopPropagation();
				
				if(!validatePromptValue()) {
					String value = $(heightValue).val();
					$(heightValue).val(value.substring(0, value.length() - 1));
				}
			}
		});
	}
	
	private boolean validatePromptValue() {
		String promptValue = getPromptValue();

		return promptValue.matches("^(-)?[0-9]*$");
	}
	
	public String getPromptValue() {
		return $(heightValue).val();
	}
	
	public void setPromptValue(String value) {
		$(heightValue).val(value);
	}
	
	public void updateElementsTexts() {
		$(getRootElement()).find("a.accept").text(DictionaryWrapper.get("ok").toUpperCase());
		$(getRootElement()).find("a.decline").text(DictionaryWrapper.get("cancel").toUpperCase());
		if (!promptTextBefore.equals("")) {
			textBefore.setInnerText(DictionaryWrapper.get(promptTextBefore) + ": ");
		}
		if (!promptTextAfter.equals("")) {
	 		textAfter.setInnerText(promptTextAfter);
		}
	}

	public void setTextContent(String[] textContent) {
		this.promptTextBefore = textContent[0];
		this.promptTextAfter = textContent[1];
		
		updateElementsTexts();
	}
}
