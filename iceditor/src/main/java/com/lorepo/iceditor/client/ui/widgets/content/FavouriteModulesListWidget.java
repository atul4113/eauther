package com.lorepo.iceditor.client.ui.widgets.content;

import java.util.HashMap;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.AnchorElement;
import com.google.gwt.dom.client.HeadingElement;
import com.google.gwt.dom.client.SpanElement;
import com.google.gwt.dom.client.Style.Display;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.ui.dlg.ModuleInfo;
import com.lorepo.iceditor.client.ui.widgets.modules.add.ModulesInfoUtils;
import com.lorepo.iceditor.client.ui.widgets.utils.MainPageUtils;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;

public class FavouriteModulesListWidget extends Composite {

	private static FavouriteModulesListWidgetUiBinder uiBinder = GWT
			.create(FavouriteModulesListWidgetUiBinder.class);

	interface FavouriteModulesListWidgetUiBinder extends
			UiBinder<Widget, FavouriteModulesListWidget> {
	}

	@UiField HTMLPanel panel;
	@UiField AnchorElement save;
	@UiField AnchorElement apply;
	@UiField HeadingElement title;
	@UiField SpanElement info;
	
	private ModulesInfoUtils modulesInfoUtils;
	private FavouriteModulesPanelWidget favouriteModulesPanel = new FavouriteModulesPanelWidget();
	
	public FavouriteModulesListWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		panel.getElement().setId("favouriteModulesPage");
		info.setId("infoMaxItems");
		addFavouriteModulesPanel();
		
		updateElementsTexts();
		hide();
	}
	
	public void show() {
		MainPageUtils.show(panel);
		MainPageUtils.addScrollBar("#favouriteModulesPanel");
	}
	
	public void hide() {
		panel.getElement().getStyle().setDisplay(Display.NONE);
		WidgetLockerController.hide();
	}
	
	public void setListener(final MainPageEventListener listener) {
		Event.sinkEvents(save, Event.ONCLICK);
		Event.setEventListener(save, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				listener.onSave();
			}
		});

		Event.sinkEvents(apply, Event.ONCLICK);
		Event.setEventListener(apply, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				listener.onApply();
			}
		});
	}
	
	public void updateElementsTexts() {
		info.setInnerText(DictionaryWrapper.get("select_max_10_items"));
		title.setInnerText(DictionaryWrapper.get("select_fav_modules"));
		save.setInnerText(DictionaryWrapper.get("save"));
		apply.setInnerText(DictionaryWrapper.get("apply"));
	}
	
	public FavouriteModulesPanelWidget getFavouriteModulesPanel() {
		return favouriteModulesPanel;
	}

	private void addFavouriteModulesPanel() {
		panel.add(favouriteModulesPanel);
	}
	
	public HashMap<String, ModuleInfo> getFavouriteModules() {
		return favouriteModulesPanel.getFavouriteModules();
	}

	public void setModulesInfoUtils(ModulesInfoUtils modulesInfoUtils) {
		this.modulesInfoUtils = modulesInfoUtils;
	}

	public void setFavouriteModules(HashMap<String, ModuleInfo> favouriteModules) {
		favouriteModulesPanel.setFavouriteModules(favouriteModules, modulesInfoUtils.getTranslatedAddonsAndModules());
	}
}
