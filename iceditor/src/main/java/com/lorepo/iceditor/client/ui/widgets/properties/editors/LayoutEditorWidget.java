package com.lorepo.iceditor.client.ui.widgets.properties.editors;

import java.util.List;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.AnchorElement;
import com.google.gwt.dom.client.DivElement;
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
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.actions.AbstractAction;
import com.lorepo.iceditor.client.actions.ActionFactory;
import com.lorepo.iceditor.client.actions.EditModuleMainPropertiesAction;
import com.lorepo.iceditor.client.actions.ActionFactory.ActionType;
import com.lorepo.iceditor.client.ui.widgets.content.WidgetLockerController;
import com.lorepo.iceditor.client.ui.widgets.utils.MainPageUtils;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.module.ILayoutProperty;
import com.lorepo.icplayer.client.module.LayoutDefinition;
import com.lorepo.icplayer.client.module.api.ILayoutDefinition.Property;

public class LayoutEditorWidget extends Composite {

	private ILayoutProperty property;
	private AbstractAction onSave;
	private EditModuleMainPropertiesAction onModulePositionEdit;
	
	private static LayoutEditorOptionsWidgetUiBinder uiBinder = GWT
			.create(LayoutEditorOptionsWidgetUiBinder.class);

	interface LayoutEditorOptionsWidgetUiBinder extends
			UiBinder<Widget, LayoutEditorWidget> {
	}
	
	public LayoutEditorWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		setStyles();
		panel.getElement().setId("layoutPage");
		mainPageWindow.getStyle().setDisplay(Display.BLOCK);
		
