package com.lorepo.iceditor.client.actions;

import com.google.gwt.http.client.RequestException;
import com.lorepo.iceditor.client.actions.api.IActionService;
import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.actions.api.IServerService.IRequestListener;
import com.lorepo.iceditor.client.semi.responsive.SemiResponsiveModificationsHistory;
import com.lorepo.iceditor.client.actions.utils.ActionUtils;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.model.page.PageList;

public class AddPageAction extends AbstractAction{
	private String pageName;
	
	public AddPageAction(IActionService service) {
		super(service);
	}
	
	@Override
	public void execute() {

		String templateUrl = getServices().getThemeController().getPageUrlByNameOrFirst(pageName);

		try {
			getServices().getServerService().addPage(templateUrl, new IRequestListener() {
				@Override
				public void onFinished(String pageUrl) {
					addPage(pageUrl);
					getServices().validatePageLimit();
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

	protected Page addPage(String pageUrl) {
		IAppController appController = getServices().getAppController();
		Page page = null;
		
		PageList chapter = getCurrentChapter();
		
		if (chapter != null) {
			page = addPageToList(pageUrl, chapter);
			
			SemiResponsiveModificationsHistory.addNewPage(page.getId());
			appController.getAppFrame().getPages().refresh();
			appController.switchToPage(page, false);
			appController.saveContent();
		}

		return page;
	}

	private Page addPageToList(String pageUrl, PageList pageList) {
		IAppController appController = getServices().getAppController();
		
		Page currentPage = appController.getCurrentPage();
		int currentIndex = pageList.indexOf(currentPage) + 1;
		String uniquePageName = pageList.generateUniquePageName();
		Page page = new Page(uniquePageName, pageUrl);
		ActionUtils.ensureUniquePageId(page, getServices().getModel());
		pageList.insertBefore(currentIndex, page);
		return page;
	}

	
	public void setPageName(String name) {
		pageName = name;
	}
}
