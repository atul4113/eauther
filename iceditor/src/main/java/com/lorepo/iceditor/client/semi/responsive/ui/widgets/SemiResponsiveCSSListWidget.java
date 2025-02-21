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
import com.lorepo.icplayer.client.model.CssStyle;

public class SemiResponsiveCSSListWidget extends Composite {

	private static SemiResponsiveCSSListWidgetUiBinder uiBinder = GWT.create(SemiResponsiveCSSListWidgetUiBinder.class);
	
	public interface OnSemiResponsiveCSSStyleChangeListener {
		public void change(String cssStyle);
	}

	interface SemiResponsiveCSSListWidgetUiBinder extends
			UiBinder<Widget, SemiResponsiveCSSListWidget> {
	}

	@UiField ListBox semiResponsiveCSSList;
	private OnSemiResponsiveCSSStyleChangeListener listener;
	private Collection<CssStyle> styles = new HashSet<CssStyle>();
	
	public SemiResponsiveCSSListWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		this.semiResponsiveCSSList.addChangeHandler(new ChangeHandler() {
			@Override
			public void onChange(ChangeEvent event) {
				listener.change(getSelectedSemiResponsiveCSSStyle());
			}
		});
	}
	
	public void setEmptyChangeHandler(boolean shouldBeEmpty) {
		if (shouldBeEmpty) {
			this.listener = new OnSemiResponsiveCSSStyleChangeListener() {
				@Override
				public void change(String cssStyle) {}
			};	
		}
	}

	public void setVisibleItemCount(int visibleItems) {
		this.semiResponsiveCSSList.setVisibleItemCount(visibleItems);
	}
	
	public void setChangeListener(OnSemiResponsiveCSSStyleChangeListener listener) {
		this.listener = listener;
	}

	public void setSemiResponsiveCssStyles(Collection<CssStyle> styles) {
		String cssStyle = null;
		if (this.semiResponsiveCSSList.getItemCount() > 0) {
			cssStyle = this.getSelectedSemiResponsiveCSSStyle();
		}
		this.styles = styles;
		this.refreshSemiResponsiveLayoutsList(cssStyle);
	}
	
	public void setSelectedSemiResponsiveCssStyle(String styleID) {
		int count = this.semiResponsiveCSSList.getItemCount();
		
		for(int i = 0; i < count; i++) {
			String listItemLayoutID = this.semiResponsiveCSSList.getValue(i);
			if (listItemLayoutID.compareTo(styleID) == 0) {
				this.semiResponsiveCSSList.setSelectedIndex(i);
				break;
			}
		}
	}
	
	public String getSelectedSemiResponsiveCSSStyle() {
		int index = this.semiResponsiveCSSList.getSelectedIndex();
		if (index != -1) {
			return this.semiResponsiveCSSList.getValue(index);	
		} else {
			return null;
		}
	}
	
	private void refreshSemiResponsiveLayoutsList(String actualSelectedLayoutID) {
		this.semiResponsiveCSSList.clear();
		
		for(CssStyle style : this.styles) {
			String styleName = getStyleName(style);
			String styleID = style.getID();
			this.semiResponsiveCSSList.addItem(styleName, styleID);
		}
		
		if (actualSelectedLayoutID == null) {
			return;
		}
		
		for (int i = 0; i < this.semiResponsiveCSSList.getItemCount(); i++) {
			if (this.semiResponsiveCSSList.getValue(i).compareTo(actualSelectedLayoutID) == 0) {
				this.semiResponsiveCSSList.setSelectedIndex(i);
				break;
			}
		}
	}

	private String getStyleName(CssStyle style) {
		String layoutName;
		if (style.isDefault()) {
			String defaultTitle = DictionaryWrapper.get("semi_responsive_default_mark");
			layoutName = style.getName() + " (" + defaultTitle + ")";
		} else {
			layoutName = style.getName();
		}
		return layoutName;
	}
}
