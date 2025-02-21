package com.lorepo.iceditor.client.actions;

import java.util.Iterator;
import java.util.Vector;

import com.google.gwt.xml.client.Document;
import com.google.gwt.xml.client.XMLParser;
import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.actions.api.ISelectionController;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.semi.responsive.SemiResponsiveDangeredAddons;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.widgets.content.WidgetLockerController;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationType;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.ModuleFactory;
import com.lorepo.icplayer.client.module.api.IModuleModel;

public class PasteAction extends AbstractPageAction{
	
	public PasteAction(AppController controller) {
		super(controller);
	}

	@Override
	public void execute() {
		if (WidgetLockerController.isVisible()) {
			return;
		}
		
		IAppController appController = getServices().getAppController();
		AppFrame appFrame = appController.getAppFrame();

		Vector<IModuleModel> modules = new Vector<IModuleModel>();
		Iterator<String> data = getServices().getClipboard().getData();
		ModuleFactory moduleFactory = new ModuleFactory(null);
		Page page = getServices().getAppController().getCurrentPage();
		if (page == null) {
			return; // Action triggered while chapter is selected
		}
		
		if (!data.hasNext()) {
			return; // There were no modules copied
		}
		
		
		boolean warningHasBeenShown = false;
		while (data.hasNext()) {
			String xml = data.next();
			Document dom = XMLParser.parse(xml);
			if(dom.getDocumentElement() != null){
				String moduleNodeName = dom.getDocumentElement().getNodeName();
				IModuleModel module = moduleFactory.createModel(moduleNodeName);
				if(module != null){
					module.load(dom.getDocumentElement(), getSelectedPage().getBaseURL(), Page.version);
					module.disableChangeEvent(true);
					
					String typeName = module.getModuleTypeName();

					if (typeName.equals("Button")) {
						typeName = InsertButtonAction.getProperButtonName(module.getButtonType());
					}
					
					typeName = typeName.replace(" ", "_");
					String id = page.createUniquemoduleId(typeName);
					
					module.setId(id);
					modules.add(module);
					module.disableChangeEvent(false);
					page.getModules().add(module);
					
					String moduleType = module.getModuleTypeName();
					
					Content model = this.getModel();
					if(this.is_semi_responsive(moduleType) && model.isSemiResponsiveContent() && !warningHasBeenShown) {
						this.show_semi_responsive_warning_message();
						warningHasBeenShown = true;
					}
				}
			}
		}
		
		int offsetTop = appFrame.getPresentation().getPageScrollTopPosition();
		int minTop = 10000;
		for (IModuleModel module : modules) {
			if(module.getTop() < minTop){
				minTop = module.getTop();
			}
		}

		int offset = offsetTop - minTop + 10;
		for (IModuleModel module : modules) {
			module.setTop(module.getTop() + offset);
		}
		
		ISelectionController selectionController = appController.getSelectionController();
		selectionController.clearSelectedModules();
		for (IModuleModel module : modules) {
			selectionController.addModule(module);
		}

		appFrame.getModules().setPage(page);
		appFrame.getPresentation().refreshView();
		appController.getUndoManager().add(page.toXML());
		appController.getModyficationController().setModified(true);
	}
	
	private void show_semi_responsive_warning_message() {
		this.getNotifications().addMessage(DictionaryWrapper.get("semi_responsive_addon_warning"), NotificationType.warning, true);
	}

	private boolean is_semi_responsive(String id) {
		String lowercaseID = id.toLowerCase();
		return SemiResponsiveDangeredAddons.addons.contains(lowercaseID);
	}
}
