package com.lorepo.iceditor.client.ui.widgets.modules.add;

import static com.google.gwt.query.client.GQuery.$;

import java.util.HashMap;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.AnchorElement;
import com.google.gwt.dom.client.DivElement;
import com.google.gwt.dom.client.Document;
import com.google.gwt.dom.client.HeadingElement;
import com.google.gwt.dom.client.Style.Display;
import com.google.gwt.query.client.GQuery;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.ui.dlg.ModuleInfo;
import com.lorepo.iceditor.client.ui.widgets.content.WidgetLockerController;
import com.lorepo.iceditor.client.ui.widgets.modules.ModuleSelected;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.iceditor.client.ui.widgets.utils.MainPageUtils;

public class AddModulePageWidget extends Composite {

	private static AddModulePageWidgetUiBinder uiBinder = GWT
			.create(AddModulePageWidgetUiBinder.class);

	interface AddModulePageWidgetUiBinder extends
			UiBinder<Widget, AddModulePageWidget> {
	}
	
	private ModulesInfoUtils moduleInfoUtils = null;
	
	@UiField HTMLPanel panel;
	@UiField DivElement tabs;
	@UiField HTMLPanel contents;
	@UiField HeadingElement addModule;

	public AddModulePageWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		
		panel.getElement().setId("addModulePage");
		
		hide();
		
		updateElementsText();
		
		tabs.setId("addModulePage-tabs");
		contents.getElement().setId("addModulePage-contents");
	}
	
	private void hide() {
		panel.getElement().getStyle().setDisplay(Display.NONE);
	}
	
	private Element getRootElement() {
		return panel.getElement();
	}
	
	public void show() {
		MainPageUtils.show(panel);
		
		GQuery contentTabs = $(getRootElement()).find(".tabContents");
		contentTabs.removeClass("visible");
		contentTabs.get(0).addClassName("visible");
		
		$(getRootElement()).find(".tabButton").removeClass("selected");
		$(getRootElement()).find(".tabButton").get(0).addClassName("selected");
	}
	
	private void createUI() {
		ModuleSelected listener = new ModuleSelected() {
			@Override
			public void onModuleSelected() {
				WidgetLockerController.hide();
				hide();
			}
		};
		
		for(String category : moduleInfoUtils.getCategories()){
			AnchorElement tab = Document.get().createAnchorElement();
			tab.setInnerText(category);
			tab.setClassName("tabButton");
			tab.setAttribute("for-name", category);
			
			tabs.appendChild(tab);
			
			AddModuleTabWidget modulesTab = new AddModuleTabWidget();
			modulesTab.setCategoryName(category);
			modulesTab.setModules(moduleInfoUtils.getCategory(category), listener);
			contents.add(modulesTab);
		}
	}

	public void setModulesInfoUtils(ModulesInfoUtils modulesInfoUtils) {
		this.moduleInfoUtils = modulesInfoUtils;
		
		createUI();
	}
	
	public void updateElementsText() {
		addModule.setInnerText(DictionaryWrapper.get("add_module_title"));
	}

	public void updateFavouriteModulesMenu(HashMap<String, ModuleInfo> favouriteModules) {
		contents.clear();
		tabs.setInnerHTML("");
		
		createUI();
	}
}
