package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.widgets.StylesWidget;
import com.lorepo.iceditor.client.ui.widgets.WorkspaceWidget;
import com.lorepo.iceditor.client.ui.widgets.content.PresentationWidget;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.api.player.IChapter;

public class ChangeCurrentContentSemiResponsiveLayoutAction extends SemiResponsiveAbstractAction {
	
	private String newLayoutID;

	public ChangeCurrentContentSemiResponsiveLayoutAction(AppController controller) {
		super(controller);
	}
	
	public void setNewLayoutID (String layoutID) {
		this.newLayoutID = layoutID;
	}
	
	@Override
	public void execute() {
		Content contentModel = this.getModel();
		contentModel.setActualLayoutID(this.newLayoutID);
		this.refreshSemiResponsive();
	}

	private void refreshSemiResponsive() {
		Content content = this.getModel();
		Page currentPage = this.getCurrentPage();
		
		this.refreshCurrentCssStyleOnly();
		
		PresentationWidget presentationWidget = this.getAppFrame().getPresentation();
		presentationWidget.refreshView();
		this.refreshStylesWidget();
		
		IChapter chapter = content.getParentChapter(currentPage);
		if (!(chapter == content.getCommonPages())) {
			presentationWidget.refreshHeaderFooter();
		}
	}
	
	private void refreshStylesWidget() {
		WorkspaceWidget workspace = this.getWorkSpaceWidget();
		StylesWidget styles = workspace.getStyles();
		
		styles.refresh();
	}
}
