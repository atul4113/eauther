package com.lorepo.iceditor.client.ui.widgets.content;

import java.util.HashMap;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.ui.dlg.ModuleInfo;

public class FavouriteModulesPanelWidget extends Composite {

	private static FavouriteModulesPanelWidgetUiBinder uiBinder = GWT
			.create(FavouriteModulesPanelWidgetUiBinder.class);

	interface FavouriteModulesPanelWidgetUiBinder extends
			UiBinder<Widget, FavouriteModulesPanelWidget> {
	}

	private HashMap<String, FavouriteItemWidget> favouriteWidgets = new HashMap<String, FavouriteItemWidget>();
	HashMap<String, ModuleInfo> allModules = new HashMap<String, ModuleInfo>();
	
	@UiField HTMLPanel panel;     
	
	public FavouriteModulesPanelWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		panel.getElement().setId("favouriteModulesPanel");

	}
	
	public HashMap<String, ModuleInfo> getFavouriteModules() {
		HashMap<String, ModuleInfo> favouriteModules = new HashMap<String, ModuleInfo>();
		
		for (FavouriteItemWidget item : favouriteWidgets.values()) {
			if(item.isFavourite()) {
				favouriteModules.put(item.getOriginalName(), allModules.get(item.getOriginalName()));
			}
		}
		
		return favouriteModules;
	}
	
	public void init(HashMap<String, ModuleInfo> favouriteModules, HashMap<String, ModuleInfo> allModules) {
		for(String name : allModules.keySet()) {
			FavouriteItemWidget item = new FavouriteItemWidget();
			item.getElement().addClassName("favouriteModule");
			item.setName(name, allModules.get(name).name);
			item.setFavourite(favouriteModules.keySet().contains(allModules.get(name).originalName));

			panel.add(item);
			favouriteWidgets.put(name, item);
		}
	}

	public void setFavouriteModules(HashMap<String, ModuleInfo> favouriteModules, HashMap<String, ModuleInfo> allModules) {
		this.allModules = allModules;
		
		if (favouriteWidgets.isEmpty()) {
			init(favouriteModules, allModules);
		} else {
			reset();
		}
	}
	
	private void reset() {
		panel.clear();
		for(FavouriteItemWidget item : favouriteWidgets.values()) {
			panel.add(item);
		}
	}
}