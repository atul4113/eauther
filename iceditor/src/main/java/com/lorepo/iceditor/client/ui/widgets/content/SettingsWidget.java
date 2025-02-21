package com.lorepo.iceditor.client.ui.widgets.content;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.AnchorElement;
import com.google.gwt.dom.client.HeadingElement;
import com.google.gwt.dom.client.InputElement;
import com.google.gwt.dom.client.LabelElement;
import com.google.gwt.dom.client.Style.Display;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.iceditor.client.ui.widgets.utils.MainPageUtils;

public class SettingsWidget extends Composite {

	private static SettingsWidgetUiBinder uiBinder = GWT
			.create(SettingsWidgetUiBinder.class);

	interface SettingsWidgetUiBinder extends UiBinder<Widget, SettingsWidget> {}
	
	@UiField HTMLPanel panel;
	@UiField AnchorElement save;
	@UiField AnchorElement apply;
	@UiField HeadingElement title;
	
	@UiField InputElement staticHeader;
	@UiField InputElement staticFooter;
	@UiField LabelElement staticHeaderLabel;
	@UiField LabelElement staticFooterLabel;
	@UiField LabelElement useGridLabel;
	@UiField LabelElement gridSizeLabel;
	@UiField LabelElement useGridSnappingLabel;
	@UiField InputElement useGrid;
	@UiField InputElement gridSize;
	@UiField InputElement useGridSnapping;
	@UiField InputElement useRulers;
	@UiField InputElement useRulersSnapping;
	@UiField LabelElement useRulersLabel;
	@UiField LabelElement useRulersSnappingLabel;
	@UiField LabelElement langLabel;
	@UiField InputElement lang;
	@UiField InputElement enableTabindex;
	@UiField LabelElement enableTabindexLabel;
	@UiField InputElement sortRightToLeft;
	@UiField LabelElement sortRightToLeftLabel;

	public SettingsWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		
		panel.getElement().setId("settingsPage");
		staticHeader.setId("staticHeaderOption");
		staticFooter.setId("staticFooterOption");

		updateElementsTexts();
		
		hide();
	}
	
	public void show() {
		MainPageUtils.show(panel);
	}

	public void hide() {
		panel.getElement().getStyle().setDisplay(Display.NONE);
		WidgetLockerController.hide();
	}

	public void setStaticHeaderSelected(boolean isChecked) {
		staticHeader.setChecked(isChecked);
	}
	
	public boolean isStaticHeaderSelected() {
		return staticHeader.isChecked();
	}

	public void setStaticFooterSelected(boolean isChecked) {
		staticFooter.setChecked(isChecked);
	}

	public boolean isStaticFooterSelected() {
		return staticFooter.isChecked();
	}
	
	public void setUseGridSelected(boolean isChecked) {
		this.useGrid.setChecked(isChecked);
	}
	
	public boolean isUseGridSelected() {
		return useGrid.isChecked();
	}
	
	public String getGridSize() {
		try {
			int gridSize = Integer.parseInt(this.gridSize.getValue());
			
			return gridSize < 2 ? "2" : this.gridSize.getValue();
			
		} catch (NumberFormatException e){
			return "20";
		}
	}

	public void setGridSize(String gridSize) {
		this.gridSize.setValue(gridSize);
	}
	
	public void setGridSnappingSelected(boolean isChecked) {
		this.useGridSnapping.setChecked(isChecked);
	}
	
	public boolean isGridSnappingSelected() {
		return useGridSnapping.isChecked();
	}
	
	public void setUseRulersSelected(Boolean isChecked) {
		this.useRulers.setChecked(isChecked);
	}
	
	public boolean isUseRulersSelected() {
		return useRulers.isChecked();
	}
	
	public void setRulersSnappingSelected(Boolean isChecked) {
		this.useRulersSnapping.setChecked(isChecked);
	}
	
	public boolean isRulersSnappingSelected() {
		return useRulersSnapping.isChecked();
	}
	
	public String getLang() {
		return this.lang.getValue() == "undefined" ? "" : this.lang.getValue();
	}

	public void setLang(String lang) {
		this.lang.setValue(lang);
	}
	
	public void setEnableTabindexSelected(boolean isChecked) {
		enableTabindex.setChecked(isChecked);
	}
	
	public boolean isEnableTabindexSelected() {
		return enableTabindex.isChecked();
	}
	
	public void setSortRightToLeftSelected(boolean isChecked) {
		sortRightToLeft.setChecked(isChecked);
	}
	
	public boolean isSortRightToLeftSelected() {
		return sortRightToLeft.isChecked();
	}

	public void setListener(final MainPageEventListener listener) {
		Event.sinkEvents(save, Event.ONCLICK);
		Event.setEventListener(save, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				listener.onSave();
			}
		});

		Event.sinkEvents(apply, Event.ONCLICK);
		Event.setEventListener(apply, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				listener.onApply();
			}
		});
		
		Event.sinkEvents(gridSize, Event.ONCHANGE);
		Event.setEventListener(gridSize, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if (Event.ONCHANGE != event.getTypeInt()) {
					return;
				}
				
				gridSize.setValue(getGridSize());
			}
		});
		
		Event.sinkEvents(lang, Event.ONCHANGE);
		Event.setEventListener(lang, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if (Event.ONCHANGE != event.getTypeInt()) {
					return;
				}
				
				lang.setValue(getLang());
			}
		});
	}
	
	public void updateElementsTexts() {
		staticHeaderLabel.setInnerText(DictionaryWrapper.get("static_header"));
		staticFooterLabel.setInnerText(DictionaryWrapper.get("static_footer"));
		useGridLabel.setInnerText(DictionaryWrapper.get("use_grid"));
		gridSizeLabel.setInnerText(DictionaryWrapper.get("grid_size"));
		useGridSnappingLabel.setInnerText(DictionaryWrapper.get("use_grid_snapping"));
		useRulersLabel.setInnerText(DictionaryWrapper.get("use_rulers"));
		useRulersSnappingLabel.setInnerText(DictionaryWrapper.get("use_rulers_snapping"));
		langLabel.setInnerText(DictionaryWrapper.get("lang"));
		enableTabindexLabel.setInnerText(DictionaryWrapper.get("is_tabindex_enabled"));
		sortRightToLeftLabel.setInnerText(DictionaryWrapper.get("is_sort_right_to_left"));
		
		title.setInnerText(DictionaryWrapper.get("settings"));
		save.setInnerText(DictionaryWrapper.get("save"));
		apply.setInnerText(DictionaryWrapper.get("apply"));
	}
}
