package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.semi.responsive.ui.widgets.SemiResponsiveLayoutsWidget;
import com.lorepo.iceditor.client.ui.widgets.StylesWidget;
import com.lorepo.iceditor.client.ui.widgets.WorkspaceWidget;
import com.lorepo.iceditor.client.ui.widgets.content.EditCSSWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.PropertiesWidget;
import com.lorepo.icplayer.client.model.Content;

public class RefreshSemiResponsiveLayoutEditingWidgetsAction extends AbstractAction {

	public RefreshSemiResponsiveLayoutEditingWidgetsAction(AppController controller) {
		super(controller);
	}
	
	@Override
	public void execute() {
		refreshPropertiesWidget();
		refreshSemiResponsiveLayoutPanelWidget();
		refreshCSSEditingWidget();
		refreshStylesWidget();
	}
	
	private void refreshCSSEditingWidget() {
		WorkspaceWidget workspace = this.getWorkSpaceWidget();
		
		EditCSSWidget editCss = workspace.getEditCSS();
		if (editCss.isVisible()) {
			Content contentModel = this.getModel();
			editCss.setStyles(contentModel.getStyles());
		}
	}

	private void refreshSemiResponsiveLayoutPanelWidget() {
		SemiResponsiveLayoutsWidget semiResponsivePanel = getWorkSpaceWidget().getSemiResponsiveLayoutsPanel();
		if (semiResponsivePanel.isVisible()) {
			Content model = this.getModel();
			semiResponsivePanel.setModel(model);
		}
	}

	private void refreshPropertiesWidget() {
		Content model = this.getModel();
		PropertiesWidget propertiesWidget = getWorkSpaceWidget().getProperties();
		propertiesWidget.setContent(this.getModel());
		propertiesWidget.setSelectedSemiResponsiveLayoutView(model.getActualSemiResponsiveLayoutID());
	}
	
	private void refreshStylesWidget() {
		WorkspaceWidget workspace = this.getWorkSpaceWidget();		
		StylesWidget stylesWidget = workspace.getStyles();
		stylesWidget.refresh();
	}
}
