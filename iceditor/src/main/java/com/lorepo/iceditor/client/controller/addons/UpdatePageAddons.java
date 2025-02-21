package com.lorepo.iceditor.client.controller.addons;

import java.util.HashMap;
import java.util.List;

import com.lorepo.icf.properties.IProperty;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.model.addon.AddonDescriptor;
import com.lorepo.icplayer.client.model.addon.AddonProperty;
import com.lorepo.icplayer.client.module.addon.AddonModel;
import com.lorepo.icplayer.client.module.addon.param.AddonParamFactory;
import com.lorepo.icplayer.client.module.addon.param.IAddonParam;
import com.lorepo.icplayer.client.module.addon.param.ListAddonParam;
import com.lorepo.icplayer.client.module.addon.param.StaticListAddonParam;
import com.lorepo.icplayer.client.module.addon.param.StaticRowAddonParam;
import com.lorepo.icplayer.client.module.api.IModuleModel;

public class UpdatePageAddons {

	private HashMap<String,AddonDescriptor> addonDescriptors;
	private AddonParamFactory addonParamFactory = new AddonParamFactory();
	
	
	public UpdatePageAddons(HashMap<String,AddonDescriptor> descriptors){
		
		this.addonDescriptors = descriptors;
	}
	
	
	public void update(Page page){
		for(IModuleModel module : page.getModules()){
			if(module instanceof AddonModel){
				updateAddon((AddonModel) module);
			}
		}
	}
	
	
	private void updateAddon(AddonModel addon) {

		AddonDescriptor desc = addonDescriptors.get(addon.getAddonId());
		if(desc != null){
			for(AddonProperty addonProperty : desc.getProperties()){
				IProperty property = addon.getPropertyByName(addonProperty.getName());
				if(property == null){
					if(addonProperty.getType().compareTo("list") == 0){
						IAddonParam param = createListAddonParam(addon, addonProperty);
						addon.addAddonParam(param);
					} else if (addonProperty.getType().compareTo("staticlist") == 0){
						addon.addAddonParam(createStaticListAddonParam(addon, addonProperty));						
					} else {
						addon.addAddonParam(addonProperty.getName(), addonProperty.getDisplayName(), addonProperty.getType());
					}
				}
				else if(addonProperty.getType().compareTo("list") == 0){
					updateListProperty(addon, addonProperty);
				}
			}
		}
	}
	
	private void updateListProperty(AddonModel module, AddonProperty addonProperty) {

		ListAddonParam listParam = null;
		List<IAddonParam> addonParams = module.getParams();
		for(IAddonParam param : addonParams){
		
			if(param instanceof ListAddonParam && param.getName().compareTo(addonProperty.getName()) == 0){
				listParam = (ListAddonParam) param;
				break;
			}
		}
		
		if(listParam != null){
		
			for(int i = 0; i < addonProperty.getChildrenCount(); i++){
				AddonProperty child = addonProperty.getProperty(i);
				listParam.addSubPropertyIfNotExists(child, addonParamFactory);
			}
		}
	}


	private IAddonParam createListAddonParam(AddonModel module, AddonProperty addonProperty) {
		
		ListAddonParam listParam = new ListAddonParam(module, "list", addonParamFactory);
		listParam.setName(addonProperty.getName());

		for(int i = 0; i < addonProperty.getChildrenCount(); i++){
		
			AddonProperty child = addonProperty.getProperty(i);
			IAddonParam param = addonParamFactory.createAddonParam(module, child.getType());
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

			IAddonParam addonParam = factory.createAddonParam(module, child.getType());
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
				listParam.addToTemplate(createStaticRowAddonParam(module, child));
			}

		}
		listParam.addNewItems(1);
		return listParam;
	}
}
