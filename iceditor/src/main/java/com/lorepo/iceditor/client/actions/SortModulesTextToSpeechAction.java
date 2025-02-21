package com.lorepo.iceditor.client.actions;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.icf.properties.IListProperty;
import com.lorepo.icf.properties.IProperty;
import com.lorepo.icf.properties.IPropertyProvider;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.ModuleList;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.api.IModuleModel;

public class SortModulesTextToSpeechAction extends AbstractPageAction{
	
	Page page = null;
	Page footer = null;
	Page header = null;
	
	public SortModulesTextToSpeechAction(AppController controller) {
		super(controller);
	}

	class ModuleWrapper {
		private int left = 0;
		private int top = 0;
		private String title = "";
		private String area = "";
		private int areaIndex = 3;
		private String id = "";
		
		public ModuleWrapper(String id, String title, String area, int left, int top) {
			this.left = left;
			this.top = top;
			this.title = title;
			this.area = area;
			this.id = id;
			if (area.toLowerCase().equals("header")) areaIndex = 0;
			if (area.toLowerCase().equals("main")) areaIndex = 1;
			if (area.toLowerCase().equals("footer")) areaIndex = 2;
		}
		
		public int getLeft() {
			return left;
		}
		
		public int getTop() {
			return top;
		}
		
		public String getTitle() {
			return title;
		}
		
		public String getArea() {
			return area;
		}
		
		public int getAreaIndex() {
			return areaIndex;
		}
		
		public String getId() {
			return id;
		}
	}
	
	class ModuleWrapperComparator {
		boolean sortRightToLeft;
		
		public ModuleWrapperComparator(boolean sortRightToLeft){
			this.sortRightToLeft = sortRightToLeft;
		}
		
		private int compare(ModuleWrapper arg0, ModuleWrapper arg1) {
			if (arg0.getAreaIndex() < arg1.getAreaIndex()) {
				return -1;
			}
			
			if (arg0.getAreaIndex() > arg1.getAreaIndex()) {
				return 1;
			}
			
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
		
		public List<ModuleWrapper> sort(List<ModuleWrapper> wrappedModules) {
			List<ModuleWrapper> result = new ArrayList<ModuleWrapper>();
			for (ModuleWrapper module: wrappedModules) {
				boolean inserted = false;
				for (int i=0 ; i < result.size(); i++) {
					if (this.compare(module, result.get(i)) < 0) {
						result.add(i, module);
						inserted = true;
						break;
					}
				}
				if (!inserted) result.add(module);
			}
			return result;
		}
		
	}
	
	@Override
	public void execute() {
		execute(this.getCurrentPage());
	}
	
	public void execute(Page page) {
		Content content = this.getServices().getModel();
		this.page = page;
		this.footer = content.getCommonPageById(this.page.getFooterId());
		if(this.footer == null) {
			this.footer = content.getDefaultFooter();
		}
		this.header = content.getCommonPageById(this.page.getHeaderId());
		if(this.header == null) {
			this.header = content.getDefaultHeader();
		}
		
		IListProperty configuration = this.getTTSConfiguration(this.page);
		if(configuration == null) return;
		
		List<ModuleWrapper> wrappedModules = new ArrayList<ModuleWrapper>();
		
		for(int j=0; j<configuration.getChildrenCount();j++){
			IPropertyProvider child = configuration.getChild(j);
			String area = "Main";
			String title = "";
			String id = "";
			for(int i = 0; i < child.getPropertyCount(); i++){
				IProperty field = child.getProperty(i);
				if(field.getName().equals("ID")){
					id = field.getValue();
				} else if(field.getName().equals("Area")){
					area = field.getValue();
				} else if(field.getName().equals("Title")){
					title = field.getValue();
				}
			}
			ModuleWrapper wrapper = null;
			IModuleModel model = getModule(id, area);
			if (model != null) {
				HashMap<String,Integer> modulePosition = getModulePosition(this.page, model);
				wrapper = new ModuleWrapper(model.getId(), title, area, modulePosition.get("left"), modulePosition.get("top"));
			} else {
				wrapper = new ModuleWrapper(id, title, area, 99999, 99999);
			}
			wrappedModules.add(wrapper);
		}
		
		boolean sortRightToLeft = Boolean.valueOf(content.getMetadataValue("sortRightToLeft"));
		ModuleWrapperComparator comparator = new ModuleWrapperComparator(sortRightToLeft);
		wrappedModules = comparator.sort(wrappedModules);
		
		clearListProperty(configuration);	
		for (int i = 0; i < wrappedModules.size(); i++) {
			addChild(configuration,wrappedModules.get(i));
		}		
		if (wrappedModules.size()>0){
			configuration.removeChildren(0);
		}
	}
	
	private IModuleModel getModule(String Id, String area) {
		Page areaPage = this.page;
		if (area.toLowerCase().equals("footer") && this.footer != null) {
			areaPage = footer;
		} else if (area.toLowerCase().equals("header") && this.header != null) {
			areaPage = header;
		}
		return areaPage.getModules().getModuleById(Id);
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
	
	private HashMap<String,Integer> getModulePosition(Page page, IModuleModel module) {
		try {
			return this.getAppFrame().getPresentation().calculatePosition(page.getId(), module);
		} catch (Exception e) {
			HashMap<String,Integer> result = new HashMap<String,Integer>();
			result.put("top", module.getTop());
			result.put("left", module.getLeft());
			return result;
		}
	}
	
	private void clearListProperty(IListProperty list){
		int size = list.getChildrenCount();
		list.addChildren(1);
		for(int i = 0; i < size; i++){
			list.removeChildren(0);
		}
	}
	
	private void addChild(IListProperty property, ModuleWrapper wrapperModule){
		property.addChildren(1);
		IPropertyProvider child = property.getChild(property.getChildrenCount() - 1);
		for(int i = 0; i < child.getPropertyCount(); i++){
			IProperty field = child.getProperty(i);
			if(field.getName().equals("ID")){
				field.setValue(wrapperModule.getId());
			} else if(field.getName().equals("Area")){
				field.setValue(wrapperModule.getArea());
			} else if(field.getName().equals("Title")){
				field.setValue(wrapperModule.getTitle());
			}
		}
	}
	
}

