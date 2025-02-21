package com.lorepo.iceditor.client.ui.widgets.modules.add;

import static com.google.gwt.query.client.GQuery.$;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.query.client.GQuery;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.ui.dlg.ModuleInfo;

public class AddFavouriteModuleWidget extends Composite {

	private static AddFavouriteModuleWidgetUiBinder uiBinder = GWT
			.create(AddFavouriteModuleWidgetUiBinder.class);

	interface AddFavouriteModuleWidgetUiBinder extends
			UiBinder<Widget, AddFavouriteModuleWidget> {
	}

	@UiField HTMLPanel panel;
	
	public AddFavouriteModuleWidget() {
		initWidget(uiBinder.createAndBindUi(this));
	}

	private Element getRootElement() {
		return panel.getElement();
	}
	
	private GQuery getImageQueryElement() {
		return $(getRootElement()).find("img");
	}
	
	public void setModule(final ModuleInfo module) {
		getImageQueryElement().attr("src", module.imageUrl);
		
		panel.addDomHandler(new ClickHandler() {
			@Override
			public void onClick(ClickEvent event) {
				if (module.command != null) {
					module.command.execute();
				}
			}
		}, ClickEvent.getType());
		
		setToolTip(module.name);
	}
	
	private void setToolTip(String name) {
		getRootElement().setAttribute("data-tooltip", name);
	}
}
