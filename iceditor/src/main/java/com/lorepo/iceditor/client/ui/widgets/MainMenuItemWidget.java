package com.lorepo.iceditor.client.ui.widgets;

import static com.google.gwt.query.client.GQuery.$;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Command;
import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;

public class MainMenuItemWidget extends Composite {

	private static MainMenuItemWidgetUiBinder uiBinder = GWT
			.create(MainMenuItemWidgetUiBinder.class);

	interface MainMenuItemWidgetUiBinder extends
			UiBinder<Widget, MainMenuItemWidget> {
	}
	
	@UiField HTMLPanel panel;

	public MainMenuItemWidget() {
		initWidget(uiBinder.createAndBindUi(this));
	}

	public void setName(String name) {
		$(getRootElement()).find("a").html(name);		
	}
	
	public String getName() {
		return $(getRootElement()).find("a").html();
	}
	
	private Element getRootElement() {
		return panel.getElement();
	}

	public void setCommand(final Command command) {
		Element element = (Element) $(getRootElement()).find("a").get(0);
		
		Event.sinkEvents(element, Event.ONCLICK);
		Event.setEventListener(element, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				command.execute();
			}
		});
	}
}
