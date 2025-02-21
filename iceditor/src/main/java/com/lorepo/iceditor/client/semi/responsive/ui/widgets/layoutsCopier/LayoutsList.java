package com.lorepo.iceditor.client.semi.responsive.ui.widgets.layoutsCopier;

import java.util.HashMap;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ChangeEvent;
import com.google.gwt.event.dom.client.ChangeHandler;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.Widget;

public class LayoutsList extends Composite {
	
	public interface LayoutsListListener {
		public void onChange(String layoutID);
	}

	interface LayoutsListUiBinder extends UiBinder<Widget, LayoutsList> {}
	
	@UiField ListBox listBox;
	private LayoutsListListener listener;
	private HashMap<String, String> layouts = new HashMap<String, String>();
	private static LayoutsListUiBinder uiBinder = GWT.create(LayoutsListUiBinder.class);

	public LayoutsList() {
		initWidget(uiBinder.createAndBindUi(this));
		this.listBox.addChangeHandler(new ChangeHandler() {
			@Override
			public void onChange(ChangeEvent event) {
				listener.onChange(getSelectedLayoutID());
			}
		});
	}
	
	public void setListener(LayoutsListListener listener) {
		this.listener = listener;
	}
	
	public void setVisibleItemCount(int visibleItems) {
		this.listBox.setVisibleItemCount(visibleItems);
	}
	
	public void setEmptyChangeHandler(boolean shouldBeEmpty) {
		if (shouldBeEmpty) {
			this.listener = new LayoutsListListener() {
				
				@Override
				public void onChange(String layoutID) {}
			};
		}
	}
	
	public void setLayouts(HashMap<String, String> layouts) {
		this.layouts = layouts;
		this.refresh();
	}
	
	public String getSelectedLayoutID() {
		int index = this.listBox.getSelectedIndex();
		try {
			return this.listBox.getValue(index);	
		}
		catch (IndexOutOfBoundsException e){
			return null;
		}
	}
	
	public void refresh() {
		this.listBox.clear();
		this.listBox.addItem("");
		for(String layout : this.layouts.keySet()) {
			listBox.addItem(layout, layouts.get(layout));
		}
		this.listBox.setSelectedIndex(0);	
	}
}