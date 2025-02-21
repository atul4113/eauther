package com.lorepo.iceditor.client.actions;

import com.google.gwt.http.client.RequestException;
import com.lorepo.iceditor.client.actions.api.IActionService;
import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.actions.api.IServerService.IRequestListener;
import com.lorepo.iceditor.client.semi.responsive.SemiResponsiveModificationsHistory;
import com.lorepo.iceditor.client.actions.utils.ActionUtils;
import com.lorepo.icf.utils.URLUtils;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.model.page.PageList;

public class DuplicatePageAction extends AbstractAction {

	public DuplicatePageAction(IActionService services) {
		super(services);
	}

	@Override
	public void execute() {
		IAppController appController = getServices().getAppController();
		Page currentPage = appController.getCurrentPage();
		if (currentPage == null) {
			return; // Action triggered while chapter is selected
		}

		duplicatePage(currentPage);
	}
	
	protected void duplicatePage(final Page page) {
			
		try {
			getServices().getServerService().addPage("", new IRequestListener() {
				public void onFinished(String pageUrl) {
					if (URLUtils.isValidUrl(pageUrl)) {
						copyPage(page, pageUrl);
						getServices().validatePageLimit();
					} else {
						getServices().showMessage(DictionaryWrapper.get("cant_add_page") + "Server returned wrong URL: \n" + pageUrl);
					}
				}
				
				public void onError(int server_error) {
					getServices().getAppController().serverErrorMessage(server_error, "cant_add_page");
				}
			}); 
			
		} catch (RequestException e) {
			getServices().showMessage(e.toString());
		}
	}

	protected String getPageXML(Page page) {
		return page.toXML();
	}
	
	private void copyPage(final Page page, final String pageUrl) {
		String xml = getPageXML(page);
		
		String url;
		if (pageUrl.startsWith("/")) {
			url = pageUrl;
		} else {
			url = getModel().getBaseUrl() + pageUrl;
		}
		
		getServices().getServerService().saveFile(url, xml, new IRequestListener() {			
			@Override
			public void onFinished(String responseText) {
				addPage(page, pageUrl);
			}
			
			@Override
			public void onError(int server_error) {
				getServices().getAppController().serverErrorMessage(server_error, "cant_save_duplicate");
			}
		});
	}
	
	protected void setModificationHistory(Page oldPage, Page newPage) {
		SemiResponsiveModificationsHistory.duplicatePage(oldPage.getId(), newPage.getId());
	}

	private void addPage(Page oldPage, String pageUrl) {
		IAppController appController = getServices().getAppController();
		Page currentPage = appController.getCurrentPage();
		PageList chapter = getCurrentChapter();
		
		if(chapter != null){
			Page page = addPageToList(pageUrl, chapter, currentPage);
			this.setModificationHistory(currentPage, page);

			page.setPreview(oldPage.getPreview());
			page.setReportable(oldPage.isReportable());

			appController.switchToPage(page, false);
			appController.saveContent();
		}
	}

	private Page addPageToList(String pageUrl, PageList pages, Page currentPage) {
		int index = pages.indexOf(currentPage) + 1;
		
		String foundName = pages.generateUniquePageName();
		Page page = new Page(foundName, pageUrl);
		ActionUtils.ensureUniquePageId(page, getServices().getModel());
		
		pages.insertBefore(index, page);
		return page;
	}
}
