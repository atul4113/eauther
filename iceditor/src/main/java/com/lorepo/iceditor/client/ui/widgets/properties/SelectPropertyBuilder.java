package com.lorepo.iceditor.client.ui.widgets.properties;

public class SelectPropertyBuilder {
	private final String name;
	private final String[] options;
	private String[] text;
	private String selectedOption;
	private SelectPropertyChangeListener listener;
	
	public SelectPropertyBuilder(String name, String[] options) {
		this.name = name;
		this.options = options;
		this.text = new String[0]; 
	}
	
	public SelectPropertyBuilder listener(SelectPropertyChangeListener listener) {
		this.listener = listener;
		
		return this;
	}
	
	public SelectPropertyBuilder selected(String selectedOption) {
		this.selectedOption = selectedOption;
		
		return this;
	}
	
	public SelectPropertyBuilder optionTexts(String[] text) {
		this.text = text;
		
		return this;
	}
	
	public SelectPropertyWidget build() {
		SelectPropertyWidget widget = new SelectPropertyWidget();
		widget.setName(name);
		widget.setValue(options, selectedOption);
		widget.setListener(listener);
		widget.setText(text);		
		
		return widget;
	}
}