		connectHandlers();
		updateElementsTexts();
	}
	
	@UiField HTMLPanel panel;
	@UiField LabelElement leftLabel;
	@UiField LabelElement rightLabel;
	@UiField LabelElement topLabel;
	@UiField LabelElement bottomLabel;
	@UiField InputElement hasLeftCheck;
	@UiField InputElement hasRightCheck;
	@UiField InputElement hasTopCheck;
	@UiField InputElement hasBottomCheck;
	@UiField LabelElement useLabel;
	@UiField LabelElement relativeToLabel;
	@UiField LabelElement sideLabel;
	@UiField ListBox rightModuleBox;
	@UiField ListBox topModuleBox;
	@UiField ListBox leftModuleBox;
	@UiField ListBox bottomModuleBox;
	@UiField ListBox leftSideBox;
	@UiField ListBox rightSideBox;
	@UiField ListBox topSideBox;
	@UiField ListBox bottomSideBox;
	@UiField HeadingElement title;
	@UiField AnchorElement save;
	@UiField DivElement mainPageWindow;
	
	public void show() {
		MainPageUtils.show(panel);
	}

	public void hide() {
		panel.getElement().getStyle().setDisplay(Display.NONE);
		WidgetLockerController.hide();
	}
	
	public void setProperty(ILayoutProperty property) {
		this.property = property;
	}
	
	private void clear() {
		leftModuleBox.clear();
		rightModuleBox.clear();
		topModuleBox.clear();
		bottomModuleBox.clear();
		leftSideBox.clear();
		rightSideBox.clear();
		topSideBox.clear();
		bottomSideBox.clear();
		hasLeftCheck.setChecked(false);
		hasRightCheck.setChecked(false);
		hasTopCheck.setChecked(false);
		hasBottomCheck.setChecked(false);
	}
	
	public void setNamesModules(List<String> modulesNames) {
		LayoutDefinition layout = this.property.getLayout();
		clear();
		
		hasLeftCheck.setChecked(layout.hasLeft());
		hasRightCheck.setChecked(layout.hasRight());
		hasTopCheck.setChecked(layout.hasTop());
		hasBottomCheck.setChecked(layout.hasBottom());
		
		leftModuleBox.addItem("-");
		rightModuleBox.addItem("-");
		topModuleBox.addItem("-");
		bottomModuleBox.addItem("-");
		
		leftSideBox.addItem("Left");
		leftSideBox.addItem("Right");

		rightSideBox.addItem("Left");
		rightSideBox.addItem("Right");

		topSideBox.addItem("Top");
		topSideBox.addItem("Bottom");

		bottomSideBox.addItem("Top");
		bottomSideBox.addItem("Bottom");
		
		for(String name : modulesNames){
			leftModuleBox.addItem(name);
			rightModuleBox.addItem(name);
			topModuleBox.addItem(name);
			bottomModuleBox.addItem(name);
			
			int index = leftModuleBox.getItemCount()-1;
			
			if(layout.getLeftRelativeTo().equals(name)){
				leftModuleBox.setItemSelected(index, true);
			}
			if(layout.getRightRelativeTo().equals(name)){
				rightModuleBox.setItemSelected(index, true);
			}
			if(layout.getTopRelativeTo().equals(name)){
				topModuleBox.setItemSelected(index, true);
			}
			if(layout.getBottomRelativeTo().equals(name)){
				bottomModuleBox.setItemSelected(index, true);
			}
		}
		
		if (layout.getLeftRelativeToProperty() == Property.left){
			leftSideBox.setItemSelected(0, true);
		} else{
			leftSideBox.setItemSelected(1, true);
		}
		
		if (layout.getRightRelativeToProperty() == Property.left){
			rightSideBox.setItemSelected(0, true);
		} else{
			rightSideBox.setItemSelected(1, true);
		}
		
		if (layout.getTopRelativeToProperty() == Property.top){
			topSideBox.setItemSelected(0, true);
		} else{
			topSideBox.setItemSelected(1, true);
		}
		
		if (layout.getBottomRelativeToProperty() == Property.top){
			bottomSideBox.setItemSelected(0, true);
		} else{
			bottomSideBox.setItemSelected(1, true);
		}
	}
	
	public void saveValue(){
		LayoutDefinition layout = property.getLayout();
		
		if (hasRightCheck.isChecked()) {
			layout.setHasRight(true);
			layout.setHasLeft(hasLeftCheck.isChecked());
		} else {
			layout.setHasRight(false);
			layout.setHasLeft(true);
		}

		if (hasBottomCheck.isChecked()) {
			layout.setHasBottom(true);
			layout.setHasTop(hasTopCheck.isChecked());
		} else {
			layout.setHasBottom(false);
			layout.setHasTop(true);
		}
		
		int index;
		index = leftModuleBox.getSelectedIndex();
		layout.setLeftRelativeTo(leftModuleBox.getItemText(index));
		index = topModuleBox.getSelectedIndex();
		layout.setTopRelativeTo(topModuleBox.getItemText(index));
		index = rightModuleBox.getSelectedIndex();
		layout.setRightRelativeTo(rightModuleBox.getItemText(index));
		index = bottomModuleBox.getSelectedIndex();
		layout.setBottomRelativeTo(bottomModuleBox.getItemText(index));
		
		if (leftSideBox.getSelectedIndex() == 0) {
			layout.setLeftRelativeToProperty(Property.left);
		} else {
			layout.setLeftRelativeToProperty(Property.right);
		}

		if (rightSideBox.getSelectedIndex() == 0) {
			layout.setRightRelativeToProperty(Property.left);
		} else {
			layout.setRightRelativeToProperty(Property.right);
		}

		if (topSideBox.getSelectedIndex() == 0) {
			layout.setTopRelativeToProperty(Property.top);
		} else {
			layout.setTopRelativeToProperty(Property.bottom);
		}

		if (bottomSideBox.getSelectedIndex() == 0) {
			layout.setBottomRelativeToProperty(Property.top);
		} else {
			layout.setBottomRelativeToProperty(Property.bottom);
		}
	}
	
	public void setActionFactory(ActionFactory actionFactory) {
		onSave = actionFactory.getAction(ActionType.save);
		onModulePositionEdit = (EditModuleMainPropertiesAction) actionFactory.getAction(ActionType.editModulePosition);
	}

	private void connectHandlers() {
		Event.sinkEvents(save, Event.ONCLICK);
		Event.setEventListener(save, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt() && Event.ONTOUCHEND != event.getTypeInt()) {
					return;
				}
				
				saveValue();
				onModulePositionEdit.execute(null);
				onSave.execute();
				hide();
			}
		});
	}
	
	public void updateElementsTexts() {
		leftLabel.setInnerText(DictionaryWrapper.get("left"));
		rightLabel.setInnerText(DictionaryWrapper.get("right"));
		topLabel.setInnerText(DictionaryWrapper.get("top"));
		bottomLabel.setInnerText(DictionaryWrapper.get("bottom"));
		useLabel.setInnerText(DictionaryWrapper.get("use"));
		relativeToLabel.setInnerText(DictionaryWrapper.get("relative_to"));
		sideLabel.setInnerText(DictionaryWrapper.get("side"));
		title.setInnerText(DictionaryWrapper.get("layout_editor"));
		save.setInnerText(DictionaryWrapper.get("save"));
	}
	
	private void setStyles() {
		leftModuleBox.getElement().setAttribute("style", "position: absolute; left: 105px; top: 35px;");
		leftSideBox.getElement().setAttribute("style", "position: absolute; left: 220px; top: 35px;");
		rightModuleBox.getElement().setAttribute("style", "position: absolute; left: 105px; top: 65px;");
		rightSideBox.getElement().setAttribute("style", "position: absolute; left: 220px; top: 65px;");
		topModuleBox.getElement().setAttribute("style", "position: absolute; left: 105px; top: 95px;");
		topSideBox.getElement().setAttribute("style", "position: absolute; left: 220px; top: 95px;");
		bottomModuleBox.getElement().setAttribute("style", "position: absolute; left: 105px; top: 125px;");
		bottomSideBox.getElement().setAttribute("style", "position: absolute; left: 220px; top: 125px;");
	}
}
