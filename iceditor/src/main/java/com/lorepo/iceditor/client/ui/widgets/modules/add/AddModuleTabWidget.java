package com.lorepo.iceditor.client.ui.widgets.modules.add;

import java.util.Collections;
import java.util.Comparator;
import java.util.List;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.ui.dlg.ModuleInfo;
import com.lorepo.iceditor.client.ui.widgets.modules.ModuleSelected;

public class AddModuleTabWidget extends Composite {

	private static AddModuleTabWidgetUiBinder uiBinder = GWT
			.create(AddModuleTabWidgetUiBinder.class);

	interface AddModuleTabWidgetUiBinder extends
			UiBinder<Widget, AddModuleTabWidget> {
	}
	
	@UiField HTMLPanel panel;

	public AddModuleTabWidget() {
		initWidget(uiBinder.createAndBindUi(this));
	}

	public void setModules(List<ModuleInfo> modules, ModuleSelected listener) {
		Collections.sort(modules, new Comparator<ModuleInfo>() {   
		    public int compare(ModuleInfo module1, ModuleInfo module2) {  
		        return module1.name.toLowerCase().compareTo(module2.name.toLowerCase());
		    }
		});
		
		for (ModuleInfo module : modules) {
			AddModuleItmWidget moduleWidget = new AddModuleItmWidget();
			moduleWidget.setModule(module, listener);
			panel.add(moduleWidget);
		}
	}

	public void setCategoryName(String category) {
		panel.getElement().setAttribute("category-name", category);
	}
}
