package com.lorepo.iceditor.client.ui.widgets.modals;

import static com.google.gwt.query.client.GQuery.$;

import java.util.List;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.AnchorElement;
import com.google.gwt.dom.client.SpanElement;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.ui.widgets.properties.BooleanPropertyWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.PropertiesWidget;
import com.lorepo.iceditor.client.ui.widgets.utils.MainPageUtils;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;

public class DropDownGapWidget extends Composite {

	private static DropDownGapWidgetUiBinder uiBinder = GWT
			.create(DropDownGapWidgetUiBinder.class);

	interface DropDownGapWidgetUiBinder extends
			UiBinder<Widget, DropDownGapWidget> {
	}

	@UiField HTMLPanel panel;
	@UiField HTMLPanel items;
	@UiField SpanElement title;
	@UiField AnchorElement add;
	@UiField SpanElement correctLabel;
	@UiField SpanElement answerLabel;
	@UiField SpanElement enableProperty;
	@UiField SpanElement feedback;
	
	private PropertiesWidget propertiesWidget = new PropertiesWidget();
	private boolean isKeepOrderChecked = false;
	private String moduleTypeName;
	
	public DropDownGapWidget(String mode, List<String> values) {
		initWidget(uiBinder.createAndBindUi(this));
		items.getElement().addClassName("gapItemsList");
		feedback.setId("add_gap_feedback");
		enableProperty.setId("infoEnableProperty");
		updateElementsTexts(mode);
		$(feedback).hide();
		
		if (values != null) {
			fillItems(values);
		} else {
			addNewItem(true);
		}
	}
	
	private void fillItems(List<String> values) {
		for (String value : values) {
			addAndFillItem(value);
		}
	}

	private void addAndFillItem(String value) {
		ItemsDropDownGapWidget item = new ItemsDropDownGapWidget();

		if (value.charAt(1) == ':') {
			item.setValue(value.substring(2));
			item.correct.setAttribute("checked", "checked");
		} else {
			item.setValue(value);
		}
		
		if (!isKeepInOrderPropertyChecked()) {
			item.correct.setAttribute("disabled", "disabled");
		}
		
		items.add(item);
	}
	
	public void addSortableItems() {
		addSortableItems(this);
	}
	
	public native void addSortableItems(DropDownGapWidget instance) /*-{
		$wnd.$('.gapItemsList').sortable({ 
			axis: 'y',
			handle: ".sortable_image",
			stop: function (event, ui) {
				if (!instance.@com.lorepo.iceditor.client.ui.widgets.modals.DropDownGapWidget::isKeepInOrderPropertyChecked()()) {
					$wnd.$('.gapItemsList > .add_gap_item > input[type="radio"]').each(function(i) {
						if (i==0) {
							$wnd.$(this).attr("checked","checked");
						} else {
							$wnd.$(this).removeAttr("checked");
						}
					});
				}
			} 
			});
	}-*/;
	
	private Element getRootElement() {
		return panel.getElement();
	}
	
	private com.google.gwt.dom.client.Element getAcceptElement() {
		return $(getRootElement()).find(".accept").get(0);
	}
	
	private com.google.gwt.dom.client.Element getDeclineElement() {
		return $(getRootElement()).find(".decline").get(0);
	}
	
	protected void init() {
		setRadios();
		isKeepInOrderPropertyChecked();
	}
	
	private void setRadios() {
		isKeepOrderChecked = isKeepInOrderPropertyChecked();
		if (isKeepOrderChecked) {
			$(enableProperty).hide();
		}
	}
	
	private boolean isKeepInOrderPropertyChecked() {
		propertiesWidget = MainPageUtils.appFrame.getProperties();
		BooleanPropertyWidget keepOriginalProperty = (BooleanPropertyWidget) propertiesWidget.getModuleProperties().get(DictionaryWrapper.get("Keep_original_order"));

		if (keepOriginalProperty == null) { // non Text module
			return false;
		}
		
		return keepOriginalProperty.getValue();
	}
	
	protected void setFocus() {
		int itemsCount = items.getWidgetCount();
		ItemsDropDownGapWidget lastItem = (ItemsDropDownGapWidget) items.getWidget(itemsCount - 1);
		
		lastItem.answer.focus();
	}
	
