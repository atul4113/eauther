package com.lorepo.iceditor.client.actions;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.Command;
import com.lorepo.iceditor.client.actions.api.IActionService;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.widgets.WorkspaceWidget;
import com.lorepo.iceditor.client.ui.widgets.modals.ModalsWidget;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationsWidget;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.model.page.PageList;
import com.lorepo.icplayer.client.module.api.player.IChapter;
import com.lorepo.icplayer.client.module.api.player.IContentNode;

public abstract class AbstractAction implements ClickHandler, Command {

	private IActionService actionServices;
	private AppController	controller;
	
	public AbstractAction(AppController	controller){
		this.controller = controller;
	}
	
	public AbstractAction(IActionService services) {
		this.actionServices = services;
	}

	
	public IActionService getServices(){
		if(actionServices != null){
			return actionServices;
		}
		else{
			return getController().getActionServices();
		}
	}

	
	@Deprecated
	public AppController getController(){
		return this.controller;
	}
	
	public AppFrame getAppFrame() {
		return this.getServices().getAppController().getAppFrame();
	}
	
	public AppController getAppController () {
		return (AppController) this.getServices().getAppController();
	}
	
	public Content getModel(){
		return this.getServices().getModel();
	}
	
	public WorkspaceWidget getWorkSpaceWidget() {
		return this.getAppFrame().getWorkspace();
	}
	
	public ModalsWidget getModals() {
		return this.getAppFrame().getModals();
	}
	
	public NotificationsWidget getNotifications() {
		return this.getAppFrame().getNotifications();
	}
	
	@Override
	public void onClick(ClickEvent event) {
		execute();
	}
	
	@Override
	public void execute() {}
	
	public PageList getCurrentChapter(){
		IContentNode node = getServices().getAppController().getSelectionController().getSelectedContent();

		if (node instanceof PageList) {
			return (PageList) node;
		}
		
		IChapter parent = getServices().getModel().getParentChapter(node);
		if (parent instanceof PageList) {
			return (PageList) parent;
		}
		
		return null;
	}
	
	public Page getCurrentPage() {
		return getAppController().getCurrentPage();
	}
	
	public void refreshView() {
		this.getAppFrame().getPresentation().refreshView();
	}
	
	public ActionFactory getActionFactory() {
		return getServices().getAppController().getActionFactory();
	}
}
