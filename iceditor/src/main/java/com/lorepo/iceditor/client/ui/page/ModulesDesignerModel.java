package com.lorepo.iceditor.client.ui.page;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import com.lorepo.icf.uidesigner.IDesignerModel;
import com.lorepo.icplayer.client.model.IModuleListListener;
import com.lorepo.icplayer.client.model.ModuleList;
import com.lorepo.icplayer.client.model.page.group.Group;
import com.lorepo.icplayer.client.module.api.IModuleModel;


public class ModulesDesignerModel implements IDesignerModel<IModuleModel>{

	private ModuleList modules;
	private IListener<IModuleModel>	listener;
	private boolean isModified = false;
	private List<Group> groups = new ArrayList<Group>();
	
	private IModuleListListener moduleListListener = new IModuleListListener() {
		
		@Override
		public void onModuleRemoved(IModuleModel module) {
			if(listener != null){
				isModified = true;
				listener.onItemRemoved(module);
			}
		}
		
		@Override
		public void onModuleChanged(IModuleModel module) {
			if(listener != null){
				isModified = true;
				listener.onItemChanged(module);
			}
		}
		
		@Override
		public void onModuleAdded(IModuleModel module) {
			if(listener != null){
				isModified = true;
				listener.onItemAdded(module);
			}
		}
	}; 


	public void setModuleList(ModuleList list){
		groups.clear();
		if(modules != null){
			modules.removeListener(moduleListListener);
		}
		this.modules = list;
		modules.addListener(moduleListListener);
		isModified = false;
	}
	
	
	@Override
	public void addListener(IListener<IModuleModel> l){
		this.listener = l;
	}
	
	
	@Override
	public void removeListener(IListener<IModuleModel> l){
		listener = null;
	}
	
	
	@Override
	public IModuleModel getItem(int index) {
		return modules.get(index);
	}


	@Override
	public int getItemsCount() {
		return modules.size();
	}

	
	public boolean isModified(){
		return isModified;
	}

	
	public void setModified(boolean flag){
		isModified = flag;
	}


	@Override
	public void createGroup(List<IModuleModel> group) {
		groups.add((Group) group);
	}


	@Override
	public void removeGroupWithItem(IModuleModel item) {
		for(Group group : groups){
			if(group.contains(item)){
				groups.remove(group);
				break;
			}
		}
	}

	public void removeGroup(Group group) {
		Iterator<Group> i = groups.iterator();
		while (i.hasNext()) {
			Group o = i.next();
		 	if(o.getId().equals(group.getId())) {
		 		i.remove();
		 	}
		}
	}

	@Override
	public Group findGroupByItem(IModuleModel item) {
		Group foundGroup = null;
		for(Group group : groups){
			if(group.contains(item)){
				foundGroup = group;
				break;
			}
		}
		return foundGroup;
	}
}
