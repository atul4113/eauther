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

public class StringPropertyWidget extends Composite {

	private static StringPropertyWidgetUiBinder uiBinder = GWT
			.create(StringPropertyWidgetUiBinder.class);

	interface StringPropertyWidgetUiBinder extends
			UiBinder<Widget, StringPropertyWidget> {
	}
	
	@UiField HTMLPanel panel;
	@UiField InputElement valueInput;
	private final int PROPERTY_LABEL_CHILD_INDEX = 0;

	public StringPropertyWidget() {
		initWidget(uiBinder.createAndBindUi(this));
	}
	
	public void setName(String name) {
		Element propertyLabel = (Element) panel.getElement().getChild(PROPERTY_LABEL_CHILD_INDEX);
		propertyLabel.setInnerHTML(name);
	}
	
	public void setValue(String value) {
		valueInput.setValue(value);
	}
	
	public String getValue() {
		return valueInput.getValue();
	}

	public void setListener(final StringPropertyChangeListener listener) {
		Event.sinkEvents(valueInput, Event.ONCHANGE | Event.FOCUSEVENTS);
		Event.setEventListener(valueInput, new EventListener() {
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
