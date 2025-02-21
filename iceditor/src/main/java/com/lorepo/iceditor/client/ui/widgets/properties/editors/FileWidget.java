package com.lorepo.iceditor.client.ui.widgets.properties.editors;

import static com.google.gwt.query.client.GQuery.$;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;

public class FileWidget extends Composite {

	private static FileWidgetUiBinder uiBinder = GWT
			.create(FileWidgetUiBinder.class);

	interface FileWidgetUiBinder extends UiBinder<Widget, FileWidget> {
	}
	
	@UiField HTMLPanel panel;

	public FileWidget() {
		initWidget(uiBinder.createAndBindUi(this));
	}

	private Element getRootElement() {
		return panel.getElement();
	}
	
	public void setInfo(String name, String url, String contentType) {
		$(getRootElement()).find(".fileItemLabel").html(name);
		
		$(getRootElement()).find(".fileItemImageContainer img").attr("src", getIconURL(contentType, url));
		$(getRootElement()).find(".fileItemPath").val(url);		
	}
	
	private static String getIconURL(String type, String imageUrl){
		if (type.startsWith("video")) {
			return GWT.getModuleBaseURL() + "images/video_icon.png";
		} else if(type.startsWith("audio")) {
			return GWT.getModuleBaseURL() + "images/audio_icon.png";
		} else if (type.equals("image/png") || type.equals("image/jpeg")) {
			if (imageUrl.startsWith("/file/serve")) {
				return imageUrl;
			} else {
				return GWT.getModuleBaseURL() + "images/image_icon.png";
			}
		} else if(type.startsWith("image")) {
			return GWT.getModuleBaseURL() + "images/image_icon.png";
		} else {
			return GWT.getModuleBaseURL() + "images/file_icon.png";
		}
	}
	
	public void setListener(final FileEventListener listener) {
		Element container = (Element) $(getRootElement()).find(".fileItemImageContainer").get(0);
		
		Event.sinkEvents(container, Event.ONCLICK);
		Event.setEventListener(container, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				if (listener != null) {
					listener.onSelected();
				}
			}
		});
	}
}
