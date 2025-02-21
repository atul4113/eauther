package com.lorepo.iceditor.client.ui.widgets.properties.editors;

import static com.google.gwt.query.client.GQuery.$;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.Style.Display;
import com.google.gwt.dom.client.AnchorElement;
import com.google.gwt.dom.client.TextAreaElement;
import com.google.gwt.query.client.Function;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.ui.widgets.content.MainPageEventListener;
import com.lorepo.iceditor.client.ui.widgets.content.WidgetLockerController;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.iceditor.client.ui.widgets.modals.ModalsWidget;
import com.lorepo.iceditor.client.ui.widgets.modals.QuestionModalListener;
import com.lorepo.iceditor.client.ui.widgets.utils.MainPageUtils;

public class TextEditorWidget extends Composite {

	private static TextEditorWidgetUiBinder uiBinder = GWT
			.create(TextEditorWidgetUiBinder.class);

	interface TextEditorWidgetUiBinder extends
			UiBinder<Widget, TextEditorWidget> {
	}
	
	@UiField HTMLPanel panel;
	@UiField TextAreaElement text;
	@UiField AnchorElement apply;
	@UiField AnchorElement save;
	private String startText;
	private ModalsWidget modals;

	public TextEditorWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		
		panel.getElement().setId("htmlEditorPage");
		
		apply.setId("editorApply");
		save.setId("editorSave");
		
		updateElementsTexts();
		initJSAPI(this);
		hide();
	}
	
	private native void initJSAPI(TextEditorWidget x) /*-{
	    $wnd.isTextEditorModified = function() {
	        return x.@com.lorepo.iceditor.client.ui.widgets.properties.editors.TextEditorWidget::isModified()();
	    }
	}-*/;
	
	private boolean isModified() {
		return !startText.equals(text.getValue());
	}
	
	public void show() {
		MainPageUtils.show(panel);
		startText = text.getValue();
	}
	
	public void hide() {
		removeHandlers();
		WidgetLockerController.hide();
		this.text.setValue("");
		panel.getElement().getStyle().setDisplay(Display.NONE);
	}
	
	public void setText(String text) {
		if (text == null) {
			text = "";
		}
		
		this.text.setValue(text);
	}
	
	public String getText() {
		return this.text.getValue();
	}
	
	private void removeHandlers() {
		$("#content").off("mousedown touchstart");
		$(".mainPageCloseBtn").off("click");
	}
	
	private void saveChanges(final MainPageEventListener listener) {
		getModals().addModal(DictionaryWrapper.get("save_changes"), new QuestionModalListener() {
			@Override
			public void onDecline() {
				reset();
				hide();
			}
			
			@Override
			public void onAccept() {
				removeHandlers();
				reset();
				listener.onSave();
			}
		});
	}
	
	public void setListener(final MainPageEventListener listener) {
		if (listener == null) {
			return;
		}
		
		Event.sinkEvents(apply, Event.ONCLICK);
		Event.setEventListener(apply, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				listener.onApply();
				reset();
			}
		});
		
		Event.sinkEvents(save, Event.ONCLICK);
		Event.setEventListener(save, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt() && Event.ONTOUCHEND != event.getTypeInt()) {
					return;
				}
				
				removeHandlers();
				listener.onSave();
				reset();
			}
		});

		$(".mainPageCloseBtn").on("click", new Function(){
			public void f() {
				if(isModified() && MainPageUtils.isWindowOpened("textEditorPage")) {
					saveChanges(listener);
				} else if (MainPageUtils.isWindowOpened("textEditorPage")) {
					hide();
				}
			}
		});
		
		$("#content").on("mousedown", new Function(){
			public void f() {
				if(isModified() && MainPageUtils.isWindowOpened("textEditorPage")) {
					saveChanges(listener);
				} else if (MainPageUtils.isWindowOpened("textEditorPage")) {
					hide();
				}
			}
		});
	}
	
	private void reset() {
		startText = text.getValue();
	}
	
	public void updateElementsTexts() {
		apply.setInnerText(DictionaryWrapper.get("apply"));
		save.setInnerText(DictionaryWrapper.get("save"));
	}
	
	public void setName(String name) {
		$(panel.getElement()).find(".mainPageHeader h3").text(name);
	}
	
	public void setModals(ModalsWidget modals) {
		this.modals = modals;
	}
	
	private ModalsWidget getModals() {
		return modals;
	}
}
