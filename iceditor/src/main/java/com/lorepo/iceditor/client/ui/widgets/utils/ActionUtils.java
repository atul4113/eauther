package com.lorepo.iceditor.client.ui.widgets.utils;

import com.google.gwt.dom.client.Element;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.lorepo.iceditor.client.actions.AbstractAction;

public class ActionUtils {
	public static void bindButtonWithAction(Element element, final int eventCode, final AbstractAction action) {
		Event.sinkEvents(element, eventCode);
		Event.setEventListener(element, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(eventCode != event.getTypeInt()) {
					return;
				}
				
				action.execute();
			}
		});
	}
}
