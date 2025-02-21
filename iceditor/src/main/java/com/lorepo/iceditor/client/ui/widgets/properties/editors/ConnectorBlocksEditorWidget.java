package com.lorepo.iceditor.client.ui.widgets.properties.editors;

import com.google.gwt.xml.client.Document;
import com.google.gwt.xml.client.Element;
import com.google.gwt.xml.client.Node;
import com.google.gwt.xml.client.XMLParser;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;

public class ConnectorBlocksEditorWidget extends BlocksEditorWidget {
	
	private String toolboxXML = null;
	protected String getToolboxXML() {
	
		if (toolboxXML != null) return toolboxXML;
		
		Document toolboxDocument = XMLParser.createDocument();
		Element root = toolboxDocument.createElement("xml");
		toolboxDocument.appendChild(root);
		
		setModuleBlocksCategory(toolboxDocument);
		setCustomBlocksCategory(toolboxDocument);
		root.appendChild(toolboxDocument.createElement("sep"));
		setActivitiesCategory(toolboxDocument);
		setMediaCategory(toolboxDocument);
		setScriptingCategory(toolboxDocument);
		
		toolboxXML = toolboxDocument.toString();
		return toolboxXML;
	}
	
	private void setModuleBlocksCategory(Document doc) {
		Node category = appendCategory(doc, doc.getChildNodes().item(0), DictionaryWrapper.get("Visual_Feedback_Creator_module_blocks"));
		appendBlock(doc,category,"vfc_source_module");
		appendBlock(doc,category,"vfc_feedback_module");	
		appendBlock(doc,category,"vfc_source_event");
	}
	
	private void setCustomBlocksCategory(Document doc) {
		Node category = appendCategory(doc, doc.getChildNodes().item(0), DictionaryWrapper.get("Visual_Feedback_Creator_custom_blocks"));
		appendBlock(doc,category,"vfc_custom_action");
		appendBlock(doc,category,"vfc_custom_event");
	}
	
	private void setActivitiesCategory(Document doc) {
		Node category = appendCategory(doc, doc.getChildNodes().item(0), DictionaryWrapper.get("activities_menu"));
		
		Node choice = appendCategory(doc, category, DictionaryWrapper.get("choice"));
		appendBlock(doc,choice,"vfc_show");
		appendBlock(doc,choice,"vfc_hide");	
		appendBlock(doc,choice,"vfc_disable");	
		appendBlock(doc,choice,"vfc_enable");	
		appendBlock(doc,choice,"vfc_reset");	
		appendBlock(doc,choice,"vfc_choice_mark_correct");
		appendBlock(doc,choice,"vfc_choice_mark_wrong");
		appendBlock(doc,choice,"vfc_choice_mark_empty");
		appendBlock(doc,choice,"vfc_choice_event");
		
		Node connection = appendCategory(doc, category, DictionaryWrapper.get("Connection_name"));
		appendBlock(doc,connection,"vfc_show");
		appendBlock(doc,connection,"vfc_hide");	
		appendBlock(doc,connection,"vfc_connection_new_correct");	
		appendBlock(doc,connection,"vfc_connection_new_wrong");	
		appendBlock(doc,connection,"vfc_connection_event");
		
		Node ordering = appendCategory(doc, category, DictionaryWrapper.get("ordering_module"));
		appendBlock(doc,ordering,"vfc_show");
		appendBlock(doc,ordering,"vfc_hide");	
		appendBlock(doc,ordering,"vfc_reset");
		appendBlock(doc,ordering,"vfc_ordering_event");
		
		Node text = appendCategory(doc, category, DictionaryWrapper.get("text"));
		appendBlock(doc,text,"vfc_show");
		appendBlock(doc,text,"vfc_hide");
		appendBlock(doc,text,"vfc_text_set_text");
		appendBlock(doc,text,"vfc_enable_gap");
		appendBlock(doc,text,"vfc_disable_gap");
		appendBlock(doc,text,"vfc_enable_gaps");
		appendBlock(doc,text,"vfc_disable_gaps");
		appendBlock(doc,text,"vfc_text_mark_correct");
		appendBlock(doc,text,"vfc_text_mark_wrong");
		appendBlock(doc,text,"vfc_text_mark_empty");	
		appendBlock(doc,text,"vfc_text_correct_gap");	
		appendBlock(doc,text,"vfc_text_wrong_gap");	
		appendBlock(doc,text,"vfc_text_event");	
		
		Node trueFalse = appendCategory(doc, category, DictionaryWrapper.get("TrueFalse_name"));
		appendBlock(doc,trueFalse,"vfc_show");
		appendBlock(doc,trueFalse,"vfc_hide");	
		appendBlock(doc,trueFalse,"vfc_reset");
		appendBlock(doc,trueFalse,"vfc_true_false_correct");
		appendBlock(doc,trueFalse,"vfc_true_false_correct_row");
		appendBlock(doc,trueFalse,"vfc_true_false_event");
	}
	
