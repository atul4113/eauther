package com.lorepo.iceditor.client.ui.widgets.properties;

public class ButtonPropertyBuilder {
	private final String name;
	private String text;
	private ButtonPropertyClickListener listener;
	
	public ButtonPropertyBuilder(String name) {
		this.name = name;
	}
	
	public ButtonPropertyBuilder text(String text) {
		this.text = text;
		
		return this;
	}
	
	public ButtonPropertyBuilder listener(ButtonPropertyClickListener listener) {
		this.listener = listener;
		
		return this;
	}
	
	public ButtonPropertyWidget build() {
		ButtonPropertyWidget widget = new ButtonPropertyWidget();
		widget.setName(name);
		
		if (text != null) {
			widget.setText(text);
		}
		
		widget.setListener(listener);
		
		return widget;
	}
}
