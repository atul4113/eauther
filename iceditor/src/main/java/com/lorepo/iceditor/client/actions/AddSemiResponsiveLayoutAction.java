package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.actions.ActionFactory.ActionType;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.semi.responsive.SemiResponsiveModificationsHistory;
import com.lorepo.iceditor.client.ui.widgets.modals.semi.responsive.AddNewSemiResponsiveLayout;
import com.lorepo.iceditor.client.ui.widgets.modals.semi.responsive.PageLayoutData;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationType;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.CssStyle;
import com.lorepo.icplayer.client.model.layout.PageLayout;
import com.lorepo.icplayer.client.model.page.Page;

public class AddSemiResponsiveLayoutAction extends AbstractAction {
	
	public AddSemiResponsiveLayoutAction(AppController controller) {
		super(controller);
	}
	
	public void execute() {
		this.getModals().addNewSemiResponsiveLayout(new AddNewSemiResponsiveLayout() {
			
			@Override
			public void onDecline() {}
			
			@Override
			public void onAddNewSemiResponsiveLayout(PageLayoutData pageLayoutData) {
				try {
					PageLayout newLayout = parseDataToPageLayout(pageLayoutData);
					CssStyle newStyle = createStyleFromPageLayout(newLayout);
					addNewLayoutData(newLayout, newStyle);
					setModificationHistory(newLayout);
					refreshWidgets();
					getNotifications().addMessage(DictionaryWrapper.get("add_new_semi_responsive_layout_success"), NotificationType.success, false);
				} catch (IllegalArgumentException e) {
					getNotifications().addMessage(e.getMessage(), NotificationType.error, true);
				}
			}
		});
	}
	
	private CssStyle createStyleFromPageLayout(PageLayout newLayout) {
		CssStyle newStyle = CssStyle.createStyleFromPageLayout(newLayout);
		
		newLayout.setCssID(newStyle.getID());
		Content model = this.getModel();
		newStyle.setValue(model.getDefaultCssStyle().getValue());
		
		return newStyle;
	}

	protected void setModificationHistory(PageLayout newLayout) {
		Page page = this.getCurrentPage();
		if (page != null) {
			String pageID = page.getId();
			SemiResponsiveModificationsHistory.addNewSemiResponsiveLayout(pageID, newLayout.getID());
			
			Content model = this.getModel();
			String layoutID = model.getActualSemiResponsiveLayoutID();
			SemiResponsiveModificationsHistory.setLastSeen(pageID, layoutID);
		}
	}
	
	private void refreshWidgets() {
		this.getActionFactory().getAction(ActionType.refreshSemiResponsiveLayoutEditingWidgets).execute();
	}

	private PageLayout parseDataToPageLayout(PageLayoutData pageLayoutData) {
		String name = pageLayoutData.name;
		String unparsedTreshold = pageLayoutData.treshold;
		
		if (name.compareTo("") == 0) {
			String errorMsg = DictionaryWrapper.get("semi_responsive_layout_error_name_empty");
			throw new IllegalArgumentException(errorMsg);
		}
		
		
		if (unparsedTreshold.compareTo("") == 0) {
			String errorMsg = DictionaryWrapper.get("semi_responsive_layout_error_threshold_non_integer");
		    throw new IllegalArgumentException(errorMsg);
		}
		
		int tresholdValue;
		try {
			tresholdValue = Integer.parseInt(unparsedTreshold, 10);        
		    if (tresholdValue <= 0) {
				String errorMsg = DictionaryWrapper.get("semi_responsive_layout_error_threshold_non_integer");
		    	throw new IllegalArgumentException(errorMsg);
		    }
		    
			if (!this.validateThresholdIsDisjoint(tresholdValue)) {
				String errorMsg = DictionaryWrapper.get("semi_responsive_layout_error_threshold_is_not_disjoint");
				throw new IllegalArgumentException(errorMsg);
			}
		} catch (NumberFormatException e) {
			String errorMsg = DictionaryWrapper.get("semi_responsive_layout_error_threshold_non_integer");
			throw new IllegalArgumentException(errorMsg);
		}
		
		
		return PageLayout.createPageLayout(name, tresholdValue, pageLayoutData.useDeviceOrientation, pageLayoutData.deviceOrientation);
	}

	private boolean validateThresholdIsDisjoint(int threshold) {
		for (PageLayout pl : this.getModel().getActualSemiResponsiveLayouts()) {
			if (pl.getThreshold() == threshold) {
				return false;
			}
		}
		
		return true;
	}
	
	private void addNewLayoutData(PageLayout newPageLayout, CssStyle newStyle) {
		Content model = this.getModel();
		model.addLayout(newPageLayout);
		model.setStyle(newStyle);
	}
}