	private void setMediaCategory(Document doc) {
		Node category = appendCategory(doc, doc.getChildNodes().item(0), DictionaryWrapper.get("media_menu"));
		
		Node audio = appendCategory(doc, category, DictionaryWrapper.get("Audio_name"));
		appendBlock(doc,audio,"vfc_show");
		appendBlock(doc,audio,"vfc_hide");	
		appendBlock(doc,audio,"vfc_play");
		appendBlock(doc,audio,"vfc_stop");
		appendBlock(doc,audio,"vfc_pause");
		appendBlock(doc,audio,"vfc_video_playing");
		appendBlock(doc,audio,"vfc_audio_ended");
		appendBlock(doc,audio,"vfc_audio_paused");
		
		Node image = appendCategory(doc, category, DictionaryWrapper.get("image"));
		appendBlock(doc,image,"vfc_show");
		appendBlock(doc,image,"vfc_hide");	
		
		Node video = appendCategory(doc, category, DictionaryWrapper.get("video"));
		appendBlock(doc,video,"vfc_show");
		appendBlock(doc,video,"vfc_hide");	
		appendBlock(doc,video,"vfc_play");
		appendBlock(doc,video,"vfc_stop");
		appendBlock(doc,video,"vfc_seek");
		appendBlock(doc,video,"vfc_next");
		appendBlock(doc,video,"vfc_prev");
		appendBlock(doc,video,"vfc_jump_to");
		appendBlock(doc,video,"vfc_jump_to_id");
		appendBlock(doc,video,"vfc_show_subs");
		appendBlock(doc,video,"vfc_hide_subs");
		appendBlock(doc,video,"vfc_video_ended");
		appendBlock(doc,video,"vfc_video_playing");

	}
	
	private void setScriptingCategory(Document doc) {
		Node category = appendCategory(doc, doc.getChildNodes().item(0), DictionaryWrapper.get("scripting_menu"));
		
		Node feedback = appendCategory(doc, category, DictionaryWrapper.get("feedback_name"));
		appendBlock(doc,feedback,"vfc_show");
		appendBlock(doc,feedback,"vfc_hide");
		appendBlock(doc,feedback,"vfc_next");
		appendBlock(doc,feedback,"vfc_prev");
		appendBlock(doc,feedback,"vfc_feedback_change");
		appendBlock(doc,feedback,"vfc_feedback_set_def");
	}
	
	private Node appendCategory(Document doc, Node parent, String title) {
		Element category = doc.createElement("category");
		category.setAttribute("name", title);
		parent.appendChild(category);
		return category;
	}
	
	private Node appendBlock(Document doc, Node parent, String blockID) {
		Element block = doc.createElement("block");
		block.setAttribute("type", blockID);
		parent.appendChild(block);
		return block;
	}
	
	protected void intializeCustomBlocks(){
		intializeCustomBlocks(this);
	}
	
	private native void intializeCustomBlocks(BlocksEditorWidget x)/*-{
		var labelKeys = Object.keys($wnd.BlocklyCustomBlocks.AGC.DEFAULT_LABELS);
		var labels = [];
		for (var i = 0; i < labelKeys.length; i++) {
			var key = labelKeys[i];
			labels[key] = x.@com.lorepo.iceditor.client.ui.widgets.properties.editors.BlocksEditorWidget::getLabel(Ljava/lang/String;)(key);
		}
		$wnd.BlocklyCustomBlocks.AGC.addBlocks(labels);
	}-*/;

}
