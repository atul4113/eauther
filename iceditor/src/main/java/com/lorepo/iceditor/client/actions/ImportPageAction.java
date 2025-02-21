package com.lorepo.iceditor.client.actions;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Set;

import com.google.gwt.core.shared.GWT;
import com.google.gwt.user.client.Window;
import com.lorepo.iceditor.client.actions.api.IActionService;
import com.lorepo.iceditor.client.semi.TranslateImportedPageLayoutsTask;
import com.lorepo.iceditor.client.semi.responsive.SemiResponsiveModificationsHistory;
import com.lorepo.iceditor.client.services.local.storage.LocalStorage;
import com.lorepo.icf.utils.ILoadListener;
import com.lorepo.icf.utils.XMLLoader;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.addon.AddonDescriptor;
import com.lorepo.icplayer.client.model.layout.PageLayout;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.addon.AddonModel;
import com.lorepo.icplayer.client.module.api.IModuleModel;
import com.lorepo.icplayer.client.xml.page.PageFactory;

public class ImportPageAction extends DuplicatePageAction {

	private String pageXML;
	private int addonCount = 0;
	
	public ImportPageAction(IActionService services) {
		super(services);
	}

	@Override
	public void execute() {
		pageXML = LocalStorage.readPageXml();
		
		if(pageXML != null){
			Page page = new Page("", "");
			PageFactory pf = new PageFactory(page);
			pf.produce(pageXML, "");
			page.setPreview(LocalStorage.readPageIcon());
			page.setReportable(LocalStorage.readPageIsReportable().equalsIgnoreCase("true"));
			registerAddons(page);
		}
		else{
			Window.alert(DictionaryWrapper.get("cant_import_page"));
		}
	}

	protected String getPageXML() {
		return pageXML;
	}
	
	protected void setModificationHistory(Page oldPage, Page newPage) {
		String newPageID = newPage.getId();
		for (PageLayout layout : this.getModel().getActualSemiResponsiveLayouts()){
             SemiResponsiveModificationsHistory.markAsVisited(newPageID, layout.getID());
        }
	}
	
	private void registerAddons(Page page) {
		Content content = getServices().getModel();
		HashMap<String, AddonDescriptor> addonDescriptors = content.getAddonDescriptors();
		Set<String> addonIds = new HashSet<String>();
		
		for(IModuleModel module : page.getModules()){
			if(module instanceof AddonModel){
				AddonModel addon = (AddonModel) module;
				if(!addonDescriptors.containsKey(addon.getAddonId())){
					addonIds.add(addon.getAddonId());
				}
				else{
					String url = getServices().getAppController().getAddonURL(addon.getAddonId());
					GWT.log("Addon url: " + url);
				}
			}
		}

		addonCount = addonIds.size();
		if(addonCount > 0){
			for(String id : addonIds){
				loadAddonDescriptor(page, id);
			}
		}
		else{
			insertPage(page);
		}
		
	}
	
	private void insertPage(Page page) {
		Content model = this.getModel();
		
		TranslateImportedPageLayoutsTask task = new TranslateImportedPageLayoutsTask();
		Page translatedPage = task.execute(LocalStorage.readSemiResponsiveConfiguration(), page, model.getActualSemiResponsiveLayouts());
		
		duplicatePage(translatedPage);
	}

	private void loadAddonDescriptor(final Page page, String addonId){

		String url = getServices().getAppController().getAddonURL(addonId);
		final AddonDescriptor descriptor = new AddonDescriptor(addonId, url);
		
		XMLLoader xmlLoader = new XMLLoader(descriptor);
		xmlLoader.load(url, new ILoadListener() {
			public void onFinishedLoading(Object obj) {

				getServices().getAppController().addAddon(descriptor);
				addonCount -= 1;
				if(addonCount == 0){
					insertPage(page);
				}
			}

			public void onError(String error) {
				Window.alert(DictionaryWrapper.get("error_loading_addon") + descriptor.getHref());
			}
		});
	}
}
