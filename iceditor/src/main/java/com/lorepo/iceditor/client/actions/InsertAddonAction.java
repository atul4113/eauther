package com.lorepo.iceditor.client.actions;

import com.google.gwt.user.client.Window;
import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.module.properties.ModuleDefaultPropertiesService;
import com.lorepo.iceditor.client.semi.responsive.SemiResponsiveDangeredAddons;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationType;
import com.lorepo.icf.utils.ILoadListener;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.addonsLoader.AddonLoaderFactory;
import com.lorepo.icplayer.client.addonsLoader.IAddonLoader;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.addon.AddonDescriptor;
import com.lorepo.icplayer.client.model.addon.AddonEntry;
import com.lorepo.icplayer.client.model.addon.AddonProperty;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.addon.AddonModel;
import com.lorepo.icplayer.client.module.addon.param.AddonParamFactory;
import com.lorepo.icplayer.client.module.addon.param.EditableSelectAddonParam;
import com.lorepo.icplayer.client.module.addon.param.IAddonParam;
import com.lorepo.icplayer.client.module.addon.param.ListAddonParam;
import com.lorepo.icplayer.client.module.addon.param.StaticListAddonParam;
import com.lorepo.icplayer.client.module.addon.param.StaticRowAddonParam;

public class InsertAddonAction extends AbstractAction {
	private final AddonEntry entry;
	private final AppController appController;
	private final AppFrame appFrame;

	public InsertAddonAction(AppController controller, AddonEntry entry) {
		super(controller);
		this.entry = entry;
		this.appController = controller;
		this.appFrame = appController.getAppFrame();
	}

	@Override
	public void execute() {
		final Page page = appController.getCurrentPage();
		if (page == null) {
			return; // Action triggered while chapter is selected
		}

		Content model = this.getModel();
		if (this.is_semi_responsive(entry.getId()) && model.isSemiResponsiveContent()) {
			this.show_semi_responsive_warning_message();
		}
		
		perform_insert_addon(page);
	}

	private void show_semi_responsive_warning_message() {
		this.getNotifications().addMessage(DictionaryWrapper.get("semi_responsive_addon_warning"), NotificationType.warning, true);
	}

	private boolean is_semi_responsive(String id) {
		String lowercaseID = id.toLowerCase();
		return SemiResponsiveDangeredAddons.addons.contains(lowercaseID);
	}

	private void perform_insert_addon(final Page page) {
		Content content = this.getModel();
		if (content.addonIsLoaded(entry.getId())) {
			onDescriptorLoaded(appController, page, content.getAddonDescriptors().get(entry.getId()));
		} else {
			final AddonDescriptor descriptor = new AddonDescriptor(entry.getId(), entry.getDescriptorURL());
			final IAppController appController = getServices().getAppController();
			AddonLoaderFactory addonLoader = new AddonLoaderFactory(this.getServices().getModel().getBaseUrl());
			IAddonLoader loader = addonLoader.getAddonLoader(descriptor);
			loader.load(new ILoadListener() {
				@Override
				public void onFinishedLoading(Object obj) {
					onDescriptorLoaded(appController, page, descriptor);
				}

				@Override
				public void onError(String error) {
					Window.alert(DictionaryWrapper.get("error_loading_addon") + descriptor.getHref());
				}
			});
		}
	}

	private void onDescriptorLoaded(IAppController appController, Page page, AddonDescriptor descriptor) {
		insertAddonIntoContent(descriptor);
		insertAddonIntoPage(descriptor);

		appController.saveCurrentPageAndContent();
		appController.getUndoManager().add(page.toXML());
	}

	private void insertAddonIntoContent(AddonDescriptor descriptor) {
		appController.addAddon(descriptor);

		Content content = getServices().getModel();
		content.getAddonDescriptors().put(descriptor.getAddonId(), descriptor);
	}

	private void insertAddonIntoPage(AddonDescriptor descriptor) {
		Page page = appController.getCurrentPage();
		AddonModel addonModel = insertAddonIntoPage(page, descriptor, appController, appFrame);
		getServices().getAppController().getActionFactory().getSingleModuleSelectedAction().execute(addonModel);
	}

