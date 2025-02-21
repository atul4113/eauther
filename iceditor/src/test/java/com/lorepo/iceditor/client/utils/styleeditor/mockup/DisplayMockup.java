package com.lorepo.iceditor.client.utils.styleeditor.mockup;

import java.util.ArrayList;
import java.util.List;

import com.lorepo.iceditor.client.utils.ui.styleeditor.StyleEditorPresenter.IDisplay;
import com.lorepo.iceditor.client.utils.ui.styleeditor.StyleEditorPresenter.IValueChanged;

public class DisplayMockup implements IDisplay {

	private boolean enabled = false;
	private String	inlineStyles;
	private List<String> classNames = new ArrayList<String>();
	private IValueChanged listener;
	private String selectedName;
	
	
	@Override
	public void setEnabled(boolean enabled) {
		this.enabled = enabled;
	}

	public boolean isEnabled(){
		return enabled;
	}

	@Override
	public void setInlineStyles(String text) {
		this.inlineStyles = text;
	}
	
	public String getInlineStyles(){
		return inlineStyles;
	}

	@Override
	public void clearClassList() {
		classNames.clear();
	}

	@Override
	public void setClassList(List<String> classNames) {
		this.classNames = classNames;
	}
	
	public List<String> getClassNames(){
		return classNames;
	}

	@Override
	public void addValueChangedListener(IValueChanged listener) {
		this.listener = listener;
	}
	
	
	public IValueChanged getListener(){
		return listener;
	}

	@Override
	public void setSelectedClass(String name) {
		this.selectedName = name;
	}
	
	public String getSelectedName(){
		return selectedName;
	}
}
