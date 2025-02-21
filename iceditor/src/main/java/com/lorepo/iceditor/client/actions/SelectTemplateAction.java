package com.lorepo.iceditor.client.actions;

import java.util.List;
import java.util.Map.Entry;
import java.util.TreeMap;

import com.google.gwt.http.client.RequestException;
import com.google.gwt.user.client.Window;
import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.actions.api.IServerService.IRequestListener;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.widgets.pages.PagesWidget;
import com.lorepo.iceditor.client.ui.widgets.templates.SelectTemplateEventListener;
import com.lorepo.iceditor.client.ui.widgets.templates.SelectTemplateWidget;
import com.lorepo.icf.utils.ILoadListener;
import com.lorepo.icf.utils.URLUtils;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.model.page.PageList;
import com.lorepo.icplayer.client.module.api.player.IContentNode;
import com.lorepo.icplayer.client.module.api.player.IPage;
import com.lorepo.icplayer.client.xml.IProducingLoadingListener;
import com.lorepo.icplayer.client.xml.page.PageFactory;

public class SelectTemplateAction extends AbstractAction{
	
	private SelectTemplateWidget selectTemplate;
	private TreeMap<Integer, Page> loadedPagesInOrder;
	private int pageToLoadCount;
	private int errorCount;
	private AppController appController;
	

	public SelectTemplateAction(AppController controller) {
		super(controller);
		this.appController = controller;
	}

	@Override
	public void execute() {
		selectTemplate = getServices().getAppController().getAppFrame().getSelectTemplate();
		selectTemplate.setThemeURL(getModel().getMetadataValue("theme.href"));
		
		selectTemplate.setEventListener(new SelectTemplateEventListener() {
			@Override
			public void onTemplateSelected(String templateName, String themeURL, boolean replaceCommons) {
				setTemplate(templateName, themeURL, replaceCommons);
			}
		});
		
		selectTemplate.show();
	}

	
	private void setTemplate(final String templateName, String themeURL, final boolean replaceCommons) {
		final IAppController controller = getServices().getAppController();
    	controller.setThemeURL(themeURL, new ILoadListener() {
			@Override
			public void onFinishedLoading(Object obj) {
		    	if (replaceCommons) {
		    		selectTemplate.setSelectedDisabled(true);
		    		replaceHeaders();
		    	}
		    	
		    	getServices().getAppController().getAppFrame().getHeader().setTemplateName(templateName);
				controller.saveContent();
		    	selectTemplate.hide();
			}
			
			@Override
			public void onError(String error) {}
		});
	}

	
	private void replaceHeaders() {
		Content themeContent = getServices().getThemeController().getTheme();
		this.loadedPagesInOrder = new TreeMap<Integer, Page>();
		
		this.removeDuplicatedHeaders(themeContent);
		
		this.pageToLoadCount = themeContent.getHeaders().size() + themeContent.getFooters().size();
		int order = 0;
		
		for (Page headerFromTheme : themeContent.getHeaders()) {
			createCommonPage(headerFromTheme, order);
			order++;
		}
		for (Page footerFromTheme : themeContent.getFooters()) {
			createCommonPage(footerFromTheme, order);
			order++;
		}
	}
	
	private void removeDuplicatedHeaders(Content themeContent) {
		PageList commons = getServices().getModel().getCommonPages();
		
		//removes headers and footers with same names as headers and footers from template
		for (Page headerFromTheme : themeContent.getHeaders()) {
			commons.remove(headerFromTheme.getName());
		}
		
		for (Page footerFromTheme : themeContent.getFooters()) {
			commons.remove(footerFromTheme.getName());
		}
	}

	private void createCommonPage(final IPage page, final int order) {
		
		Content template = getServices().getThemeController().getTheme();
		String baseURL = template.getBaseUrl(); 
		String url = URLUtils.resolveURL(baseURL, page.getURL());
		try {
			getServices().getServerService().addPage(url, new IRequestListener() {
				
				@Override
				public void onFinished(String pageUrl) {
					loadCommonPage(pageUrl, page.getName(), order);
				}
				
				@Override
				public void onError(int server_error) {
					errorCount++;
					Window.alert(DictionaryWrapper.get("Cant_add_page_from_template"));
					getServices().getAppController().serverErrorMessage(server_error, "cant_add_page");
				}
			}); 
			
		} catch (RequestException e) {
			getServices().showMessage(e.toString());
		}
	}

	
	private void loadCommonPage(String pageUrl, String pageName, final int order) {
		final Page page = new Page(pageName, pageUrl);
		String url = URLUtils.resolveURL(getServices().getModel().getBaseUrl(), page.getHref());

		PageFactory factory = new PageFactory(page);
		factory.load(url, new IProducingLoadingListener() {
			@Override
			public void onFinishedLoading(Object producedItem) {
            	onPageLoaded((Page) producedItem, order);
			}

			@Override
			public void onError(String error) {
				errorCount++;
				appController.showLoadingErrorMessage("common page", error);
			}
		});
	}


	
	private void onPageLoaded(Page page, int order) {
		this.loadedPagesInOrder.put(Integer.valueOf(order), page);
		pageToLoadCount--;
		if (pageToLoadCount == 0) {
			this.allLoaded();
		} else if (pageToLoadCount - errorCount == 0) {
			this.selectTemplate.setSelectedDisabled(false);
		}
	}
	
	private void allLoaded() {
		PageList commons = getServices().getModel().getCommonPages();
		
		int i = 0;
		for (Entry<Integer, Page> entry : this.loadedPagesInOrder.entrySet()) {
			commons.addOnIndex(i, entry.getValue());
			i++;
		}
		
		PagesWidget pw = getServices().getAppController().getAppFrame().getPages();
		IContentNode selectedNode = pw.getSelectedNode();
		pw.refresh();
		pw.setSelectedNode(selectedNode);

		getServices().getAppController().saveContent();
		this.selectTemplate.setSelectedDisabled(false);
		this.switchToPage(commons);
	}
	
	private void switchToPage(PageList commons) {
		List<Page> allPages = getServices().getModel().getAllPages();

		Page pageLesson = getServices().getAppController().getCurrentPage();
		
		boolean isCurrentPageInCommons = commons.contains(pageLesson);
		boolean isCurrentPageInAllPages = allPages.contains(pageLesson);
		if (!isCurrentPageInCommons && !isCurrentPageInAllPages) {
			//current page doesn't exist
			pageLesson = getServices().getModel().getAllPages().get(0);
		}
		
		getServices().getAppController().switchToPage(pageLesson, true);
	}
}
