package com.lorepo.iceditor.client.actions;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import com.lorepo.iceditor.client.actions.api.IActionService;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.widgets.modals.QuestionModalListener;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationType;
import com.lorepo.iceditor.client.actions.utils.ActionUtils;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.api.ILayoutDefinition;
import com.lorepo.icplayer.client.module.api.ILayoutDefinition.Property;
import com.lorepo.icplayer.client.model.page.group.Group;
import com.lorepo.icplayer.client.module.api.IModuleModel;
import com.lorepo.icplayer.client.xml.page.PageFactory;

public class SplitPageAction extends DuplicatePageAction {

	private AppFrame appFrame = getServices().getAppController().getAppFrame();
	private float splitFraction = 1;

	public SplitPageAction(IActionService services) {
		super(services);
	}

	private void executeDuplicatePageAction() {
		super.execute();
	}

	public void execute(int splitHeight) {
		splitFraction = (float)splitHeight / (float)getCurrentPage().getHeight();
		String currentLayoutID = getCurrentPage().getSemiResponsiveLayoutID();

		Boolean canExecute = canExecuteThisAction();
		selectLayout(getCurrentPage(), currentLayoutID);

		if (canExecute) {
			appFrame.getModals().addModal(DictionaryWrapper.get("split_page_confirmation"), new QuestionModalListener() {
				@Override
				public void onDecline() {}
				
				@Override
				public void onAccept() {
					executeDuplicatePageAction();
					appFrame.getPresentation().refreshView();
				}
			});
		} else {
			appFrame.getNotifications().addMessage(DictionaryWrapper.get("split_page_not_possible"), NotificationType.error, false);
		}

	}
	
	private void selectLayout(Page page, String layoutID) {
		page.setSemiResponsiveLayoutID(layoutID);

		for (IModuleModel module : page.getModules()) {
			module.setSemiResponsiveLayoutID(layoutID);
		}
	}

	private boolean canExecuteThisAction() {
		Page currentPage = getCurrentPage();
		String pageID = currentPage.getId();
		List<Group> groups = getServices().getAppController().getSelectionController().getPageGroups(pageID);

		boolean isOver;
		boolean isBelow;
		
		if (groups == null) {
			return true;
		}

		for (Group group : groups) {
			isOver = false;
			isBelow = false;
			

			for (String layoutID : getCurrentPage().getSizes().keySet()) {

				for (IModuleModel module : group) {

					module.setSemiResponsiveLayoutID(layoutID);
					HashMap<String, Integer> modulePosition = this.getAppFrame().getPresentation().calculatePosition(currentPage.getId(), module);

					int moduleTop = modulePosition.get("top");
					int moduleBottom = modulePosition.get("bottom");

					float splitHeight = splitFraction*currentPage.getHeight();

					if (splitHeight > moduleTop &&  splitHeight < moduleBottom) {
						return false;
					}

					if (moduleTop > splitHeight) {
						isOver = true;
					} else {
						isBelow = true;
					}

					if (isOver && isBelow) {
						return false;
					}
				}
			}
		}
		
		return true;
	}
	
	@Override
	protected String getPageXML(Page currentPage) {
		String xml = currentPage.toXML();
		Page newPage = new Page("","");
		PageFactory pf = new PageFactory(newPage);
		pf.produce(xml, "");
		ActionUtils.ensureUniquePageId(newPage, getServices().getModel());

		ArrayList<IModuleModel> modulesToStay = new ArrayList<IModuleModel>();
		ArrayList<IModuleModel> modulesToMove = new ArrayList<IModuleModel>();
		splitModules(currentPage, modulesToStay, modulesToMove);

		removeModulesFromCurrentPage(currentPage, modulesToMove);
		removeModulesFromNewPage(newPage, modulesToStay);

		adjustPagesHeight(currentPage, newPage);

		return newPage.toXML();
	}
	
	private void splitModules(Page page, ArrayList<IModuleModel> modulesToStay,  ArrayList<IModuleModel> modulesToMove) {
		for (IModuleModel module : page.getModules()) {
			HashMap<String, Integer> modulePosition = this.getAppFrame().getPresentation().calculatePosition(page.getId(), module);

			if (modulePosition.get("top") > (int)(splitFraction * page.getHeight())) {
				modulesToMove.add(module);
			}
			else {
				modulesToStay.add(module);
			}
		}
	}


	private void removeModulesFromCurrentPage(Page currentPage, ArrayList<IModuleModel> modulesToMove) {
		currentPage.getModules().removeAll(modulesToMove);
	}

	private void removeModulesFromNewPage(Page newPage, ArrayList<IModuleModel> modulesToStay) {
		for (IModuleModel module : modulesToStay) {
			newPage.removeModule(newPage.getModules().getModuleById(module.getId()));
		}
	}

	private void adjustPagesHeight(Page currentPage, Page newPage) {
		for (String layoutID : currentPage.getSizes().keySet()) {
			currentPage.setSemiResponsiveLayoutID(layoutID);
			int currentPageNewHeight = (int)(splitFraction * currentPage.getHeight());
			currentPage.setHeight(currentPageNewHeight);

			newPage.setSemiResponsiveLayoutID(layoutID);
			newPage.setHeight(newPage.getHeight() - currentPageNewHeight);
			calculateModulesPositionsOnNewPage(newPage, layoutID, currentPageNewHeight);
		}
	}

	private void calculateModulesPositionsOnNewPage(Page newPage, String layoutID, int currentPageNewHeight) {
		for (IModuleModel module : newPage.getModules()) {
			module.setSemiResponsiveLayoutID(layoutID);

			ILayoutDefinition moduleLayout = module.getLayout();
			if (moduleLayout.getTopRelativeTo().equals("") && moduleLayout.getTopRelativeToProperty() == Property.top) {
				module.setTop(module.getTop() - currentPageNewHeight);
			}
		}
	}
}