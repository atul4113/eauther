package com.lorepo.iceditor.client.semi.responsive.ui.widgets.propertiesWidget;

import java.util.Collection;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.DivElement;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.actions.ActionFactory;
import com.lorepo.iceditor.client.actions.ActionFactory.ActionType;
import com.lorepo.iceditor.client.actions.ChangeCurrentContentSemiResponsiveLayoutAction;
import com.lorepo.iceditor.client.semi.responsive.ui.widgets.SemiResponsiveLayoutsListWidget;
import com.lorepo.iceditor.client.semi.responsive.ui.widgets.SemiResponsiveLayoutsListWidget.OnSemiResponsiveLayoutChangeListener;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.layout.PageLayout;

public class PropertiesPanelSemiResponsiveLayoutsChanger extends Composite {

	private static PropertiesPanelSemiResponsiveLayoutsChangerUiBinder uiBinder = GWT.create(PropertiesPanelSemiResponsiveLayoutsChangerUiBinder.class);
	
	@UiField SemiResponsiveLayoutsListWidget semiResponsiveList;
	@UiField DivElement titleLabel;
	private ChangeCurrentContentSemiResponsiveLayoutAction onChangePageSemiResponsiveLayout;
	
	interface PropertiesPanelSemiResponsiveLayoutsChangerUiBinder extends UiBinder<Widget, PropertiesPanelSemiResponsiveLayoutsChanger> {
	}

	public PropertiesPanelSemiResponsiveLayoutsChanger() {
		initWidget(uiBinder.createAndBindUi(this));
		this.semiResponsiveList.setChangeListener(this.getSemiResponsiveListChangeHandler());
		this.setTexts();
	}
	
	public void setActionFactory(ActionFactory af) {
		this.onChangePageSemiResponsiveLayout = (ChangeCurrentContentSemiResponsiveLayoutAction) af.getAction(ActionType.changeCurrentContentSemiResponsiveLayout);
	}
	
	private OnSemiResponsiveLayoutChangeListener getSemiResponsiveListChangeHandler() {
		return new OnSemiResponsiveLayoutChangeListener() {
			@Override
			public void change(String layoutID) {
				onChangePageSemiResponsiveLayout.setNewLayoutID(layoutID);
				onChangePageSemiResponsiveLayout.execute();
			}
		};
	}
	
	private void setTexts() {
		titleLabel.setInnerHTML(DictionaryWrapper.get("semi_responsive_properties_label"));
	}

	public void setSemiResponsiveLayouts(Collection<PageLayout> actualSemiResponsiveLayouts) {
		this.semiResponsiveList.setSemiResponsiveLayouts(actualSemiResponsiveLayouts);
	}

	public void setSelectedSemiResponsiveLayoutID(String semiResponsiveLayoutID) {
		this.semiResponsiveList.setSelectedSemiResponsiveLayoutID(semiResponsiveLayoutID);
	}
	
	public String getSelectedSemiResponsiveLayoutID() {
		return this.semiResponsiveList.getSelectedSemiResponsiveLayout(); 
	}
}
