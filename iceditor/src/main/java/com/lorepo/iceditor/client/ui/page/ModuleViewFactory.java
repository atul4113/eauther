package com.lorepo.iceditor.client.ui.page;

import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.module.addon.AddonPreview;
import com.lorepo.iceditor.client.module.api.IEditorServices;
import com.lorepo.iceditor.client.module.report.ReportPreview;
import com.lorepo.iceditor.client.module.sourcelist.SourceListPreview;
import com.lorepo.iceditor.client.module.text.TextPreview;
import com.lorepo.icf.uidesigner.IItemViewFactory;
import com.lorepo.icplayer.client.module.ModuleFactory;
import com.lorepo.icplayer.client.module.addon.AddonModel;
import com.lorepo.icplayer.client.module.api.IActivity;
import com.lorepo.icplayer.client.module.api.ILayoutDefinition;
import com.lorepo.icplayer.client.module.api.IModuleModel;
import com.lorepo.icplayer.client.module.api.IPresenter;
import com.lorepo.icplayer.client.module.report.ReportModule;
import com.lorepo.icplayer.client.module.sourcelist.SourceListModule;
import com.lorepo.icplayer.client.module.text.TextModel;

public class ModuleViewFactory implements IItemViewFactory<IModuleModel>{

	private ModuleFactory moduleFactory = new ModuleFactory(null);
	private IEditorServices services;
	
	
	public ModuleViewFactory(IEditorServices editorServices) {
		this.services = editorServices;
	}


	@Override
	public ProxyWidget getWidget(IModuleModel item) {
		ProxyWidget widget = new ProxyWidget(item);
		
		if(item instanceof TextModel){
			widget.setInnerWidget(new TextPreview((TextModel) item));
			widget.setMaxScore(this.getTextPresenterMaxScore(item));
		}
		else if(item instanceof ReportModule){
			widget.setInnerWidget(new ReportPreview((ReportModule) item, services));
		}
		else if(item instanceof AddonModel){
			AddonPreview addonPreview = new AddonPreview((AddonModel) item, services);
			widget.setInnerWidget(addonPreview);
			widget.setAddonPreview(addonPreview);
		}
		else if(item instanceof SourceListModule){
			widget.setInnerWidget(new SourceListPreview((SourceListModule) item, services));
		}
		else if(item instanceof IModuleModel){
			
			widget.setInnerWidget((Widget) moduleFactory.createView((IModuleModel) item));
			try{
				IPresenter presenter = moduleFactory.createPresenter((IModuleModel) item);
				IActivity activity = (IActivity) presenter;
				widget.setMaxScore(activity.getMaxScore());
			}catch(Exception e){
			}
		}
		else{
			widget.setInnerWidget(new HTML(item.toString()));
		}
		
		if(item instanceof IModuleModel) {
			if(!item.isModuleInEditorVisible()) {
				widget.addStyleName("ice_module_hide_module_in_editor");
			}	
		}
		
		widget.addStyleName("ice_module");

		setAttributesToWidget(widget, item);
		return widget;
	}
	
	private int getTextPresenterMaxScore(IModuleModel item) {
		IActivity activity = (IActivity) moduleFactory.createPresenter((TextModel) item);
		return activity.getMaxScore();
	}

	/**
	 * This method sets widget's attributes. 
	 * This is only one class where widget is proper representation of module and it is access to manage it
	 * 
	 * As value of attribute is set its module in relation and module's side in relation with it [RelativeTo:side]
	 * 
	 * @param widget - The widget to that attributes are set
	 * @param item - The module with Layout Definition
	 */
	private void setAttributesToWidget(ProxyWidget widget, IModuleModel item) {
		ILayoutDefinition moduleLayout = item.getLayout();

		if (moduleLayout.hasLeft()) {
			widget.getElement().setAttribute("data-relative-left", moduleLayout.getLeftRelativeTo() + ":" + moduleLayout.getLeftRelativeToProperty());
		} else {
			widget.getElement().removeAttribute("data-relative-left");
		}
		
		if (moduleLayout.hasTop()) {
			widget.getElement().setAttribute("data-relative-top", moduleLayout.getTopRelativeTo() + ":" + moduleLayout.getTopRelativeToProperty());
		} else {
			widget.getElement().removeAttribute("data-relative-top");
		}
		
		if (moduleLayout.hasRight()) {
			widget.getElement().setAttribute("data-relative-right", moduleLayout.getRightRelativeTo() + ":" + moduleLayout.getRightRelativeToProperty());
		} else {
			widget.getElement().removeAttribute("data-relative-right");
		}
		
		if (moduleLayout.hasBottom()) {
			widget.getElement().setAttribute("data-relative-bottom", moduleLayout.getBottomRelativeTo() + ":" + moduleLayout.getBottomRelativeToProperty());
		} else {
			widget.getElement().removeAttribute("data-relative-bottom");
		}
	}
}
