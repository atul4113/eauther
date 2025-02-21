package com.lorepo.iceditor.client.actions;

import java.util.HashMap;
import java.util.Map;

import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.module.properties.ModuleDefaultPropertiesService;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.widgets.content.PresentationWidget;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.ModuleFactory;
import com.lorepo.icplayer.client.module.api.IModuleModel;
import com.lorepo.icplayer.client.module.button.ButtonModule;
import com.lorepo.icplayer.client.module.button.ButtonModule.ButtonType;

public class InsertButtonAction extends AbstractAction{

	private ButtonType buttonType;


	public InsertButtonAction(AppController controller) {
		
		super(controller);
	}

	
	@Override
	public void execute() {
		IAppController appController = getServices().getAppController();
		AppFrame appFrame = appController.getAppFrame();
		PresentationWidget presentation = appFrame.getPresentation();
		
		Page page = appController.getCurrentPage();
		if (page == null) {
			return; // Action triggered while chapter is selected
		}
		
		ModuleFactory moduleFactory = new ModuleFactory(null);
		IModuleModel module = moduleFactory.createModel("buttonModule");
		int offsetTop = presentation.getPageScrollTopPosition();

		if(module instanceof ButtonModule){
			ButtonModule buttonModule = (ButtonModule) module;
			buttonModule.setType(buttonType);
			module.setLeft(10);
			module.setTop(offsetTop+10);
			module.setWidth(50);
			module.setHeight(50);
			String buttonType = getProperButtonName(getButtonType());
			String id = page.createUniquemoduleId(buttonType);
			module.setId(id);
			
			ModuleDefaultPropertiesService.setProperties(module);
			
			page.getModules().add(module);
			
			presentation.refreshView();
			appFrame.getModules().setPage(page);
			appFrame.getProperties().setModule(module);
			appController.saveCurrentPageAndContent();
			appController.getActionFactory().getSingleModuleSelectedAction().execute(module);
		}
	}

	public static String getProperButtonName(String buttonType) {
		final Map<String, String> classNames = new HashMap<String, String>() {
			private static final long serialVersionUID = -3122532703076343298L;
			{
				put("cancel", "ClosePopup");
				put("popup", "OpenPopup");
				put("reset", "Reset");
				put("gotoPage", "GoToPage");
				put("nextPage", "NextPage");
				put("prevPage", "PreviousPage");
			}};
		
		if (classNames.containsKey(buttonType)) {
			return classNames.get(buttonType);
		}
		
		return buttonType;
	}
	
	public String getButtonType() {
		return buttonType.toString();
	}
	
	public void setButtonType(ButtonType type){
		this.buttonType = type;
	}
}
