package com.lorepo.iceditor.client.ui.widgets.modals;

import static com.google.gwt.query.client.GQuery.$;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.SpanElement;
import com.google.gwt.dom.client.TextAreaElement;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;

public class ImageAltTextWidget extends Composite {
	private static ImageAltTextWidgetUiBinder uiBinder = GWT
			.create(ImageAltTextWidgetUiBinder.class);

	interface ImageAltTextWidgetUiBinder extends
			UiBinder<Widget, ImageAltTextWidget> {
	}
	
	@UiField HTMLPanel panel;
	@UiField SpanElement title;
	@UiField TextAreaElement altText;
	@UiField SpanElement altTextLabel;
	
	public ImageAltTextWidget(String value) {
		initWidget(uiBinder.createAndBindUi(this));
		this.updateElementsTexts(value);
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
	
	public void setFocus() {
		altText.focus();
	}
	
	public String getValue() {
		return this.altText.getValue();
	}
	
	public void updateElementsTexts(String value) {
		this.getAcceptElement().setInnerText(DictionaryWrapper.get("ok").toUpperCase());
		this.getDeclineElement().setInnerText(DictionaryWrapper.get("cancel").toUpperCase());
	
		this.altTextLabel.setInnerText(DictionaryWrapper.get("alternative_text"));
		this.title.setInnerText(DictionaryWrapper.get("edit_alternative_text"));
		this.altText.setValue(value);	
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
}
