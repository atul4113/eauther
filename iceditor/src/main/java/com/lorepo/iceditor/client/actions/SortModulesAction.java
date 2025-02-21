package com.lorepo.iceditor.client.actions;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

import com.google.gwt.dom.client.Element;
import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.widgets.modules.ModulesWidget;

import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.ModuleList;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.api.IModuleModel;

public class SortModulesAction extends AbstractPageAction{
	public SortModulesAction(AppController controller) {
		super(controller);
	}
	
	class ModuleWrapper {
		int left = 0;
		int top = 0;
		IModuleModel model;
		
		public ModuleWrapper(IModuleModel model) {
			this.left = model.getLeft();
			this.top = model.getTop();
			this.model = model;
		}
		
		public ModuleWrapper(IModuleModel model, int left, int top) {
			this.left = left;
			this.top = top;
			this.model = model;
		}
		
		public int getLeft() {
			return left;
		}
		
		public int getTop() {
			return top;
		}
		
		public IModuleModel getModel() {
			return model;
		}
	}
	
	class ModuleWrapperComparator implements Comparator<ModuleWrapper> {
		boolean sortRightToLeft;
		public ModuleWrapperComparator(boolean sortRightToLeft){
			this.sortRightToLeft = sortRightToLeft;
		}

		@Override
		public int compare(ModuleWrapper arg0, ModuleWrapper arg1) {
			
			if (arg0.getTop() < arg1.getTop()) {
				return -1;
			}
			if (arg0.getTop() > arg1.getTop()) {
				return 1;
			}
			if (arg0.getLeft() < arg1.getLeft()) {
				if (sortRightToLeft) {
					return 1;
				} else {
					return -1;
				}
			}
			if (arg0.getLeft() > arg1.getLeft()) {
				if (sortRightToLeft) {
					return -1;
				} else {
					return 1;
				}
			}
			return 0;
		}
		
	}

	@Override
	public void execute() {
		IAppController appController = getServices().getAppController();
		AppFrame appFrame = appController.getAppFrame();
		ModulesWidget modules = appFrame.getModules();
		Page selectedPage = getSelectedPage();
		
		ModuleList moduleList = selectedPage.getModules();
		
		List<ModuleWrapper> wrappedModules = new ArrayList<ModuleWrapper>();
		for(int i = 0; i < moduleList.size(); i++) {
			IModuleModel model = moduleList.get(i);
			
			ModuleWrapper wrapper = null;
			int[] dimensions = getXY(appFrame.getContentWrapper().getElement(), model.getId());
			if (dimensions.length == 2) {
				wrapper = new ModuleWrapper(model, dimensions[0], dimensions[1]);
			} else {
				wrapper = new ModuleWrapper(model);
			}
			wrappedModules.add(wrapper);
		}
		
		Content content = this.getModel();
		boolean sortRightToLeft = Boolean.valueOf(content.getMetadataValue("sortRightToLeft"));
	
		Collections.sort(wrappedModules, new ModuleWrapperComparator(sortRightToLeft));
		
		for(int i = 0; i < wrappedModules.size(); i++){
			IModuleModel model = wrappedModules.get(i).getModel();
			moduleList.moveModuleToIndex(model, i);
		}
		
		modules.setPage(selectedPage);
		appFrame.getPresentation().refreshView();
		appController.getUndoManager().add(selectedPage.toXML());
	}
	
	private native int[] getXY(Element content, String moduleID) /*-{
		var $_ = $wnd.$;
		var $container = $_(content).find('.ic_main');
		var $module = $container.find('[data-id="' + moduleID + '"]');
		if ($module.length > 0){
			var left = parseInt($module.css('left'));
			var top = parseInt($module.css('top'));
			return [left, top];
		} else {
			return [];
		}
		
	}-*/;
	
}

