package com.lorepo.iceditor.client.ui.widgets.content;

import static com.google.gwt.query.client.GQuery.$;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.InputElement;
import com.google.gwt.dom.client.SpanElement;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;

public class FavouriteItemWidget extends Composite {

	private static FavouriteModuleItemWidgetUiBinder uiBinder = GWT
			.create(FavouriteModuleItemWidgetUiBinder.class);

	interface FavouriteModuleItemWidgetUiBinder extends
			UiBinder<Widget, FavouriteItemWidget> {
	}

	@UiField InputElement isFavourite;
	@UiField SpanElement name;
	
	private final int favouritiesLimit = 10;
	private String originalName;
	
	public FavouriteItemWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		connectHandlers();
	}

	public void setName(String originalName, String name) {
		this.name.setInnerText(name);
		this.originalName = originalName;
	}

	public void setFavourite(Boolean isFavourite) {
		this.isFavourite.setChecked(isFavourite);
	}
	
	public boolean isFavourite() {
		return isFavourite.isChecked();
	}

	public String getName() {
		return name.getInnerText();
	}
	
	public String getOriginalName() {
		return originalName;
	}
	
	private void connectHandlers() {		
		Event.sinkEvents(isFavourite, Event.ONCLICK);
		Event.setEventListener(isFavourite, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}

				if ($("#favouriteModulesPanel").find("input:checked").length() > favouritiesLimit) {
					$(isFavourite).attr("checked", false);
				}
			}
		});
	}

}
