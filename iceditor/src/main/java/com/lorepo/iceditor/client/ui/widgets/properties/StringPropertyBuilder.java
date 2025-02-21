package com.lorepo.iceditor.client.ui.widgets.properties;

public class StringPropertyBuilder {
	private final String name;
	private final String value;
	private StringPropertyChangeListener listener;
	
	public StringPropertyBuilder(String name, String value) {
		this.name = name;
		this.value = value;
	}
	
	public StringPropertyBuilder listener(StringPropertyChangeListener listener) {
		this.listener = listener;
		
		return this;
	}
	
	public StringPropertyWidget build() {
		StringPropertyWidget widget = new StringPropertyWidget();
		widget.setName(name);
		widget.setValue(value);
		widget.setListener(listener);
		
		return widget;
	}
}
