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
import com.lorepo.iceditor.client.ui.widgets.modules.ModuleSelected;

public class AddModuleItmWidget extends Composite {

	private static AddModuleItmWidgetUiBinder uiBinder = GWT
			.create(AddModuleItmWidgetUiBinder.class);

	interface AddModuleItmWidgetUiBinder extends
			UiBinder<Widget, AddModuleItmWidget> {
	}
	
	@UiField HTMLPanel panel;

	public AddModuleItmWidget() {
		initWidget(uiBinder.createAndBindUi(this));
	}
	
	private Element getRootElement() {
		return panel.getElement();
	}
	
	private GQuery getImageQueryElement() {
		return $(getRootElement()).find("img");
	}
	
	private GQuery getLabelQueryElement() {
		return $(getRootElement()).find("div");
	}
	
	public void setModule(final ModuleInfo module, final ModuleSelected listener) {
		getLabelQueryElement().html(module.name);
		getImageQueryElement().attr("title", module.info);
		getImageQueryElement().attr("src", module.imageUrl);
		
		panel.addDomHandler(new ClickHandler() {
			@Override
			public void onClick(ClickEvent event) {
				if (module.command != null) {
					module.command.execute();
				}
				
				if (listener != null) {
					listener.onModuleSelected();
				}
			}
		}, ClickEvent.getType());
	}
}
