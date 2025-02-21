package com.lorepo.iceditor.client.ui.widgets.content;

import static com.google.gwt.query.client.GQuery.$;

import com.google.gwt.core.client.GWT;
import com.google.gwt.query.client.Function;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.widgets.utils.MainPageUtils;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.api.IModuleModel;

public class AddWCAGItemWidget extends Composite {

	private static ModuleWidgetUiBinder uiBinder = GWT.create(ModuleWidgetUiBinder.class);

	interface ModuleWidgetUiBinder extends UiBinder<Widget, AddWCAGItemWidget> {
	}
	
	@UiField HTMLPanel panel;
	Page page;
	IModuleModel model;
	String error = "";
	boolean isCommon = false;
	AppController appController;

	public AddWCAGItemWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		
		$(getRootElement()).find(".tableCell").on("click", new Function(){
			public void f() {
				if (MainPageUtils.isWindowOpened("addWCAGPage")) {
					moveToModule();
				}
			}
		});
		
	}

	private Element getRootElement() {
		return panel.getElement();
	}
	
	public void setId(IModuleModel model) {
		this.model = model;
		$(getRootElement()).find(".moduleID").html(model.getId());
	}
	
	public void setIsCommon(boolean isCommon) {
		this.isCommon = isCommon;
		if (page == null) return;
		String pageName = this.page.getName();
		if (this.isCommon) pageName += " (Commons)";
		$(getRootElement()).find(".pageName").html(pageName);
	}
	
	public void setPageName(Page page) {
		this.page = page;
		
		String pageName = this.page.getName();
		if (this.isCommon) pageName += " (Common)";
		$(getRootElement()).find(".pageName").html(pageName);
	}
	
	public void setErrorMessage(String error) {
		this.error = error;
		$(getRootElement()).find(".errorMessage").html(error);
	}
	
	public void setAppController(AppController appController) {
		this.appController = appController;
	}
	
	private void moveToModule() {
		if (appController == null) return;
		if (MainPageUtils.isWindowOpened("addWCAGPage")) {
			appController.getAppFrame().getAddWCAG().hide();
		}
		appController.switchToPage(this.page, true);
		appController.getSelectionController().clearSelectedModules();
		appController.getSelectionController().selectModule(model);
	}
}
