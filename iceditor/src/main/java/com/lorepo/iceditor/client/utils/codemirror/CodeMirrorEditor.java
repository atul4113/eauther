package com.lorepo.iceditor.client.utils.codemirror;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.dom.client.Element;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.TextArea;

public class CodeMirrorEditor extends Composite{

	private TextArea textArea;
	private JavaScriptObject editor;
	
	public CodeMirrorEditor(){
	
		createUI();
	}
	
	
	private void createUI() {

		textArea = new TextArea();
		textArea.setPixelSize(300, 600);

		initWidget(textArea);
	}


	@Override
	protected void onLoad(){
		
		editor = initCodeMirror(textArea.getElement());
	}
	
	
	public String getText() {

		return getEditorCode(editor);
	}


	public void setText(String css) {
		
		String formatted = css;
		formatted = formatted.replace("\n", "");
		formatted = formatted.replace("{", "{\n");
		formatted = formatted.replace("}", "}\n\n");
		formatted = formatted.replace(";", ";\n");
		setEditorCode(editor, formatted);
	}
	
	
	public native JavaScriptObject initCodeMirror(Element textArea) /*-{
    
    	var editor = $wnd.CodeMirror.fromTextArea(textArea, {
  			mode:  "css",
  			lineNumbers: true,
		});

		return editor;
	}-*/;

	public native String getEditorCode(JavaScriptObject editor)/*-{
		return editor.getValue();
	}-*/;
	
	public native void setEditorCode(JavaScriptObject editor, String code)/*-{
		editor.setValue(code);
	}-*/;

}
