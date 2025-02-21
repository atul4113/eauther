package com.lorepo.iceditor.client.actions;

import java.util.Collection;
import java.util.HashMap;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.widgets.modals.semi.responsive.SetSemiResponsiveLayoutCSSStyle;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.CssStyle;
import com.lorepo.icplayer.client.model.layout.PageLayout;

public class SetSemiResponsiveLayoutStyleAction extends SemiResponsiveAbstractAction {

	private String layoutID;

	public SetSemiResponsiveLayoutStyleAction(AppController controller) {
		super(controller);
	}
	
	public void setSemiResponsiveLayoutID(String layoutID) {
		this.layoutID = layoutID;
	}
	
	@Override
	public void execute() {
		Content model = this.getModel();
		Collection<CssStyle> styles = model.getStyles().values();
		
		this.getModals().setCSSStyleForSemiResponsive(styles, new SetSemiResponsiveLayoutCSSStyle() {
			
			@Override
			public void onDecline() {}
			
			@Override
			public void onSetSemiResponsiveLayoutCSSStyle(String styleID) {
				changeLayoutStyleTo(layoutID, styleID);
				refreshCurrentStyle(styleID);
				refreshSemiResponsiveEditingWidgets();
			}
		});
	}

	private void refreshCurrentStyle(String styleID) {
		Content content = this.getModel();
		CssStyle cssStyle = content.getStyle(styleID);
		
		AppController appController = this.getAppController();
		appController.refreshStyles(cssStyle.getValue());
	}

	private void changeLayoutStyleTo(String layoutID, String styleID) {
		Content model = this.getModel();
		HashMap<String, PageLayout> layouts = model.getLayouts();
		
		PageLayout pl = layouts.get(layoutID);
		pl.setCssID(styleID);

		layouts.put(layoutID, pl);
	}
}
