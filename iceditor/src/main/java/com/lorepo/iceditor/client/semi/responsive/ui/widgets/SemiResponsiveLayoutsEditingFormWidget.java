package com.lorepo.iceditor.client.semi.responsive.ui.widgets;

import java.util.ArrayList;
import java.util.Collection;
import java.util.HashSet;
import java.util.Set;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.AnchorElement;
import com.google.gwt.dom.client.InputElement;
import com.google.gwt.dom.client.SpanElement;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.actions.ActionFactory;
import com.lorepo.iceditor.client.actions.ActionFactory.ActionType;
import com.lorepo.iceditor.client.actions.ShowNotificationAction;
import com.lorepo.iceditor.client.semi.responsive.ui.widgets.SemiResponsiveLayoutsListWidget.OnSemiResponsiveLayoutChangeListener;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationType;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.layout.PageLayout;

public class SemiResponsiveLayoutsEditingFormWidget extends Composite {

	private static SemiResponsiveLayoutsEditingFormUiBinder uiBinder = GWT.create(SemiResponsiveLayoutsEditingFormUiBinder.class);

	interface SemiResponsiveLayoutsEditingFormUiBinder extends UiBinder<Widget, SemiResponsiveLayoutsEditingFormWidget> {}
	
	@UiField SemiResponsiveLayoutsListWidget semiResponsiveList;
	@UiField SemiResponsiveLayoutsActionButtonsWidget actionsButtons;

	@UiField SpanElement nameLabel;
	@UiField SpanElement tresholdLabel;
	
	@UiField InputElement nameInput;
	@UiField InputElement thresholdInput;
	
	@UiField AnchorElement saveChangesButton;
	
	@UiField SemiResponsiveOrientationDeviceSelectorWidget deviceOrientationWidget;
	
	ShowNotificationAction onShowNotification;
	
	private final String DISABLE_EDITING_CLASS = "semi-responsive-editing-disabled";
	
	Content model;
	Collection<PageLayout> pageLayouts = new ArrayList<PageLayout>();
	PageLayout selectedSemiResponsiveLayout;
	
