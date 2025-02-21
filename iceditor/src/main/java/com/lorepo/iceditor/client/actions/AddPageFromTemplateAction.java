package com.lorepo.iceditor.client.actions;

import java.util.HashMap;

import com.google.gwt.http.client.RequestException;
import com.google.gwt.user.client.Window;
import com.lorepo.iceditor.client.actions.api.IActionService;
import com.lorepo.iceditor.client.actions.api.IServerService.IRequestListener;
import com.lorepo.iceditor.client.semi.SemiResponsiveConfigurationJava;
import com.lorepo.iceditor.client.semi.TranslateImportedPageLayoutsTask;
import com.lorepo.iceditor.client.semi.responsive.SemiResponsiveModificationsHistory;
import com.lorepo.iceditor.client.ui.widgets.pages.select.SelectPageEventListener;
import com.lorepo.iceditor.client.ui.widgets.pages.select.SelectPageWidget;
import com.lorepo.iceditor.client.actions.utils.ActionUtils;
import com.lorepo.icf.utils.ILoadListener;
import com.lorepo.icf.utils.URLUtils;
import com.lorepo.icf.utils.XMLLoader;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.addon.AddonDescriptor;
import com.lorepo.icplayer.client.model.layout.PageLayout;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.api.player.IPage;
import com.lorepo.icplayer.client.xml.IProducingLoadingListener;
import com.lorepo.icplayer.client.xml.page.PageFactory;

public class AddPageFromTemplateAction extends AddPageAction {
	
	final SelectPageWidget selectPage = getServices().getAppController().getAppFrame().getSelectPage();

	public AddPageFromTemplateAction(IActionService service) {
		super(service);
	}
	
	@Override
	public void execute() {
		Content template = getServices().getThemeController().getTheme();
		if (template == null) {
			super.execute();
			return;
		}
		
		selectPage.setTemplate(template);
		selectPage.setEventListener(new SelectPageEventListener() {
			@Override
			public void onPageSelected(IPage page) {
				PageFactory factory = new PageFactory((Page) page);
				factory.load(page.getURL(), new IProducingLoadingListener() {
					
					@Override
					public void onFinishedLoading(Object producedItem) {
						addPage((Page) producedItem);
						getServices().validatePageLimit();
					}
					 
					@Override
					public void onError(String string) {
						getServices().showMessage(DictionaryWrapper.get("Cant_add_page_from_template") + " " + string);
					}
				});
				
			}
		});

		selectPage.show();
	}

	protected String getProperPageUrl(String url) {
		if (url.startsWith("/")) {
			return url;
		} else {
			return getModel().getBaseUrl() + url;
		}
	}
	
	protected void registerAddonDescriptors(Content templateContent, Content currentContent) {
		HashMap<String, AddonDescriptor> templateDescriptors = templateContent.getAddonDescriptors();
		HashMap<String, AddonDescriptor> currentDescriptors = currentContent.getAddonDescriptors();
		
		for (String key: templateDescriptors.keySet()) {
			if (!currentDescriptors.containsKey(key)) {
				loadAddonDescriptor(templateDescriptors.get(key));
			}
		}
	}
	
	protected void loadAddonDescriptor(final AddonDescriptor descriptor) {
		XMLLoader xmlLoader = new XMLLoader(descriptor);
		xmlLoader.load(descriptor.getHref(), new ILoadListener() {
			public void onFinishedLoading(Object obj) {
				getServices().getAppController().addAddon(descriptor);
			}

			public void onError(String error) {
				Window.alert(DictionaryWrapper.get("error_loading_addon") + descriptor.getHref());
			}
		});
	}

	protected void markLayoutsAsVisited(String pageID) {
		Content currentContent = getServices().getModel();
		for (PageLayout layout : currentContent.getActualSemiResponsiveLayouts()){
            SemiResponsiveModificationsHistory.markAsVisited(pageID, layout.getID());
       }
	}
	
	private void addPage(final IPage templatePage) {
		final Content template = getServices().getThemeController().getTheme();
		String baseURL = template.getBaseUrl(); 
		String url = URLUtils.resolveURL(baseURL, templatePage.getURL());

		try {
			getServices().getServerService().addPage(url, new IRequestListener() {		
				@Override
				public void onFinished(final String pageUrl) {
					if (URLUtils.isValidUrl(pageUrl)) {						
						Content currentContent = getServices().getModel();
						registerAddonDescriptors(template, currentContent);
						
						Page newPage = new Page("", "");
						
						PageFactory factory = new PageFactory(newPage);
						factory.produce(templatePage.toXML(), "");
						ActionUtils.ensureUniquePageId(newPage, currentContent);

						// translate semiresponsive layouts to layouts of current page
						SemiResponsiveConfigurationJava templateConfiguration = new SemiResponsiveConfigurationJava(template.getActualSemiResponsiveLayouts());
						TranslateImportedPageLayoutsTask task = new TranslateImportedPageLayoutsTask();
						newPage = task.execute(templateConfiguration, newPage, currentContent.getActualSemiResponsiveLayouts());
						
						// save page with translated layouts 
						getServices().getServerService().saveFile(getProperPageUrl(pageUrl), newPage.toXML(), new IRequestListener() {			
							@Override
							public void onFinished(String responseText) {
								Page p1 = addPage(pageUrl);
								
								markLayoutsAsVisited(p1.getId());								
								
								getServices().getAppController().getAppFrame().getPages().refresh();
								getServices().getAppController().getAppFrame().getPages().setSelectedNode(p1);

								p1.setReportable(templatePage.isReportable());
								 
								selectPage.hide();
							}
							
							@Override
							public void onError(int server_error) {
								getServices().showMessage(DictionaryWrapper.get("cant_add_page") + "Can't save page at URL: \n" + pageUrl);
							}
						});
					} else {
						getServices().showMessage(DictionaryWrapper.get("cant_add_page") + "Server returned wrong URL: \n" + pageUrl);
					}
				}
				
				@Override
				public void onError(int server_error) {
					getServices().getAppController().serverErrorMessage(server_error, "cant_add_page");
				}
			}); 
		} catch (RequestException e) {
			getServices().showMessage(e.toString());
		}
	}
}
