package com.lorepo.iceditor.client.ui.widgets.content;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Set;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.dom.client.AnchorElement;
import com.google.gwt.dom.client.DivElement;
import com.google.gwt.dom.client.Element;
import com.google.gwt.dom.client.HeadingElement;
import com.google.gwt.dom.client.NodeList;
import com.google.gwt.dom.client.Style.Display;
import com.google.gwt.dom.client.Style.Unit;
import com.google.gwt.dom.client.TextAreaElement;
import com.google.gwt.event.dom.client.ChangeEvent;
import com.google.gwt.event.dom.client.ChangeHandler;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.actions.ActionFactory;
import com.lorepo.iceditor.client.ui.widgets.utils.MainPageUtils;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.CssStyle;

public class EditCSSWidget extends Composite {

	private static EditCSSWidgetUiBinder uiBinder = GWT.create(EditCSSWidgetUiBinder.class);

	interface EditCSSWidgetUiBinder extends UiBinder<Widget, EditCSSWidget> {}
	
	@UiField HTMLPanel panel;
	@UiField AnchorElement apply;
	@UiField AnchorElement save;
	@UiField TextAreaElement editor;
	@UiField HeadingElement title;
	@UiField DivElement tip;
	@UiField DivElement schemelessURLWarning;
	@UiField DivElement tabContents;
	@UiField AnchorElement closeButton;
	@UiField ListBox lessonStylesSelect;

	private boolean visible;
	private boolean shouldOpen = false;
	private boolean firstOpen = true;
	private final static String NO_SCHEMELESS_WARNING_STYLE = "file-select-schemeless-urls-no-warning";
	
	private JavaScriptObject codeEditor;
	
	private HashMap<String, CssStyle> styles = new HashMap<String, CssStyle>();
	private String actualStyleID = "default";
	private ChangeHandler changeHandler;
	private String previousSelectedStyle;

