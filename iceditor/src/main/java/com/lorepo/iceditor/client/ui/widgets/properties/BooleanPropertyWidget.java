package com.lorepo.iceditor.client.ui.widgets.properties;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.InputElement;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.ui.widgets.content.WidgetLockerController;

public class BooleanPropertyWidget extends Composite {

	private static BooleanPropertyWidgetUiBinder uiBinder = GWT
			.create(BooleanPropertyWidgetUiBinder.class);

	interface BooleanPropertyWidgetUiBinder extends
			UiBinder<Widget, BooleanPropertyWidget> {
	}
	
	@UiField HTMLPanel panel;
	@UiField InputElement valueInput;
	private final int PROPERTY_LABEL_CHILD_INDEX = 0;

	public BooleanPropertyWidget() {
		initWidget(uiBinder.createAndBindUi(this));
	}
	
	public void setName(String name) {
		Element propertyLabel = (Element) panel.getElement().getChild(PROPERTY_LABEL_CHILD_INDEX);
		propertyLabel.setInnerHTML(name);
	}
	
	public void setValue(boolean value) {
		this.valueInput.setChecked(value);
	}
	
	public boolean getValue() {
		return this.valueInput.isChecked();
	}

	public void setListener(final BooleanPropertyChangeListener listener) {
		Event.sinkEvents(this.valueInput, Event.ONCHANGE | Event.FOCUSEVENTS);
		Event.setEventListener(this.valueInput, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCHANGE == event.getTypeInt()) {
					if (listener != null) {
						listener.onChange(getValue());
					}
				} else if (Event.ONFOCUS == event.getTypeInt()) {
					WidgetLockerController.disableKeysAction();
				} else if (Event.ONBLUR == event.getTypeInt()) {
					WidgetLockerController.enableKeysAction();
				}
			}
		});
	}
}