	public static AddonModel insertAddonIntoPage(Page page, AddonDescriptor descriptor, AppController appController, AppFrame appFrame) {

		final int offsetTop = appFrame.getPresentation().getPageScrollTopPosition();
		int top = offsetTop + 10;

		if (offsetTop < 10) {
			top = 10;
		}
		AddonModel module = new AddonModel();
		if(!isAddToDrag()){
			module.setLeft(10);
			module.setTop(top);
		}
		module.setWidth(100);
		module.setHeight(100);
		module.setAddonId(descriptor.getAddonId());

		for (AddonProperty property: descriptor.getProperties()) {
			if (property.getType().compareTo("list") == 0) {
				module.addAddonParam(createListAddonParam(module, property));
			} else if (property.getType().compareTo("staticlist") == 0) {
				module.addAddonParam(createStaticListAddonParam(module, property));
			} else if (property.getType().compareTo("editableselect") == 0) {
				module.addAddonParam(createEditableSelectAddonParam(module, property));
			} else {
				module.addAddonParam(property.getName(), property.getDisplayName(), property.getType());
			}
		}
		ModuleDefaultPropertiesService.setProperties(module);
		
		module.setId(page.createUniquemoduleId(module.getAddonId()));
		
		page.getModules().add(module);
		appFrame.getPresentation().refreshView();
		appFrame.getModules().setPage(page);

		appFrame.setModule(module);
		return module;
	}

	private static IAddonParam createEditableSelectAddonParam(AddonModel module, AddonProperty property) {
		AddonParamFactory factory = new AddonParamFactory();
		EditableSelectAddonParam selectParam = new EditableSelectAddonParam(module, "editableselect", factory);
		selectParam.setDisplayName(property.getDisplayName());
		selectParam.setName(property.getName());

		for (int i = 0; i < property.getChildrenCount(); i++) {
			AddonProperty child = property.getProperty(i);
			IAddonParam param = createAddonParam(module, child);
			param.setName(child.getName());
			param.setDisplayName(child.getDisplayName());
			selectParam.addOptions(param, child.getType());
		}

		return selectParam;
	}

	private static IAddonParam createListAddonParam(AddonModel module, AddonProperty property) {

		AddonParamFactory factory = new AddonParamFactory();
		ListAddonParam listParam = new ListAddonParam(module, "list", factory);
		listParam.setName(property.getName());
		listParam.setDisplayName(property.getDisplayName());

		for (int i = 0; i < property.getChildrenCount(); i++) {
			AddonProperty child = property.getProperty(i);
			IAddonParam param = createAddonParam(module, child);
			param.setName(child.getName());
			param.setDisplayName(child.getDisplayName());
			listParam.addToTemplate(param);
		}

		listParam.addNewItems(1);
		return listParam;
	}

	private static IAddonParam createStaticRowAddonParam(AddonModel module, AddonProperty property) {
		AddonParamFactory factory = new AddonParamFactory();
		StaticRowAddonParam param = (StaticRowAddonParam) factory.createAddonParam(module, property.getType());
		param.setName(property.getName());
		param.setDisplayName(property.getDisplayName());
		for (int i = 0; i < property.getChildrenCount(); i++) {
			AddonProperty child = property.getProperty(i);

			IAddonParam addonParam = createAddonParam(module, child);
			addonParam.setName(child.getName());
			addonParam.setDisplayName(child.getDisplayName());
			param.addToTemplate(addonParam);
		}

		return param;
	}

	private static IAddonParam createStaticListAddonParam(AddonModel module, AddonProperty property) {

		AddonParamFactory factory = new AddonParamFactory();
		StaticListAddonParam listParam = new StaticListAddonParam(module, "staticlist", factory);
		listParam.setName(property.getName());
		listParam.setDisplayName(property.getDisplayName());

		for (int i = 0; i < property.getChildrenCount(); i++) {
			AddonProperty child = property.getProperty(i);
			if (child.getType().trim().toLowerCase().compareTo("staticrow") == 0) {
				IAddonParam addonParam = createStaticRowAddonParam(module, child);
				listParam.addToTemplate(addonParam);


			}

		}
		listParam.addNewItems(1);
		return listParam;
	}

	private static IAddonParam createAddonParam(AddonModel module, AddonProperty property) {
		if (property.getType().trim().toLowerCase().compareTo("editableselect") == 0) {
			return createEditableSelectAddonParam(module, property);
		} else {
			AddonParamFactory factory = new AddonParamFactory();
			return factory.createAddonParam(module, property.getType());
		}
	}

	public static native boolean isAddToDrag() /*-{
		return $wnd.isAddToDragAction();
	}-*/;

}
