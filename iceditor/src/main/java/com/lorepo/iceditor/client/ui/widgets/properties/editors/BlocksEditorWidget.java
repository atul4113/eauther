package com.lorepo.iceditor.client.ui.widgets.properties.editors;

import static com.google.gwt.query.client.GQuery.$;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.dom.client.AnchorElement;
import com.google.gwt.dom.client.DivElement;
import com.google.gwt.dom.client.Element;
import com.google.gwt.dom.client.Style.Display;
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
import com.lorepo.iceditor.client.ui.widgets.modals.ModalsWidget;
import com.lorepo.iceditor.client.ui.widgets.modals.QuestionModalListener;
import com.lorepo.iceditor.client.ui.widgets.utils.MainPageUtils;
import com.lorepo.icf.utils.JavaScriptUtils;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;

public abstract class BlocksEditorWidget extends Composite {
	private static TextEditorWidgetUiBinder uiBinder = GWT
			.create(TextEditorWidgetUiBinder.class);

	interface TextEditorWidgetUiBinder extends
			UiBinder<Widget, BlocksEditorWidget> {
	}
	
	@UiField HTMLPanel panel;
	@UiField DivElement text;
	@UiField AnchorElement apply;
	@UiField AnchorElement save;
	private String startText;
	private ModalsWidget modals;
	private JavaScriptObject blocklyWorkspace;
	private JavaScriptObject blocklyWorkspaceSVG;
	private String initialText = "<xml></xml>";

	public BlocksEditorWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		
		panel.getElement().setId("blocksEditorPage");
		
		apply.setId("editorApply");
		save.setId("editorSave");
		
		updateElementsTexts();
		initJSAPI(this);
		addResizeMessageListener(this);
		hide();
	}
	
	private native void initJSAPI(BlocksEditorWidget x) /*-{
	    $wnd.isTextEditorModified = function() {
	        return x.@com.lorepo.iceditor.client.ui.widgets.properties.editors.BlocksEditorWidget::isModified()();
	    }
	}-*/;
	
	private native void addResizeMessageListener(BlocksEditorWidget x) /*-{
    	$wnd.addEventListener('message',function(event){
    		if(event.data == 'RESIZE_EDITOR'){
    			var workspace = x.@com.lorepo.iceditor.client.ui.widgets.properties.editors.BlocksEditorWidget::getBlocklyWorkspaceSVG()();
    			$wnd.Blockly.svgResize(workspace);
    		}
    	});	    
	}-*/;
	
	private void setBlocklyWorkspaceSVG(JavaScriptObject workspace) {
		this.blocklyWorkspaceSVG = workspace;
	}
	
	private void setBlocklyWorkspace(JavaScriptObject workspace) {
		this.blocklyWorkspace = workspace;
	}
	
	private JavaScriptObject getBlocklyWorkspaceSVG() {
		return this.blocklyWorkspaceSVG;
	}
	
	private boolean isModified() {
		return !startText.equals(getText());
	}
	
	private native void renderWorkspace(BlocksEditorWidget x, JavaScriptObject workspaceSVG, JavaScriptObject workspace)/*-{
		workspaceSVG.render();
		if (workspace != null) {
			var toolboxXML = x.@com.lorepo.iceditor.client.ui.widgets.properties.editors.BlocksEditorWidget::getToolboxXML()();
			workspace.updateToolbox(toolboxXML);
		}
	}-*/;
	
	public void show() {
		MainPageUtils.show(panel);
		if (this.blocklyWorkspaceSVG == null) {
			this.initBlockly(this, this.getElement());
			setText(initialText);
		} else{
			renderWorkspace(this, blocklyWorkspaceSVG, blocklyWorkspaceSVG);
		}
		startText = getText();
		
	}
	
	
	abstract protected void intializeCustomBlocks();
	
	abstract protected String getToolboxXML();
	
	private String getLabel(String key) {
		return DictionaryWrapper.get(key);
	}
	
	private native void initBlockly(BlocksEditorWidget x, Element el)/*-{
		var $el = $wnd.$(el).find('.ic_scriptEditor');
		var toolboxXML = x.@com.lorepo.iceditor.client.ui.widgets.properties.editors.BlocksEditorWidget::intializeCustomBlocks()();
		var toolboxXML = x.@com.lorepo.iceditor.client.ui.widgets.properties.editors.BlocksEditorWidget::getToolboxXML()();
		var workspace = $wnd.initBlocklyCodeEditor($el[0], toolboxXML);
		x.@com.lorepo.iceditor.client.ui.widgets.properties.editors.BlocksEditorWidget::setBlocklyWorkspaceSVG(Lcom/google/gwt/core/client/JavaScriptObject;)(workspace);
	}-*/;
	
	private native String getWorkspaceXML(BlocksEditorWidget x)/*-{
		var workspace = x.@com.lorepo.iceditor.client.ui.widgets.properties.editors.BlocksEditorWidget::getBlocklyWorkspaceSVG()();
		if (workspace == null) return "";
		var xml = $wnd.Blockly.Xml.workspaceToDom(workspace);
		var xml_text = $wnd.Blockly.Xml.domToText(xml);
		return xml_text;
	}-*/;
	
	private native void loadWorkspaceXML(BlocksEditorWidget x, String workspaceXML)/*-{
		var workspaceSVG = x.@com.lorepo.iceditor.client.ui.widgets.properties.editors.BlocksEditorWidget::getBlocklyWorkspaceSVG()();
		if (workspaceSVG == null) return;
		workspaceSVG.clear();
		var xml = $wnd.Blockly.Xml.textToDom(workspaceXML);
		var workspace = $wnd.Blockly.Xml.domToWorkspace(xml, workspaceSVG);
		x.@com.lorepo.iceditor.client.ui.widgets.properties.editors.BlocksEditorWidget::setBlocklyWorkspace(Lcom/google/gwt/core/client/JavaScriptObject;)(workspace);
	}-*/;
	
	public void hide() {
		removeHandlers();
		WidgetLockerController.hide();
		setText("<xml></xml>");
		panel.getElement().getStyle().setDisplay(Display.NONE);
	}
	
	public void setText(String text) {
		if (text == null) {
			text = "";
		}
		if (blocklyWorkspaceSVG != null){
			loadWorkspaceXML(this,text);
		} else {
			initialText = text;
		}
	}
	
	public String getText() {
		return getWorkspaceXML(this);
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
				if(isModified() && MainPageUtils.isWindowOpened("blocksEditorPage")) {
					saveChanges(listener);
				} else if (MainPageUtils.isWindowOpened("blocksEditorPage")) {
					hide();
				}
			}
		});
		
		$("#content").on("mousedown", new Function(){
			public void f() {
				if(isModified() && MainPageUtils.isWindowOpened("blocksEditorPage")) {
					saveChanges(listener);
				} else if (MainPageUtils.isWindowOpened("blocksEditorPage")) {
					hide();
				}
			}
		});
	}
	
	private void reset() {
		startText = getText();
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
