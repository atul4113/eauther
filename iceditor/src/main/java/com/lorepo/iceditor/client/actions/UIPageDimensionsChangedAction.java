package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.widgets.content.PresentationWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.PropertiesWidget;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.api.player.IContentNode;
import com.lorepo.icplayer.client.module.api.player.IPage;

public class UIPageDimensionsChangedAction extends AbstractPageAction{
	public UIPageDimensionsChangedAction(AppController controller) {
		super(controller);
	}

	public void execute(String height, String width, boolean submit) {
		IContentNode selectedContent = getServices().getSelectionController().getSelectedContent();
		if (!(selectedContent instanceof IPage)) {
			return;
		}

		Page selectedPage = (Page) selectedContent;
		AppFrame appFrame = getServices().getAppController().getAppFrame();
		PresentationWidget presentation = appFrame.getPresentation();
		PropertiesWidget properties = appFrame.getProperties();

		properties.setNewPageDimensions(height, width);
		
		if (submit) {
			selectedPage.setHeight(Integer.valueOf(height));
			selectedPage.setWidth(Integer.valueOf(width));
			
			getServices().getAppController().saveCurrentPageAndContent();
			getServices().getAppController().getUndoManager().add(selectedPage.toXML());

			presentation.refreshView();
		}
	}
}