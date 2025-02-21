package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.module.properties.ModuleDefaultPropertiesService;
import com.lorepo.iceditor.client.semi.responsive.SemiResponsiveDangeredAddons;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationType;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.ModuleFactory;
import com.lorepo.icplayer.client.module.api.IModuleModel;

public class InsertModuleAction extends AbstractAction {
	private final String moduleName;

	public InsertModuleAction(AppController controller, String moduleName) {
		super(controller);
		this.moduleName = moduleName;
	}

	@Override
	public void execute() {
		Page page = this.getCurrentPage();
		if (page == null) {
			return; // Action triggered while chapter is selected
		}
		
		Content model = this.getModel();
		if (this.is_semi_responsive(this.moduleName) && model.isSemiResponsiveContent()) {
			this.show_semi_responsive_warning_message();
		}
		
		perform_insert_module(page);
	}

	private void show_semi_responsive_warning_message() {
		this.getNotifications().addMessage(DictionaryWrapper.get("semi_responsive_addon_warning"), NotificationType.warning, true);
	}

	private boolean is_semi_responsive(String id) {
		String lowercaseID = id.toLowerCase();
		return SemiResponsiveDangeredAddons.addons.contains(lowercaseID);
	}

	private void perform_insert_module(Page page) {
		IAppController appController = getServices().getAppController();
		AppFrame appFrame = appController.getAppFrame();

		ModuleFactory moduleFactory = new ModuleFactory(null);

		IModuleModel module = moduleFactory.createModel(moduleName);
		final int offsetTop = appFrame.getPresentation().getPageScrollTopPosition();
		int top = offsetTop + 10;
		
		if (offsetTop < 10) {
			top = 10;
		}
		
		if (module != null) {
			if(!isAddToDrag()){
				module.setLeft(10);
				module.setTop(top);
			}
			module.setWidth(100);
			module.setHeight(100);
			final String typeName = module.getModuleTypeName().replace(" ", "_");
			final String id = page.createUniquemoduleId(typeName);
			module.setId(id);

			ModuleDefaultPropertiesService.setProperties(module);

			page.getModules().add(module);
			
			appFrame.getPresentation().refreshView();
			appFrame.getModules().setPage(page);
			appFrame.getProperties().setModule(module);

			appController.saveCurrentPageAndContent();
			
			if(!isAddToDrag()){
				appController.getUndoManager().add(page.toXML());
			}

			appController.getActionFactory().getSingleModuleSelectedAction().execute(module);
		}
	}
	
	public static native boolean isAddToDrag() /*-{
	  return $wnd.isAddToDragAction();
	}-*/;
}
