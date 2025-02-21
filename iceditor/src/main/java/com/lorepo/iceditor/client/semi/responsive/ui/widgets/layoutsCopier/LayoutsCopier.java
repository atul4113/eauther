package com.lorepo.iceditor.client.semi.responsive.ui.widgets.layoutsCopier;

import java.util.Collection;
import java.util.HashMap;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.DivElement;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.semi.responsive.ui.widgets.layoutsCopier.LayoutsList.LayoutsListListener;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.layout.PageLayout;


public class LayoutsCopier extends Composite {
	
	interface LayoutsCopierUiBinder extends UiBinder<Widget, LayoutsCopier> {}

	private static LayoutsCopierUiBinder uiBinder = GWT.create(LayoutsCopierUiBinder.class);
	
	@UiField LayoutsList layoutsList;
	@UiField DivElement label;

	
	public LayoutsCopier() {
		initWidget(uiBinder.createAndBindUi(this));
		label.setInnerHTML(DictionaryWrapper.get("copy_page_layout"));
	}

	public void setListener(LayoutsListListener listener) {
		this.layoutsList.setListener(listener);
	}

	public void setLayouts(Collection<PageLayout> layouts) {
		HashMap<String, String> newLayouts = new HashMap<String, String>();
		for (PageLayout layout : layouts) {
			newLayouts.put(layout.getName(), layout.getID());
		}
		this.layoutsList.setLayouts(newLayouts);
	}

	public void refreshList() {
		this.layoutsList.refresh();
	}

	public String getSelectedLayoutID() {
		return this.layoutsList.getSelectedLayoutID(); 
	}

}
