package com.lorepo.iceditor.client.actions;

import java.util.HashMap;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.semi.responsive.ui.widgets.SaveChangesListener;
import com.lorepo.iceditor.client.semi.responsive.ui.widgets.SemiResponsiveLayoutsWidget;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.CssStyle;
import com.lorepo.icplayer.client.model.layout.PageLayout;

public class ShowSemiResponsivePanel extends SemiResponsiveAbstractAction {

	public ShowSemiResponsivePanel(AppController controller) {
		super(controller);
	}
	
	@Override
	public void execute() {
		AppFrame appFrame = this.getAppFrame();
		SemiResponsiveLayoutsWidget editor = appFrame.getEditSemiResponsiveLayouts();
		
		Content model = this.getModel();
		
		editor.setModel(model);
		editor.setSaveChangesListener(new SaveChangesListener() {
				@Override
				public void saveChanges(PageLayout pageLayout) {
					boolean changed = saveChangesInContent(pageLayout);
					if (changed) {
						getServices().getAppController().saveCurrentPageAndContent();
						refreshSemiResponsiveEditingWidgets();
						refreshCurrentCssStyleOnly();
					}
				}
		});
		editor.show();
	}

	private boolean saveChangesInContent(PageLayout pageLayout) {
		if (pageLayout != null) {
			Content model = this.getModel();
			changeStyleName(model, pageLayout);
			changePageLayout(pageLayout, model);
			
			return true;
		}
		
		return false;
	}

	private void changePageLayout(PageLayout pageLayout, Content model) {
		HashMap<String, PageLayout> map = model.getLayouts();
		map.put(pageLayout.getID(), pageLayout);
		
		model.setSemiResponsiveLayouts(map);
	}

	private Content changeStyleName(Content model, PageLayout pageLayout) {
		CssStyle style = model.getStyle(pageLayout.getID());
		style.setName(pageLayout.getName());
		model.setStyle(style);
		
		return model;
	}
}
