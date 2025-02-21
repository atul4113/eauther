package com.lorepo.iceditor.client.semi.responsive.ui.widgets;

import java.util.Collection;
import java.util.HashSet;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ChangeEvent;
import com.google.gwt.event.dom.client.ChangeHandler;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.layout.PageLayout;

public class SemiResponsiveLayoutsListWidget extends Composite {
	
	public interface OnSemiResponsiveLayoutChangeListener {
		public void change(String semiResponsiveID);
	}

	private static SemiResponsiveLayoutsListWidgetUiBinder uiBinder = GWT.create(SemiResponsiveLayoutsListWidgetUiBinder.class);

	interface SemiResponsiveLayoutsListWidgetUiBinder extends UiBinder<Widget, SemiResponsiveLayoutsListWidget> {}
	
	@UiField ListBox semiResponsiveLayoutsList;
	private OnSemiResponsiveLayoutChangeListener listener;
	private Collection<PageLayout> layouts = new HashSet<PageLayout>();

	public SemiResponsiveLayoutsListWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		this.semiResponsiveLayoutsList.addChangeHandler(new ChangeHandler() {
			@Override
			public void onChange(ChangeEvent event) {
				listener.change(getSelectedSemiResponsiveLayout());
			}
		});
	}
	
	public void setVisibleItemCount(int visibleItems) {
		this.semiResponsiveLayoutsList.setVisibleItemCount(visibleItems);
	}
	
	public void setChangeListener(OnSemiResponsiveLayoutChangeListener listener) {
		this.listener = listener;
	}
	
	public void setEmptyChangeHandler(boolean shouldBeEmpty) {
		if (shouldBeEmpty) {
			this.listener = new OnSemiResponsiveLayoutChangeListener() {
				@Override
				public void change(String semiResponsiveID) {}
			}; 
		}
	}
	
	public void setSelectedSemiResponsiveLayoutID(String layoutID) {
		int count = this.semiResponsiveLayoutsList.getItemCount();
		for(int i = 0; i < count; i++) {
			String listItemLayoutID = this.semiResponsiveLayoutsList.getValue(i);
			if (listItemLayoutID.compareTo(layoutID) == 0) {
				this.semiResponsiveLayoutsList.setSelectedIndex(i);
				break;
			}
		}
	}
	
	public void setSemiResponsiveLayouts(Collection<PageLayout> layouts) {
		String actualSelectedLayout = null;
		if (this.semiResponsiveLayoutsList.getItemCount() > 0) {
			actualSelectedLayout = this.getSelectedSemiResponsiveLayout();
		}
		this.layouts = layouts;
		this.refreshSemiResponsiveLayoutsList(actualSelectedLayout);
	}
	
	public String getSelectedSemiResponsiveLayout() {
		int index = this.semiResponsiveLayoutsList.getSelectedIndex();
		if (index != -1) {
			return this.semiResponsiveLayoutsList.getValue(index);	
		} else {
			return null;
		}
	}
	
	private void refreshSemiResponsiveLayoutsList(String actualSelectedLayoutID) {
		this.semiResponsiveLayoutsList.clear();
		
		for(PageLayout layout : this.layouts) {
			String layoutName = getLayoutName(layout);
			String layoutID = layout.getID();
			this.semiResponsiveLayoutsList.addItem(layoutName, layoutID);
		}
		
		if (actualSelectedLayoutID == null) {
			return;
		}
		
		for (int i = 0; i < this.semiResponsiveLayoutsList.getItemCount(); i++) {
			if (this.semiResponsiveLayoutsList.getValue(i).compareTo(actualSelectedLayoutID) == 0) {
				this.semiResponsiveLayoutsList.setSelectedIndex(i);
				break;
			}
		}
	}

	private String getLayoutName(PageLayout layout) {
		String layoutName;
		if (layout.isDefault()) {
			String defaultTitle = DictionaryWrapper.get("semi_responsive_default_mark");
			layoutName = layout.getName() + " (" + defaultTitle + " " + layout.getThreshold() + ")";
		} else {
			layoutName = layout.getName() + " (" + layout.getThreshold() + ")";
		}
		return layoutName;
	}

	public void removeClassName(String styleName) {
		this.semiResponsiveLayoutsList.getElement().addClassName(styleName);
		
	}

	public void setClassName(String styleName) {
		this.semiResponsiveLayoutsList.getElement().setClassName(styleName);
	}
}
