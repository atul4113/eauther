package com.lorepo.iceditor.client.ui.widgets.properties;

public class BooleanPropertyBuilder {
	private final String name;
	private final boolean value;
	private BooleanPropertyChangeListener listener;
	
	public BooleanPropertyBuilder(String name, boolean value) {
		this.name = name;
		this.value = value;
	}
	
	public BooleanPropertyBuilder listener(BooleanPropertyChangeListener listener) {
		this.listener = listener;
		
		return this;
	}
	
	public BooleanPropertyWidget build() {
		BooleanPropertyWidget widget = new BooleanPropertyWidget();
		widget.setName(name);
		widget.setValue(value);
		widget.setListener(listener);
		
		return widget;
	}
}