	private void addNewItem(boolean isSelected) {
		ItemsDropDownGapWidget item = new ItemsDropDownGapWidget();
		
		if (isSelected) {
			item.correct.setAttribute("checked", "checked");
		} else if (!isKeepOrderChecked) {
			item.correct.setAttribute("disabled", "disabled");
		}
		
		items.add(item);
		setFocus();
	}
	
	private native boolean isCorrectFilled() /*-{
		var $_ = $wnd.$,
			$_items = $_('.gapItemsList').find('.add_gap_item'),
			isCorrect = false;
		
		$_.each($_items, function(i, el) {
			var value = $_(el).find('input:text')[0].value,
				radioChecked = $_(el).find('input:radio')[0].checked;
						
			if (value !== "" && radioChecked) {
				isCorrect = true;
				return false;
			}
		});
		
		return isCorrect;
	}-*/;
	
	public void setListener(final QuestionModalListener listener) {
		if (listener == null) {
			return;
		}
		
		com.google.gwt.dom.client.Element acceptElement = getAcceptElement();
		Event.sinkEvents(acceptElement, Event.ONCLICK);
		Event.setEventListener(acceptElement, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				event.preventDefault();
				event.stopPropagation();
				if(isCorrectFilled()) {
					listener.onAccept();
				} else {
					$(feedback).show().delay(1000).fadeOut();
				}
			}
		});
		
		com.google.gwt.dom.client.Element declineElement = getDeclineElement();
		Event.sinkEvents(declineElement, Event.ONCLICK);
		Event.setEventListener(declineElement, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				event.preventDefault();
				event.stopPropagation();

				listener.onDecline();
			}
		});
		
		Event.sinkEvents(add, Event.ONCLICK);
		Event.setEventListener(add, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				event.preventDefault();
				event.stopPropagation();
				
				addNewItem(false);
				
				MainPageUtils.updateScrollBar("gapItemsList");
			}
		});
		
		
	}
	
	public void updateElementsTexts(String mode) {
		$(getRootElement()).find("a.accept").text(DictionaryWrapper.get("ok").toUpperCase());
		$(getRootElement()).find("a.decline").text(DictionaryWrapper.get("cancel").toUpperCase());
		add.setInnerText("+");
		correctLabel.setInnerText(DictionaryWrapper.get("gap_correct"));
		answerLabel.setInnerText(DictionaryWrapper.get("gap_answer"));
		feedback.setInnerText(DictionaryWrapper.get("fill_required_field"));

		if (moduleTypeName.equals("HTMLEditor")) {
			enableProperty.setInnerText(DictionaryWrapper.get("enable_keep_order_property"));
		}

		if (mode.equals("edit")) {
			title.setInnerText(DictionaryWrapper.get("edit_dropdown_gap"));
		} else {
			title.setInnerText(DictionaryWrapper.get("add_dropdown_gap"));
		}
	}
	
	public native String getDefinition() /*-{
		var syntax = "",
			$_ = $wnd.$,
			$_items = $_('.gapItemsList').find('.add_gap_item');
		
		$_.each($_items, function(i, el) {
			var value = $_(el).find('input:text')[0].value,
				radioChecked = $_(el).find('input:radio')[0].checked;
			
			if (value !== "") {
				if (radioChecked) {
					syntax += "1:" + value + "|";
				} else {
					syntax += value + "|";
				}
			}
		});
		
		return "{{" + syntax.substring(0, syntax.length - 1) + "}}";
	}-*/;

	public native String getLongestWord() /*-{
		var syntax = "",
			$_ = $wnd.$,
			$_items = $_('.gapItemsList').find('.add_gap_item'),
			longestWord = "";
		
		$_.each($_items, function(i, el) {
			var value = $_(el).find('input:text')[0].value,
				radioChecked = $_(el).find('input:radio')[0].checked;
			
			if (value !== "") {
				if (value.length > longestWord.length) longestWord = value;
			}
		});
		
		return longestWord;
	}-*/;

	public void setModuleTypeName(String moduleTypeName) {
		this.moduleTypeName = moduleTypeName;
	}
}