	public EditCSSWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		this.changeHandler = this.createChangeHandler();
		this.lessonStylesSelect.addChangeHandler(this.changeHandler);
		codeEditor = initCodeMirror(editor, this);
		updateElementsText();
		hide();
	}
	
	public void setActionFactory(ActionFactory factory) {
	}
	
	public String getStyle() {
		return getStylesValue(codeEditor);
	}
	
	public HashMap<String, CssStyle> getStyles() {
		return this.styles;
	}
	
	public void hideSchemelessWarning() {
		schemelessURLWarning.addClassName(NO_SCHEMELESS_WARNING_STYLE);
	}

	public void showSchemelessWarning() {
		schemelessURLWarning.removeClassName(NO_SCHEMELESS_WARNING_STYLE);
	}
	
	private ChangeHandler createChangeHandler() {
		return new ChangeHandler() {
			@Override
			public void onChange(ChangeEvent event) {
				saveCurrentStyle();

				String styleID = getCurrentSelectedStyleID();
				
				CssStyle selectedStyle = styles.get(styleID);
				setActualStyleID(styleID);
				previousSelectedStyle = selectedStyle.getID();
				setStyle(selectedStyle);
			}
		};
	}

	public void renderSelectOptions() {
		this.lessonStylesSelect.clear();
		int index = 0;
		
		for (CssStyle style : this.styles.values()) {
			this.lessonStylesSelect.addItem(getStyleName(style), style.getID());
			
			if (style.getID().compareTo(this.actualStyleID) == 0) {
				this.lessonStylesSelect.setSelectedIndex(index);
				this.previousSelectedStyle = style.getID();
			}
			
			index++;
		}
		
		this.setStyle(this.styles.get(this.actualStyleID));
	}
	
	private String getDefaultStyleID(HashMap<String, CssStyle> styles) {
		for(CssStyle style : styles.values()) {
			if (style.isDefault()) {
				return style.getID();
			}
		}
		
		return null;
	}

	public void saveCurrentStyle() {
		CssStyle previousStyle = styles.get(previousSelectedStyle);
		previousStyle.setValue(getStyle());
		styles.put(previousSelectedStyle, previousStyle);
	}

	public boolean isVisible () {
		return visible;
		
	}
	public void hide() {
		panel.getElement().getStyle().setDisplay(Display.NONE);
		WidgetLockerController.hide();
		visible = false;
	}
	
	public void show() {
		MainPageUtils.showWithoutLockers(panel);
		tabContents.getStyle().setHeight(tabContents.getOffsetHeight(), Unit.PX);
		this.renderSelectOptions();
		visible = true;
		this.refreshEditor(codeEditor);
		if (firstOpen) {
			firstOpen = false;
			this.refreshEditor(codeEditor);
		}
	}

	public void setListener(final MainPageEventListener listener) {
		Event.sinkEvents(this.save, Event.ONCLICK);
		Event.setEventListener(this.save, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}

				saveCurrentStyle();
				listener.onSave();
			}
		});
		
		Event.sinkEvents(this.apply, Event.ONCLICK);
		Event.setEventListener(apply, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				saveCurrentStyle();
				listener.onApply();
			}
		});
		
		Event.sinkEvents(closeButton, Event.ONCLICK);
		Event.setEventListener(closeButton, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				visible = false;
			}
		});
		
		getElementsByClassName(tabContents, "CodeMirror-scroll").getItem(0).getStyle().setHeight(100, Unit.PCT);
	}

	
	public void setStyles(HashMap<String, CssStyle> styles) {
		this.actualStyleID = this.findStyleToSelect(styles, this.styles, this.actualStyleID);
		this.styles = styles;
		this.renderSelectOptions();
	}
	
	private String findStyleToSelect(HashMap<String, CssStyle> newStyles, HashMap<String, CssStyle> oldStyles, String actualStyleID) {
		String result;
		
		if (newStyles.size() == oldStyles.size() + 1) {
			result = this.findNewlyAddedStyle(newStyles, oldStyles);
		} else if (newStyles.size() == oldStyles.size() - 1 && !newStyles.containsKey(actualStyleID)) {
			result = this.getDefaultStyleID(newStyles);
		} else if (newStyles.containsKey(actualStyleID)) {
			result = actualStyleID;
		} else {
			result = this.getDefaultStyleID(newStyles);
		}
		
		return result;
	}
	
	public String findNewlyAddedStyle(HashMap<String, CssStyle> newStyles, HashMap<String, CssStyle> oldStyles) {
		Set<String> newStylesIds = new HashSet<String>();
		Set<String> oldStylesIds = new HashSet<String>();

		for(CssStyle cssStyle : newStyles.values()) {
			newStylesIds.add(cssStyle.getID());
		}
		
		for(CssStyle cssStyle : oldStyles.values()) {
			oldStylesIds.add(cssStyle.getID());
		}

		newStylesIds.removeAll(oldStylesIds);
		return newStylesIds.iterator().next();	
	}
	

	public void setActualStyleID(String actualStyleID) {
		this.actualStyleID  = actualStyleID;
		this.setStyle(this.styles.get(actualStyleID));
	}
	
	private native NodeList<Element> getElementsByClassName(Element element, String name) /*-{
    	return element.getElementsByClassName(name);
	}-*/;

	private native int getElementHeight(Element element) /*-{
    	return $(element).height();
	}-*/;
	
	private void setStyle(CssStyle style) {
		String formatted = style.getValue();

		if (styles == null) {
			formatted = "";
		} else {
			formatted = formatted.replace("\n", "");
			formatted = formatted.replace("{", "{\n");
			formatted = formatted.replace("}", "}\n\n");
			formatted = formatted.replace(";", ";\n");
		}

		setEditorCode(codeEditor, formatted);	
	}
	
	private native JavaScriptObject initCodeMirror(Element textArea, EditCSSWidget widget) /*-{
		function parseAllLines () {
			for (var i = 0; i < editor.lineCount(); i++) {
				var haveNonSchemelessURL = searchNonSchemelessURL(editor.getLine(i).toUpperCase());
				setWarningVisibility(haveNonSchemelessURL);
				if (haveNonSchemelessURL) {
					break;
				}
			}
		};
		
		function setWarningVisibility (visible) {
			if (visible) {
				widget.@com.lorepo.iceditor.client.ui.widgets.content.EditCSSWidget::showSchemelessWarning()();
			}
			else {
				widget.@com.lorepo.iceditor.client.ui.widgets.content.EditCSSWidget::hideSchemelessWarning()();
			}		
		}
		
		function searchNonSchemelessURL (line) {
			var visible = false;
			var pattern = /(HTTP|HTTPS)\:\/\//; 
																						
			if (line.match(pattern)) {
				return true;
			}
			
			for (var pos = line.indexOf("WWW."); pos !== -1; pos = line.indexOf("WWW.", pos + 1)) {
    			if (line[pos-1] != '/' || line[pos-2] != '/') {
					return true;    				
    			}
			}
			
			return false;
		}
		
		var editor = $wnd.CodeMirror.fromTextArea(textArea, {
			mode:  "css",
			lineNumbers: true
		});

		
		$wnd.CodeMirror.connect(editor.getInputField(), "change", parseAllLines);
		$wnd.CodeMirror.connect(editor.getInputField(), "keyup", parseAllLines);
		
		return editor;
	}-*/;
	
	private native void setEditorCode(JavaScriptObject editor, String code)/*-{
		editor.setValue(code);
	}-*/;
	
	private native String getStylesValue(JavaScriptObject editor)/*-{
		return editor.getValue();
	}-*/;
	
	private native void refreshEditor (JavaScriptObject editor) /*-{
		editor.refresh();
	}-*/;
	
	private void updateElementsText() {
		save.setInnerText(DictionaryWrapper.get("save"));
		apply.setInnerText(DictionaryWrapper.get("apply"));
		tip.setInnerText(DictionaryWrapper.get("edit_css_tip"));
		title.setInnerText(DictionaryWrapper.get("edit_css"));
		schemelessURLWarning.setInnerHTML(DictionaryWrapper.get("schemeless_url_warning"));
	}

	private String getCurrentSelectedStyleID() {
		int selectedValueIndex = lessonStylesSelect.getSelectedIndex();

		String styleID = lessonStylesSelect.getValue(selectedValueIndex);
		return styleID;
	}
	
	private String getStyleName(CssStyle style) {
		String layoutName;
		if (style.isDefault()) {
			String defaultTitle = DictionaryWrapper.get("semi_responsive_default_mark");
			layoutName = style.getName() + " (" + defaultTitle + ")";
		} else {
			layoutName = style.getName();
		}
		return layoutName;
	}
}
