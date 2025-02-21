package com.lorepo.iceditor.client.ui.widgets.modules;

import static com.google.gwt.query.client.GQuery.$;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.NativeEvent;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;

public class ModuleWidget extends Composite {

	private static ModuleWidgetUiBinder uiBinder = GWT
			.create(ModuleWidgetUiBinder.class);

	interface ModuleWidgetUiBinder extends UiBinder<Widget, ModuleWidget> {
	}
	
	@UiField HTMLPanel panel;
	
	private boolean isVisible;
	private boolean isLocked;
	private ModuleChangeListener listener; 
	private boolean isSelected;

	public ModuleWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		
		connectHandlers();
	}

	private void connectHandlers() {
		panel.addDomHandler(new ClickHandler() {
			@Override
			public void onClick(ClickEvent event) {
				NativeEvent nativeEvent = event.getNativeEvent();
				
				setSelected(true);
				
				if (listener != null) {
					listener.onSelected(nativeEvent.getCtrlKey(), nativeEvent.getShiftKey());
				}
			}
		}, ClickEvent.getType());
		
		com.google.gwt.dom.client.Element visibilityElement = getVisibilityElement();
		Event.sinkEvents(visibilityElement, Event.ONCLICK);
		Event.setEventListener(visibilityElement, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				event.preventDefault();
				event.stopPropagation();
				
				setVisible(!isVisible);

				if (listener != null) {
					listener.onVisibilityChanged(isVisible);
				}
			}
		});
		
		com.google.gwt.dom.client.Element lockElement = getLockElement();
		Event.sinkEvents(lockElement, Event.ONCLICK);
		Event.setEventListener(lockElement, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				event.preventDefault();
				event.stopPropagation();

				setLocked(!isLocked);
				
				if (listener != null) {
					listener.onLockedChanged(isLocked);
				}
			}
		});
	}

	private Element getRootElement() {
		return panel.getElement();
	}
	
	public void setId(String id) {
		$(getRootElement()).find("span").html(id);
	}
	
	public com.google.gwt.dom.client.Element getVisibilityElement() {
		return $(getRootElement()).find(".itemVisibility").get(0);
	}
	
	public com.google.gwt.dom.client.Element getLockElement() {
		return $(getRootElement()).find(".itemLock").get(0);
	}
	
	public void setVisible(boolean isVisible) {
		this.isVisible = isVisible;

		if (isVisible) {
			getRootElement().removeClassName("invisible");
		} else {
			getRootElement().addClassName("invisible");
		}
	}
	
	public void setLocked(boolean isLocked) {
		this.isLocked = isLocked;
		
		if (isLocked) {
			getRootElement().addClassName("locked");
		} else {
			getRootElement().removeClassName("locked");
		}
	}
	
	public void setListener(ModuleChangeListener listener) {
		this.listener = listener;
	}
	
	public void setSelected(boolean isSelected) {
		if (isSelected) {
			getRootElement().addClassName("selected");
		} else {
			getRootElement().removeClassName("selected");
		}
		
		this.isSelected = isSelected;
	}
	
	public boolean isSelected() {
		return isSelected;
	}
}
