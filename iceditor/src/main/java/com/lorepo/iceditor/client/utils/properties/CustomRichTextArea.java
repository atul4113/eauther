package com.lorepo.iceditor.client.utils.properties;

import com.google.gwt.user.client.DOM;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.ui.RichTextArea;

public class CustomRichTextArea extends RichTextArea {
	
	public CustomRichTextArea(){
		super();
		DOM.sinkEvents(this.getElement(), Event.KEYEVENTS);
	}
	
	@Override
	public void onBrowserEvent(Event event) {

		final int eventType = DOM.eventGetType(event);

		if (Event.ONKEYPRESS == eventType) {
			if(event.getCharCode() == 'b' && event.getCtrlKey()){ 
				event.preventDefault();
				event.stopPropagation();
				this.getFormatter().toggleBold();
			}
			else if(event.getCharCode() == 'i' && event.getCtrlKey()){ 
				event.preventDefault();
				event.stopPropagation();
				this.getFormatter().toggleItalic();
			}
		}
	}
}
