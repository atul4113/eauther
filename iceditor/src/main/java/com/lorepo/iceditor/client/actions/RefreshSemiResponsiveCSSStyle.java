package com.lorepo.iceditor.client.actions;

import java.util.HashMap;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.CssStyle;
import com.lorepo.icplayer.client.model.layout.PageLayout;
import com.lorepo.icplayer.client.model.page.Page;


public class RefreshSemiResponsiveCSSStyle extends AbstractAction {
	private String newLayoutID;
	
	public RefreshSemiResponsiveCSSStyle(AppController controller) {
		super(controller);
	}
	
	
	public RefreshSemiResponsiveCSSStyle setLayoutID (String layoutID) {
		this.newLayoutID = layoutID;
		return this;
	}
	
	@Override
	public void execute() {
		Page page = getCurrentPage();
		
		if (page == null) {
			return;
		}

		page.setSemiResponsiveLayoutID(this.newLayoutID);
		this.refreshCssStyle();
	}

	private void refreshCssStyle() {
		Content content = this.getModel();
		
		this.getCurrentPage().getLayout();
		HashMap<String, PageLayout> layouts = content.getLayouts();
		PageLayout actualPageLayout = layouts.get(this.newLayoutID);
		CssStyle cssStyle = content.getStyle(actualPageLayout.getStyleID());
		
		AppController appController = this.getAppController();
		appController.refreshStylesOnly(cssStyle.getValue());
	}
}
