package com.lorepo.iceditor.client.actions;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.google.gwt.dom.client.Element;
import com.google.gwt.user.client.ui.HTML;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.widgets.content.AddWCAGWidget;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationType;
import com.lorepo.icf.properties.IHtmlProperty;
import com.lorepo.icf.properties.IListProperty;
import com.lorepo.icf.properties.IProperty;
import com.lorepo.icf.properties.IPropertyProvider;
import com.lorepo.icf.properties.IStaticListProperty;
import com.lorepo.icf.properties.IStaticRowProperty;
import com.lorepo.icf.utils.URLUtils;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.ModuleList;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.api.IModuleModel;
import com.lorepo.icplayer.client.xml.IProducingLoadingListener;
import com.lorepo.icplayer.client.xml.page.PageFactory;

public class LoadMissingWCAGPropertiesAction extends AbstractAction{
	
	private int correctPageParsedCounter = 0;
	private int errorPageParsedCounter = 0;
	private int pagesSum = 0;
	private AppFrame appFrame;
	private AddWCAGWidget addWCAG;
	
	private List<Page> commonPages = null;
	
	public LoadMissingWCAGPropertiesAction(AppController controller) {
		super(controller);
	}
	
	@Override
	public void execute() {
		
		this.appFrame = getAppFrame();
		this.addWCAG = appFrame.getAddWCAG();
		List<Page> pages = getServices().getModel().getAllPages();
		commonPages = getServices().getModel().getCommonPages().getAllPages();
		pages.addAll(getServices().getModel().getCommonPages().getAllPages());
		correctPageParsedCounter = 0;
		errorPageParsedCounter = 0;
		pagesSum = pages.size();
		
		appFrame.getNotifications().addMessage(DictionaryWrapper.get("Editor_begin_loading_missing_wcag"), NotificationType.notice, false);
		this.addWCAG.clearItemList();
		
		for(int i = 0; i < pages.size(); i++){
			loadAndParsePage(pages.get(i));
		}
	}
	
	private void loadAndParsePage(final Page page){
		if(!page.isLoaded()){	
			Content model = getServices().getModel();

			// Load new page
			String baseUrl = model.getBaseUrl();

			String url = URLUtils.resolveURL(baseUrl, page.getHref());

			PageFactory factory = new PageFactory((Page) page);
			factory.load(url, new IProducingLoadingListener() {
				@Override
				public void onFinishedLoading(Object producedItem) {
					Map<IModuleModel, List<String>> result = getAllModulesWithMissingWCAGProperties(page);
					displayResults(page, result);
					incrementPageParseCounter(true);
				}

				@Override
				public void onError(String error) {
					incrementPageParseCounter(false);
				}
			});
		} else {
			Map<IModuleModel, List<String>> result = getAllModulesWithMissingWCAGProperties(page);
			displayResults(page, result);
			incrementPageParseCounter(true);
		}
	}
	
	public void incrementPageParseCounter(boolean correct){
		if(correct) {
			this.correctPageParsedCounter++;
		} else {
			this.errorPageParsedCounter++;
		}
		if(this.pagesSum <= correctPageParsedCounter + errorPageParsedCounter) {
			if (errorPageParsedCounter == 0){
				appFrame.getNotifications().addMessage(DictionaryWrapper.get("Editor_finish_loading_missing_wcag"), NotificationType.notice, false);
			} else {
				appFrame.getNotifications().addMessage(DictionaryWrapper.get("Editor_finish_loading_missing_wcag_with_errors"), NotificationType.error, false);
			}
		}
	}
	
	private Map<IModuleModel, List<String>> getAllModulesWithMissingWCAGProperties(Page page) {
		ModuleList modules = page.getModules();
		Map<IModuleModel, List<String>> result = new HashMap<IModuleModel,List<String>>();
		for (IModuleModel module: modules) {
			for(int i = 0; i < module.getPropertyCount(); i++){
				IProperty property = module.getProperty(i);
				List<String> missingWCAGProps = searchProperties(property, "");
				if (missingWCAGProps.size() > 0){
					result.put(module, missingWCAGProps);
				}
			}
		}
		return result;
	}
	
	private boolean isUnfinishedWCAGProperty(IProperty property) {
		String name = property.getName().toLowerCase().replaceAll(" ", "");
		if((name.contains("alt") && name.contains("text")) || name.equals("subtitles") || name.equals("audiodescription")){
			return property.getValue().trim().length() == 0;
		} else if (property instanceof IHtmlProperty) {
			HTML propertyContent = new HTML(property.getValue());
			return hasImagesWithoutAlt(propertyContent.getElement());		
		}
		return false;
	}
	
	private List<String> searchProperties(IProperty property, String path) {
		List<String> result = new ArrayList<String>();
		if (property instanceof IListProperty) {
			IListProperty listProp = (IListProperty) property;
			for(int i=0; i<listProp.getChildrenCount(); i++) {
				IPropertyProvider fileProvider = listProp.getChild(i);
				for(int j=0; j < fileProvider.getPropertyCount(); j++) {
					IProperty childProperty = fileProvider.getProperty(j);
					result.addAll(searchProperties(childProperty, path + property.getDisplayName()+"/"));
				}
			};
		}else if (property instanceof IStaticListProperty) {
			IStaticListProperty listProp = (IStaticListProperty) property;
			for(int i=0; i<listProp.getChildrenCount(); i++) {
				IPropertyProvider fileProvider = listProp.getChild(i);
				for(int j=0; j < fileProvider.getPropertyCount(); j++) {
					IProperty childProperty = fileProvider.getProperty(j);
					result.addAll(searchProperties(childProperty, path + property.getDisplayName()+"/"));
				}
			};
		} else if (property instanceof IStaticRowProperty){
			IStaticRowProperty rowProp = (IStaticRowProperty) property;
			for(int i=0; i<rowProp.getChildrenCount(); i++) {
				IPropertyProvider fileProvider = rowProp.getChild(i);
				for(int j=0; j < fileProvider.getPropertyCount(); j++) {
					IProperty childProperty = fileProvider.getProperty(j);
					result.addAll(searchProperties(childProperty, path + property.getDisplayName()+"/"));
				}
			};
			
		}else if (isUnfinishedWCAGProperty(property)){
			result.add(path + property.getDisplayName());
		}
		return result;
	}
	
	private native boolean hasImagesWithoutAlt(Element e)/*-{
		var $_ = $wnd.$;
		var $e = $_(e);
		var $imgs = $e.find('img').filter(function(){
			var $this = $_(this);
			return !$this.attr('alt');
		});
		return $imgs.length > 0;
	}-*/;
	
	private void displayResults(Page page, Map<IModuleModel, List<String>> missingWCAGModules) {
		if(missingWCAGModules == null || missingWCAGModules.size() == 0) return;
		
		for(IModuleModel model: missingWCAGModules.keySet()){
			String error = DictionaryWrapper.get("Editor_wcag_missing");
			List<String> missingProps = missingWCAGModules.get(model);
			for(String prop: missingProps) error += prop + ", ";
			error = error.substring(0, error.length()-2);
			boolean isCommon = this.commonPages.indexOf(page) != -1;
			this.addWCAG.addItemToList(page, model, error, isCommon);
		}
	}
}
