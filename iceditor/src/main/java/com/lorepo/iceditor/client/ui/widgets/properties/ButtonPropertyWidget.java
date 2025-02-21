package com.lorepo.iceditor.client.ui.widgets.properties;

import static com.google.gwt.query.client.GQuery.$;

import com.google.gwt.core.client.GWT;
import com.google.gwt.query.client.GQuery;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;

public class ButtonPropertyWidget extends Composite {

	private static ButtonPropertyWidgetUiBinder uiBinder = GWT
			.create(ButtonPropertyWidgetUiBinder.class);

	interface ButtonPropertyWidgetUiBinder extends
			UiBinder<Widget, ButtonPropertyWidget> {
	}
	
	@UiField HTMLPanel panel;

	public ButtonPropertyWidget() {
		initWidget(uiBinder.createAndBindUi(this));
	}
	
	public void setName(String name) {
		$(getRootElement()).find(".propertyLabel").html(name);		
	}
	
	public void setText(String text){ 
		$(getRootElement()).find(".listText").text(text);
	}

	private GQuery getButtonQueryElement() {
		return $(getRootElement()).find(".propertyValue button");
	}
	
	private Element getButtonElement() {
		return (Element) getButtonQueryElement().get(0);
	}

	private Element getRootElement() {
		return panel.getElement();
	}

	public void setListener(final ButtonPropertyClickListener listener) {
		final Element buttonElement = getButtonElement();
		
		Event.sinkEvents(buttonElement, Event.ONCLICK);
		Event.setEventListener(buttonElement, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				listener.onSelected();
			}
		});
	}
}