	private SaveChangesListener saveChangesListener;
	private String actualLayoutID = "default";
	
	
	public SemiResponsiveLayoutsEditingFormWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		this.updateElementsText();
		this.connectHandlers();
		this.blockInputs();
	}
	
	public void setActionFactory(ActionFactory actionFactory) {
		this.actionsButtons.setActionFactory(actionFactory);
		this.onShowNotification = (ShowNotificationAction) actionFactory.getAction(ActionType.showNotification);
	}
	
	public void setVisibleItemCount(int number) {
		this.semiResponsiveList.setVisibleItemCount(number);
	}
	
	public void setModel(Content model) {
		String layoutIDToBeSelected = this.findLayoutToSelect(model, this.pageLayouts, this.actualLayoutID);
	
		this.actualLayoutID = layoutIDToBeSelected;
		this.model = model;
		this.pageLayouts = model.getActualSemiResponsiveLayouts();
		this.semiResponsiveList.setSemiResponsiveLayouts(this.pageLayouts);
		this.semiResponsiveList.setSelectedSemiResponsiveLayoutID(layoutIDToBeSelected);

		this.checkIfSelectedInLayouts();
		this.refreshInputs();
	}
	
	private String findLayoutToSelect(Content newModel, Collection<PageLayout> pageLayouts, String actualLayoutID) {
		Set<PageLayout> newPageLayouts = newModel.getActualSemiResponsiveLayouts();
		boolean pageLayoutsHaveBeenLoaded = pageLayouts.size() > 0;
		boolean thereIsNewLayout = newPageLayouts.size() == pageLayouts.size() + 1;
		boolean layoutDeletionOccured = newPageLayouts.size() == pageLayouts.size() - 1;

		Set<String> newPageLayoutsIds = new HashSet<String>();
		Set<String> oldPageLayoutsIds = new HashSet<String>();
		
		for(PageLayout pl : newPageLayouts) {
			newPageLayoutsIds.add(pl.getID());
		}
		
		for(PageLayout pl : pageLayouts) {
			oldPageLayoutsIds.add(pl.getID());
		}

		if (pageLayoutsHaveBeenLoaded && thereIsNewLayout) {
			newPageLayoutsIds.removeAll(oldPageLayoutsIds);
			return newPageLayoutsIds.iterator().next();
		} else if (pageLayoutsHaveBeenLoaded && layoutDeletionOccured) {
			return newModel.getDefaultSemiResponsiveLayoutID();
		} else if (pageLayoutsHaveBeenLoaded && newPageLayoutsIds.contains(actualLayoutID)) {
			return actualLayoutID;
		} else {
			return newModel.getDefaultSemiResponsiveLayoutID();
		}
	}

	private void checkIfSelectedInLayouts() {
		if (this.selectedSemiResponsiveLayout != null) {
			String selectedID = this.selectedSemiResponsiveLayout.getID();
			for (PageLayout pl : this.pageLayouts) {
				if (pl.getID().compareTo(selectedID) == 0) {
					return;
				}
			}
			
			this.selectedSemiResponsiveLayout = null;
		}
	}

	public String getSelectedSemiResponsiveLayout() {
		String layoutID = this.semiResponsiveList.getSelectedSemiResponsiveLayout();
		if (layoutID == null) {
			throw new IllegalArgumentException(DictionaryWrapper.get("semi_responsive_layout_panel_select_layout_first"));
		}
		return layoutID;
	}
	
	public void setSelectedSemiResponsiveLayoutID(String semiResponsiveLayoutID) {
		this.semiResponsiveList.setSelectedSemiResponsiveLayoutID(semiResponsiveLayoutID);
	}
	
	public void setSaveChangesListener(SaveChangesListener saveChangesListener) {
		this.saveChangesListener = saveChangesListener;
	}
	
	private void blockInputs() {
		this.disableElement(this.nameInput);
		this.disableElement(this.thresholdInput);
	}
	
	private void unblockInputs() {
		this.enableElement(this.nameInput);
		this.enableElement(this.thresholdInput);
	}
	
	private void disableElement(InputElement element) {
		element.setAttribute("disabled", "disabled");
		element.addClassName(this.DISABLE_EDITING_CLASS);
	}
	
	private void enableElement(InputElement element) {
		element.removeAttribute("disabled");
		element.removeClassName(this.DISABLE_EDITING_CLASS);
	}

	private void refreshInputs() {
		try {
			String layoutID = this.getSelectedSemiResponsiveLayout();
			this.fillInputs(layoutID);	
		} catch (IllegalArgumentException e) {
			this.unfillInputs();
		}
	}
	
	private void fillInputs(String semiResponsiveID) {
		PageLayout semiResponsiveLayout = this.findSemiResponsiveLayout(semiResponsiveID);
		
		this.selectedSemiResponsiveLayout = semiResponsiveLayout;
		
		String name = semiResponsiveLayout.getName();
		String threshold = Integer.toString(semiResponsiveLayout.getThreshold());

		this.nameInput.setValue(name);
		this.thresholdInput.setValue(threshold);
		
		deviceOrientationWidget.setUseDeviceOrientation(semiResponsiveLayout.useDeviceOrientation());
		deviceOrientationWidget.setDeviceOrientation(semiResponsiveLayout.getDeviceOrientation());
		
		this.unblockInputs();
	}
	
	private void unfillInputs() {
		this.nameInput.setValue("");
		this.thresholdInput.setValue("");
	}

	private PageLayout findSemiResponsiveLayout(String semiResponsiveID) {
		for(PageLayout pl : this.pageLayouts) {
			if (pl.getID().compareTo(semiResponsiveID) == 0) {
				return pl;
			}
		}
		
		return null;
	}

	private void connectHandlers() {
		this.actionsButtons.setGetSelectedSemiResponsiveLayout(new GetSelectedSemiResponsiveLayout() {
			@Override
			public String getValue() {
				return getSelectedSemiResponsiveLayout();
			}
		});
		
		this.semiResponsiveList.setChangeListener(new OnSemiResponsiveLayoutChangeListener() {
			@Override
			public void change(String semiResponsiveID) {
				actualLayoutID = semiResponsiveID;
				fillInputs(semiResponsiveID);
			}
		});
		
		Event.sinkEvents(this.saveChangesButton, Event.ONCLICK);
		Event.setEventListener(this.saveChangesButton, getSaveButtonHandler());
	}

	private EventListener getSaveButtonHandler() {
		return new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if (event.getTypeInt() == Event.ONCLICK && saveChangesListener != null) {
					PageLayout pageLayout = getFormData();
					saveChangesListener.saveChanges(pageLayout);
				}
			}
		};
	}
	
	private PageLayout getFormData() {
		String selectedSemiResponsiveLayoutID = this.selectedSemiResponsiveLayout.getID();
		int threshold;
		String name = this.nameInput.getValue();
		try {
			threshold = Integer.parseInt(this.thresholdInput.getValue());
			if (threshold <= 0) {
				this.showThresholdErrorNotification();
				return null;
			}
			
			if (!this.validateThresholdIsDisjoint(selectedSemiResponsiveLayoutID, threshold)) {
				this.showThresholdDisjointErrorNotification();
				return null;
			}
		} catch(NumberFormatException e) {
			this.showThresholdErrorNotification();
			return null;
		}
		 
		PageLayout modifiedPageLayout = new PageLayout(selectedSemiResponsiveLayoutID, name);
		modifiedPageLayout.setThreshold(threshold);
		modifiedPageLayout.setIsDefault(this.selectedSemiResponsiveLayout.isDefault());
		
		modifiedPageLayout.useDeviceOrientation(this.deviceOrientationWidget.getUseDeviceOrientation());
		modifiedPageLayout.setDeviceOrientation(this.deviceOrientationWidget.getDeviceOrientation());
		
		return modifiedPageLayout;
	}

	private boolean validateThresholdIsDisjoint(String layoutID, int threshold) {
		for (PageLayout pl : this.model.getActualSemiResponsiveLayouts()) {
			if (pl.getThreshold() == threshold && pl.getID().compareTo(layoutID) != 0) {
				return false;
			}
		}
		
		return true;
	}

	private void showThresholdErrorNotification() {
		this.onShowNotification.setType(NotificationType.error)
			.setIsClosable(false)
			.setText(DictionaryWrapper.get("semi_responsive_layout_error_threshold_non_integer"))
			.execute();
	}
	
	private void showThresholdDisjointErrorNotification() {
		this.onShowNotification.setType(NotificationType.error)
		.setIsClosable(false)
		.setText(DictionaryWrapper.get("semi_responsive_layout_error_threshold_is_not_disjoint"))
		.execute();		
	}


	private void updateElementsText() {
		this.nameLabel.setInnerText(DictionaryWrapper.get("semi_responsive_editing_layout_name_label"));
		this.tresholdLabel.setInnerText(DictionaryWrapper.get("semi_responsive_editing_layout_threshold_label"));
		this.saveChangesButton.setInnerText(DictionaryWrapper.get("semi_responsive_editing_layout_save_changes_action"));
	}
}
