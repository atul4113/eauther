package com.lorepo.iceditor.client.ui.widgets.modals;

import static com.google.gwt.query.client.GQuery.$;

import java.util.List;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.InputElement;
import com.google.gwt.dom.client.SpanElement;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;

public class AltTextWidget extends Composite {

	private static AltTextWidgetUiBinder uiBinder = GWT
			.create(AltTextWidgetUiBinder.class);

	interface AltTextWidgetUiBinder extends UiBinder<Widget, AltTextWidget> {
	}

	@UiField HTMLPanel panel;
	@UiField SpanElement title;
	@UiField SpanElement visibleTextLabel;
	@UiField InputElement visibleText;
	@UiField SpanElement altTextLabel;
	@UiField InputElement altText;
	@UiField SpanElement langTagLabel;
	@UiField InputElement langTagText;
	
	public AltTextWidget(List<String> values) {
		initWidget(uiBinder.createAndBindUi(this));
		updateElementsTexts();
		
		if (values != null) {
			fillItems(values);
		}
	}
	
	private void fillItems(List<String> values) {
		$(visibleText).val(values.get(0));
		if(values.size()>1){
			$(altText).val(values.get(1));
		}
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
	
	protected void setFocus() {
		if($(visibleText).val().length()>0 && $(altText).val().length()==0) {
			altText.focus();
		} else {
			visibleText.focus();
		}
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
	
	public String getDefinition() {
		String returnedValue = "\\alt{";
		returnedValue += $(visibleText).val();
		returnedValue += "|";
		returnedValue += $(altText).val() + "}";
		
		if ($(langTagText).val().trim().length() > 0) {
			returnedValue += "[lang ";
			returnedValue += $(langTagText).val().trim();
			returnedValue += "]";
		}
		return returnedValue;
	}
	
	public void updateElementsTexts() {
		$(getRootElement()).find("a.accept").text(DictionaryWrapper.get("ok").toUpperCase());
		$(getRootElement()).find("a.decline").text(DictionaryWrapper.get("cancel").toUpperCase());
		visibleTextLabel.setInnerText(DictionaryWrapper.get("visible_text_alt_text"));
		altTextLabel.setInnerText(DictionaryWrapper.get("alt_text_alt_text"));
		langTagLabel.setInnerText(DictionaryWrapper.get("choice_lang_attribute"));
		title.setInnerText(DictionaryWrapper.get("add_alt_text_title"));

	}

	public String getVisibleText() {
		return $(visibleText).val();
	}
	
	public String getAltText() {
		return $(altText).val();
	}
}
