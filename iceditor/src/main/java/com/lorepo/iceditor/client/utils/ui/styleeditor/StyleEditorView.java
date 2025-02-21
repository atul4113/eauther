package com.lorepo.iceditor.client.utils.ui.styleeditor;

import java.util.List;

import com.google.gwt.dom.client.Style.Unit;
import com.google.gwt.event.dom.client.ChangeEvent;
import com.google.gwt.event.dom.client.ChangeHandler;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.LayoutPanel;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.TextArea;
import com.lorepo.iceditor.client.utils.ui.styleeditor.StyleEditorPresenter.IDisplay;
import com.lorepo.iceditor.client.utils.ui.styleeditor.StyleEditorPresenter.IValueChanged;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;

/**
 * Edytor ten umożliwia edycję:
 * - klasy
 * - parametrów inline CSS
 * 
 * @author Krzysztof Langner
 *
 */
public class StyleEditorView extends LayoutPanel implements IDisplay{

	private Label 		styleClassLabel;
	private ListBox		classNameEditor;
	private Label 		inlineCSSLabel;
	private TextArea	inlineCSSEditor;
	private Button		saveInlineStyleButton;
	
	private IValueChanged listener;
	

	public StyleEditorView(){
	
		createUI();
		connectHandlers();
	}
	
	private void createUI() {

		HTML header = new HTML(DictionaryWrapper.get("styles"));
		header.setStyleName("ice_panelHeader");
		styleClassLabel = new Label(DictionaryWrapper.get("css_class"));
		classNameEditor = new ListBox();
		classNameEditor.setWidth("97%");
		inlineCSSLabel = new Label(DictionaryWrapper.get("inline_css"));
		inlineCSSEditor = new TextArea();
		inlineCSSEditor.setStyleName("ice_cssEditor");
		inlineCSSEditor.setSize("97%", "98%");
		saveInlineStyleButton = new Button(DictionaryWrapper.get("update_style"));
		
		add(header);
		add(styleClassLabel);
		add(classNameEditor);
		add(inlineCSSLabel);
		add(inlineCSSEditor);
		add(saveInlineStyleButton);

		// Set position
		setWidgetTopHeight(header, 0, Unit.EM, 1.5, Unit.EM);
		setWidgetTopHeight(styleClassLabel, 2, Unit.EM, 1, Unit.EM);
		setWidgetTopHeight(classNameEditor, 3, Unit.EM, 2, Unit.EM);
		setWidgetTopHeight(inlineCSSLabel, 5.5, Unit.EM, 1, Unit.EM);
		setWidgetTopBottom(inlineCSSEditor, 6.5, Unit.EM, 2.5, Unit.EM);
		setWidgetBottomHeight(saveInlineStyleButton, 5, Unit.PX, 1.8, Unit.EM);
		
		setWidgetLeftRight(styleClassLabel, 5, Unit.PX, 5, Unit.PX);
		setWidgetLeftRight(classNameEditor, 5, Unit.PX, 5, Unit.PX);
		setWidgetLeftRight(inlineCSSLabel, 5, Unit.PX, 5, Unit.PX);
		setWidgetLeftRight(inlineCSSEditor, 5, Unit.PX, 5, Unit.PX);
		setWidgetLeftWidth(saveInlineStyleButton, 5, Unit.PX, 40, Unit.PCT);
		
		// Disable UI till module is set
		enableUI(false);
	}


	private void connectHandlers() {
		
		classNameEditor.addChangeHandler(new ChangeHandler() {
			public void onChange(ChangeEvent event) {
			
				if(listener != null){
					int index = classNameEditor.getSelectedIndex();
					String className = classNameEditor.getItemText(index);
					listener.onClassNameChanged(className);
				}
			}
		});

		saveInlineStyleButton.addClickHandler(new ClickHandler() {
			public void onClick(ClickEvent event) {
				if(listener != null){
					String convertedStyle = inlineCSSEditor.getText().replace("\n", "");
					listener.onInlineStyleChanged(convertedStyle);
				}
			}
		});
	}


	private void enableUI(boolean enable) {
		
		classNameEditor.setEnabled(enable);
		inlineCSSEditor.setEnabled(enable);
	}


	@Override
	public void setEnabled(boolean enabled) {
		enableUI(enabled);
	}


	/**
	 * To zamieszanie z dodaniem pojedyńczej spacji wynika z dziwnego bugu.
	 * Czasami edytor nie pozwala rozpocząć edycji, jeżeli jest pusty string.
	 * Dzieje się to losowo i nie ma żadnego exception. 
	 * Podejrzewam, że to jakiś bug w TextArea
	 */
	@Override
	public void setInlineStyles(String text) {
		
		if(!text.isEmpty()){
			inlineCSSEditor.setText(text);
		}
		else{
			inlineCSSEditor.setText(" ");
		}
	}


	@Override
	public void clearClassList() {
		classNameEditor.clear();
	}


	@Override
	public void setClassList(List<String> classNames) {

		for(String name : classNames){
			classNameEditor.addItem(name);
		}
	}


	@Override
	public void addValueChangedListener(IValueChanged listener) {
		this.listener = listener;
	}

	@Override
	public void setSelectedClass(String name) {
		
		if(name == null){
			return;
		}
		
		for(int i = 0; i < classNameEditor.getItemCount(); i++){
			String itemText = classNameEditor.getItemText(i);
			if(itemText.compareTo(name) == 0){
				classNameEditor.setSelectedIndex(i);
				break;
			}
		}
	}
}
