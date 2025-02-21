package com.lorepo.iceditor.client.actions;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.module.addon.AddonPreview;
import com.lorepo.iceditor.client.module.api.IEditorServices;
import com.lorepo.icf.properties.IListProperty;
import com.lorepo.icf.properties.IProperty;
import com.lorepo.icf.properties.IPropertyProvider;
import com.lorepo.icf.utils.JavaScriptUtils;
import com.lorepo.icplayer.client.model.ModuleList;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.addon.AddonModel;
import com.lorepo.icplayer.client.module.addon.AddonPresenter;
import com.lorepo.icplayer.client.module.api.IModuleModel;
import com.lorepo.icplayer.client.module.api.player.IPage;
import com.lorepo.icplayer.client.module.IWCAGModuleModel;
import com.google.gwt.core.client.JavaScriptObject;

public class AddAllTextToSpeechAction extends AbstractAction{
	
	public class modelWrapper {
		public String area;
		public IModuleModel model;
		
		modelWrapper(IModuleModel model, String area){
			this.area = area;
			this.model = model;
		}
		
		public String toString() {
			return model.getId() + "\n" + area;
		}
		
		public String getId() {
			return this.model.getId();
		}
		
	}
	public AddAllTextToSpeechAction(AppController controller) {
		super(controller);
	}
	
	@Override
	public void execute() {
		execute(this.getCurrentPage());
	}
	
	public void execute(Page page) {
		IListProperty configuration = this.getTTSConfiguration(page);
		if(configuration == null) return;
		
		List<modelWrapper> headerItems = new ArrayList<modelWrapper>();
		if (page.hasHeader()) {
			IPage header = this.getServices().getModel().getCommonPageById(page.getHeaderId());
			if (header == null) {
				header = this.getServices().getModel().getDefaultHeader();
			}
			if (header != null && header instanceof Page) {
				Page headerPage = (Page) header;
				ModuleList headerModuleList = headerPage.getModules();
				headerItems = getWrapperModels(headerModuleList, "Header");
				
			}
		}
		
		List<modelWrapper> footerItems = new ArrayList<modelWrapper>();
		if (page.hasFooter()) {
			IPage footer = this.getServices().getModel().getCommonPageById(page.getFooterId());
			if (footer == null) {
				footer = this.getServices().getModel().getDefaultFooter();
			}
			
			if(footer != null && footer instanceof Page){
				Page footerPage = (Page) footer;
				ModuleList footerModuleList = footerPage.getModules();
				footerItems = getWrapperModels(footerModuleList, "Footer");
			}
		}
		List<modelWrapper> items = new ArrayList<modelWrapper>();
		
		ModuleList mainModuleList = page.getModules();
		List<modelWrapper> mainItems = getWrapperModels(mainModuleList, "Main");
		items.addAll(headerItems);
		items.addAll(mainItems);
		items.addAll(footerItems);
		
		addChildren(configuration, items);
	}
	
	private void addChild(IListProperty property, String id, String area, String title){
		property.addChildren(1);
		IPropertyProvider child = property.getChild(property.getChildrenCount() - 1);
		for(int i = 0; i < child.getPropertyCount(); i++){
			IProperty field = child.getProperty(i);
			if(field.getName().equals("ID")){
				field.setValue(id);
			} else if(field.getName().equals("Area")){
				field.setValue(area);
			} else if(field.getName().equals("Title")){
				field.setValue(title);
			}
		}
	}
	
	private List<modelWrapper> getWrapperModels(ModuleList moduleList, String area ){
		ArrayList<modelWrapper> list = new ArrayList<modelWrapper>();
		for(int i = 0; i < moduleList.size(); i++){
			list.add(new modelWrapper(moduleList.get(i), area));
		}
		return list;
	}
	
	private void addChildren(IListProperty list, List<modelWrapper> items) {
		HashMap<String,String> titles = new HashMap<String,String>();
		
		for(int i=0; i<list.getChildrenCount(); i++){
			IPropertyProvider child = list.getChild(i);
			String id = null;
			String area = null;
			String title = "";
			for(int j = 0; j < child.getPropertyCount(); j++){
				IProperty field = child.getProperty(j);
				if(field.getName() == "ID") {
					id = field.getValue();
				} else if(field.getName() == "Area"){
					area = field.getValue();
				}else if(field.getName() == "Title"){
					title = field.getValue();
				}
			}
			if(id != null && area != null){
				titles.put(id + "\n" + area, title);
			}
		}
		
		clearListProperty(list);
		
		for (int i = 0; i < items.size(); i++){
			modelWrapper newItem = items.get(i);
			
			if(!isWCAGSupported(newItem.model)) continue;
			
			String title = "";
			if (titles.containsKey(newItem.toString())){
				title = titles.get(newItem.toString());
			}
			addChild(list, newItem.getId(), newItem.area, title);
		}
		
		list.removeChildren(0);
	}
	
	private IListProperty getTTSConfiguration(Page page){
		ModuleList modules = page.getModules();
		IModuleModel ttsModel = modules.getModuleById("Text_To_Speech1");
		
		if (ttsModel == null) {
			return null;
		}
		
		IProperty configuration = null;
		for(int i = 0; i < ttsModel.getPropertyCount(); i++){
			if(ttsModel.getProperty(i).getName().equals("configuration")){
				configuration = ttsModel.getProperty(i);
				break;
			}
		}
		if (configuration == null){
			return null;
		}
		
		if(configuration instanceof IListProperty){
			return (IListProperty) configuration;
		} else return null;
		
	}

	private boolean isWCAGSupported(IModuleModel model) {
		if(model instanceof AddonModel){
			IEditorServices services = this.getAppFrame().getPresentation().getEditorServices();
			AddonPreview addonPreview = new AddonPreview((AddonModel) model, services);
			AddonModel aModel = (AddonModel) model;
			return AddonPresenter.isButton(aModel.getAddonId()) || isAddonSupportingWCAG(addonPreview.getPresenterObject());
		}
		
		return model instanceof IWCAGModuleModel;
	}

	private native boolean isAddonSupportingWCAG(JavaScriptObject presenter) /*-{
        return presenter.hasOwnProperty('setWCAGStatus') || presenter.hasOwnProperty('speechTexts');
    }-*/;

	private void clearListProperty(IListProperty list){
		int size = list.getChildrenCount();
		list.addChildren(1);
		for(int i = 0; i < size; i++){
			list.removeChildren(0);
		}
	}
	
	

}
