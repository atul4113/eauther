package com.lorepo.iceditor.client.ui.widgets.content;

import static com.google.gwt.query.client.GQuery.$;

import java.util.ArrayList;
import java.util.List;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.AnchorElement;
import com.google.gwt.dom.client.HeadingElement;
import com.google.gwt.dom.client.Style.Display;
import com.google.gwt.query.client.Function;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.api.IModuleModel;
import com.lorepo.iceditor.client.actions.AbstractAction;
import com.lorepo.iceditor.client.actions.ActionFactory;
import com.lorepo.iceditor.client.actions.ActionFactory.ActionType;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.widgets.utils.ActionUtils;
import com.lorepo.iceditor.client.ui.widgets.utils.MainPageUtils;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;

public class AddWCAGWidget extends Composite {

	private static AddWCAGWidgetUiBinder uiBinder = GWT.create(AddWCAGWidgetUiBinder.class);

	interface AddWCAGWidgetUiBinder extends UiBinder<Widget, AddWCAGWidget> {}
	
	@UiField HTMLPanel panel;
	@UiField HTMLPanel modulesList;
	@UiField AnchorElement addTTS;
	@UiField HeadingElement title;
	
	AbstractAction onAddTTSToPresentationAction;
	AbstractAction onLoadMissingWCAGProperties;
	AppController appController;
	boolean first = false;

	private final List<AddWCAGItemWidget> modules = new ArrayList<AddWCAGItemWidget>();
	
	public AddWCAGWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		
		panel.getElement().setId("addWCAGPage");
		updateElementsTexts();
		bindHandlers();
		
		hide();
	}
	
	public void show() {
		MainPageUtils.show(panel);
		if (!first) {
			first = true;
			$("#content").on("mousedown", new Function(){
				public void f() {
					if (MainPageUtils.isWindowOpened("addWCAGPage")) {
						hide();
					}
				}
			});
		}
	}

	public void hide() {
		panel.getElement().getStyle().setDisplay(Display.NONE);
		WidgetLockerController.hide();
	}
	
	public void updateElementsTexts() {
		
		title.setInnerText(DictionaryWrapper.get("wcag"));
		addTTS.setInnerText(DictionaryWrapper.get("Editor_add_missing_tts"));
	}
	
	public void setActionFactory(ActionFactory actionFactory) {
		onAddTTSToPresentationAction = actionFactory.getAction(ActionType.addTTSToPresentation);	
		ActionUtils.bindButtonWithAction(this.addTTS, Event.ONCLICK, this.onAddTTSToPresentationAction);
	}
	
	public void setAppController(AppController appController) {
		this.appController = appController;
	}
	
	public void bindHandlers() {
		
		$(".mainPageCloseBtn").on("click", new Function(){
			public void f() {
				if (MainPageUtils.isWindowOpened("addWCAGPage")) {
					hide();
				}
			}
		});

	}

	
	public void addItemToList(Page page, IModuleModel module, String errorMessage, boolean isCommon) {
		AddWCAGItemWidget moduleWidget = new AddWCAGItemWidget();
		moduleWidget.setId(module);
		moduleWidget.setIsCommon(isCommon);
		moduleWidget.setPageName(page);
		moduleWidget.setErrorMessage(errorMessage);
		moduleWidget.setAppController(appController);
		modules.add(moduleWidget);
		modulesList.add(moduleWidget);
	}
	
	public void clearItemList() {
		modulesList.clear();
		modules.clear();
	}
}
