package com.lorepo.iceditor.client.semi.responsive.ui.widgets;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.HeadingElement;
import com.google.gwt.dom.client.Style.Display;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.actions.ActionFactory;
import com.lorepo.iceditor.client.ui.widgets.content.WidgetLockerController;
import com.lorepo.iceditor.client.ui.widgets.utils.MainPageUtils;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.Content;

public class SemiResponsiveLayoutsWidget extends Composite {

	private static LayoutsWidgetUiBinder uiBinder = GWT.create(LayoutsWidgetUiBinder.class);

	interface LayoutsWidgetUiBinder extends UiBinder<Widget, SemiResponsiveLayoutsWidget> {}
	
	@UiField HTMLPanel panel;
	@UiField HeadingElement title;
	@UiField HeadingElement semiResponsiveLayoutsHeader;
	
	@UiField SemiResponsiveLayoutsEditingFormWidget semiResponsiveLayoutsEditingForm;
	
	private boolean isVisible;

	public SemiResponsiveLayoutsWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		
		panel.getElement().setId("semi-responsive-panel");

		updateElementsTexts();
		hide();
	}
	
	public void setActionFactory(ActionFactory actionFactory) {
		this.semiResponsiveLayoutsEditingForm.setActionFactory(actionFactory);
	}
	
	public boolean isVisible() {
		return isVisible;
	}
	
	public void setModel(Content model) {
		this.semiResponsiveLayoutsEditingForm.setModel(model);
	}
	
	public void setSaveChangesListener(SaveChangesListener saveChangesListener) {
		this.semiResponsiveLayoutsEditingForm.setSaveChangesListener(saveChangesListener);
	}

	public void show() {
		this.isVisible = true;
		MainPageUtils.show(panel);
	}
	
	public void hide() {
		this.panel.getElement().getStyle().setDisplay(Display.NONE);
		this.isVisible = false;
		WidgetLockerController.hide();
	}
	
	private void updateElementsTexts() {
		this.title.setInnerText(DictionaryWrapper.get("semi_responsive_panel_title"));
		this.semiResponsiveLayoutsHeader.setInnerText(DictionaryWrapper.get("semi_responsive_panel_semi_responsive_layouts_title"));
	}
}
