package com.lorepo.iceditor.client.ui.widgets;

import static com.google.gwt.query.client.GQuery.$;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.AnchorElement;
import com.google.gwt.dom.client.DivElement;
import com.google.gwt.dom.client.InputElement;
import com.google.gwt.dom.client.SpanElement;
import com.google.gwt.dom.client.Style.Display;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.EditorConfig;
import com.lorepo.iceditor.client.actions.AbstractAction;
import com.lorepo.iceditor.client.actions.ActionFactory;
import com.lorepo.iceditor.client.actions.ChangeGridSizeAction;
import com.lorepo.iceditor.client.actions.ChangeGridVisibilityAction;
import com.lorepo.iceditor.client.actions.ActionFactory.ActionType;
import com.lorepo.iceditor.client.actions.ChangeRulersVisibilityAction;
import com.lorepo.iceditor.client.actions.SnappingModuleToGrid;
import com.lorepo.iceditor.client.actions.SnappingModuleToRulerAction;
import com.lorepo.iceditor.client.ui.dlg.ModuleInfo;
import com.lorepo.iceditor.client.ui.widgets.modules.add.AddFavouriteModuleWidget;
import com.lorepo.iceditor.client.ui.widgets.modules.add.ModulesInfoUtils;
import com.lorepo.iceditor.client.ui.widgets.utils.ActionUtils;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.addon.AddonEntry;

public class MenuWidget extends Composite {

	private static MenuWidgetUiBinder uiBinder = GWT
			.create(MenuWidgetUiBinder.class);

	interface MenuWidgetUiBinder extends UiBinder<Widget, MenuWidget> {
	}
	
	private ModulesInfoUtils modulesInfoUtils;
	
	private AbstractAction onSaveAction;
	private AbstractAction onEditCSSAction;
	private AbstractAction onEditLayoutsAction;
	private AbstractAction onSettingsAction;
	private AbstractAction onAddWCAGAction;
	private AbstractAction onSelectTemplateAction;
	private AbstractAction onCloseAction;
	private AbstractAction onAddModuleAction;
	private AbstractAction onRemoveModuleAction;
	private AbstractAction onMoveModuleUpAction;
	private AbstractAction onMoveModuleDownAction;
	private AbstractAction onBringModuleToFrontAction;
	private AbstractAction onSendBackModuleAction;
	private AbstractAction onCopyAction;
	private AbstractAction onPasteAction;
	private AbstractAction onUndoAction;
	private AbstractAction onRedoAction;
	private AbstractAction onGroupAction;
	private AbstractAction onUngroupAction;
	
	/** CHAPTERS */
	private AbstractAction onChapterAddAction;
	private AbstractAction onChapterRemoveAction;
	
	/** PAGES */
	private AbstractAction onAddEmptyPageAction;
	private AbstractAction onAddPageFromTemplateAction;
	private AbstractAction onDuplicatePageAction;
	private AbstractAction onMovePageUpAction;
	private AbstractAction onMovePageDownAction;
	private AbstractAction onMovePageToCommonsAction;
	private AbstractAction onMovePageToNavigationAction;
	private AbstractAction onRemovePageAction;
	private AbstractAction onPageCopyAction;
	private AbstractAction onPagePasteAction;
	
	private AbstractAction onFavouriteModulesPreferences;
	private AbstractAction onManageFavourites;
	
	/** GRID */
	private ChangeGridVisibilityAction onGridChangeVisibilityAction;
	private SnappingModuleToGrid onGridSnappingAction;
	private ChangeGridSizeAction onChangeGridSizeAction;
	
	/** RULERS **/
	private ChangeRulersVisibilityAction onRulersChangeVisibilityAction;
	private SnappingModuleToRulerAction onRulerSnappingAction;
	
	@UiField DivElement additionalMenuPanel;
	@UiField SpanElement favouriteModulesPanelLabel;
	@UiField HTMLPanel panel;
	
	@UiField AnchorElement save;
	@UiField AnchorElement editCSS;
	@UiField AnchorElement editLayouts;
	@UiField AnchorElement settings;
	@UiField AnchorElement selectTemplate;
	@UiField AnchorElement addWCAG;
	@UiField AnchorElement close;
	
	/** MODULES */
	@UiField AnchorElement addModule;
	@UiField HTMLPanel activities;
	@UiField HTMLPanel games;
	@UiField HTMLPanel reporting;
	@UiField HTMLPanel learnpen;
	@UiField HTMLPanel navigation;
	@UiField HTMLPanel media;
	@UiField HTMLPanel scripting;
	@UiField HTMLPanel privateAddons;
	@UiField AnchorElement removeModule;
	@UiField AnchorElement moveModuleUp;
	@UiField AnchorElement moveModuleDown;
	@UiField AnchorElement bringToFront;
	@UiField AnchorElement sendBack;
	@UiField HTMLPanel favourite;
	
	/** PAGES */
	@UiField AnchorElement addEmptyPage;
	@UiField AnchorElement addPageFromTemplate;
	@UiField AnchorElement duplicatePage;
	@UiField AnchorElement movePageUp;
	@UiField AnchorElement movePageDown;
	@UiField AnchorElement movePageToCommons;
	@UiField AnchorElement movePageToNavigation;
	@UiField AnchorElement removePage;
	@UiField AnchorElement copyPage;
	@UiField AnchorElement pastePage;
	
	// Additional menu
	@UiField AnchorElement addModuleButton;
	@UiField AnchorElement duplicatePageButton;
	@UiField AnchorElement movePageUpButton;
	@UiField AnchorElement movePageDownButton;
	@UiField AnchorElement removeModuleButton;
	@UiField AnchorElement addEmptyPageButton;
	@UiField AnchorElement addPageFromTemplateButton;
	@UiField AnchorElement removePageButton;
	@UiField AnchorElement copyPageButton;
	@UiField AnchorElement pastePageButton;
	@UiField AnchorElement copyModuleButton;
	@UiField AnchorElement pasteModuleButton;
	@UiField AnchorElement undoButton;
	@UiField AnchorElement redoButton;
	@UiField AnchorElement gridVisibilityButton;
	@UiField AnchorElement gridSnappingButton;
	@UiField AnchorElement rulersVisibilityButton;
	@UiField AnchorElement rulersSnappingButton;
	@UiField SpanElement gridSizeText;
	@UiField InputElement gridSize;
	
	@UiField AnchorElement undo;
	@UiField AnchorElement redo;
	@UiField AnchorElement copy;
	@UiField AnchorElement paste;
	@UiField AnchorElement addChapter;
	@UiField AnchorElement removeChapter;
	
	@UiField AnchorElement documentation;
	@UiField AnchorElement interactiveTutorials;
	@UiField AnchorElement modulesExamples;

	//menu
	@UiField AnchorElement presentationMenu;
	@UiField AnchorElement editMenu;
	@UiField AnchorElement chapterMenu;
	@UiField AnchorElement pageMenu;
	@UiField AnchorElement moduleMenu;
	@UiField AnchorElement helpMenu;
	@UiField SpanElement pageAddiotonalMenuPanel;
	@UiField SpanElement moduleAddiotonalMenuPanel;
	@UiField SpanElement gridAddiotonalMenuPanel;
	@UiField SpanElement rulersAddiotonalMenuPanel;
	@UiField AnchorElement groupModules;
	@UiField AnchorElement ungroupModules;
	
	@UiField AnchorElement favouriteModulesButton;
	@UiField AnchorElement manageFavourites;

	
	private ActionFactory actionFactory;
	private boolean isGridVisibleButtonPressed;
	private boolean isSnappingButtonPressed;
	private boolean isRulersVisibleButtonPressed;
	private boolean isSnappingRulersButtonPressed;

	public MenuWidget() {
		this.initWidget(uiBinder.createAndBindUi(this));
		
		this.addModuleButton.setId("addModuleButton");
		this.removeModuleButton.setId("removeModuleButton");
		this.addEmptyPageButton.setId("pageAddEmptyButton");
		this.addPageFromTemplateButton.setId("pageAddFromTemplateButton");
		this.duplicatePageButton.setId("pageDuplicateButton");
		this.movePageUpButton.setId("pageMoveUpButton");
		this.movePageDownButton.setId("pageMoveDownButton");
		this.removePageButton.setId("pageRemoveButton");
		this.copyPageButton.setId("pageCopyButton");
		this.pastePageButton.setId("pagePasteButton");
		this.copyModuleButton.setId("copyModuleButton");
		this.pasteModuleButton.setId("pasteModuleButton");
		this.undoButton.setId("pageUndoButton");
		this.redoButton.setId("pageRedoButton");
		this.gridVisibilityButton.setId("gridVisibilityButton");
		this.gridSnappingButton.setId("gridSnappingButton");
		this.gridSize.setId("gridWidthButton");
		this.rulersVisibilityButton.setId("rulersVisibilityButton");
		this.rulersSnappingButton.setId("rulersSnappingButton");
		this.favouriteModulesButton.setId("favouriteModulesButton");

		this.updateElementsTexts();
		initJavaScriptAPI(this);
	}

	private void connectHandlers() {
		ActionUtils.bindButtonWithAction(this.save, Event.ONCLICK, this.onSaveAction);
		ActionUtils.bindButtonWithAction(this.editCSS, Event.ONCLICK, this.onEditCSSAction);
		ActionUtils.bindButtonWithAction(this.editLayouts, Event.ONCLICK, this.onEditLayoutsAction);
		ActionUtils.bindButtonWithAction(this.settings, Event.ONCLICK, this.onSettingsAction);
		ActionUtils.bindButtonWithAction(this.addWCAG, Event.ONCLICK, this.onAddWCAGAction);
		ActionUtils.bindButtonWithAction(this.selectTemplate, Event.ONCLICK, this.onSelectTemplateAction);
		ActionUtils.bindButtonWithAction(this.close, Event.ONCLICK, this.onCloseAction);
		ActionUtils.bindButtonWithAction(this.addModule, Event.ONCLICK, this.onAddModuleAction);
		ActionUtils.bindButtonWithAction(this.addModuleButton, Event.ONCLICK, this.onAddModuleAction);
		ActionUtils.bindButtonWithAction(this.removeModule, Event.ONCLICK, this.onRemoveModuleAction);
		ActionUtils.bindButtonWithAction(this.removeModuleButton, Event.ONCLICK, this.onRemoveModuleAction);
		ActionUtils.bindButtonWithAction(this.moveModuleUp, Event.ONCLICK, this.onMoveModuleUpAction);
		ActionUtils.bindButtonWithAction(this.moveModuleDown, Event.ONCLICK, this.onMoveModuleDownAction);
		ActionUtils.bindButtonWithAction(this.bringToFront, Event.ONCLICK, this.onBringModuleToFrontAction);
		ActionUtils.bindButtonWithAction(this.sendBack, Event.ONCLICK, this.onSendBackModuleAction);
		ActionUtils.bindButtonWithAction(this.copy, Event.ONCLICK, this.onCopyAction);
		ActionUtils.bindButtonWithAction(this.copyModuleButton, Event.ONCLICK, this.onCopyAction);
		ActionUtils.bindButtonWithAction(this.paste, Event.ONCLICK, this.onPasteAction);
		ActionUtils.bindButtonWithAction(this.pasteModuleButton, Event.ONCLICK, this.onPasteAction);
		ActionUtils.bindButtonWithAction(this.undo, Event.ONCLICK, this.onUndoAction);
		ActionUtils.bindButtonWithAction(this.undoButton, Event.ONCLICK, this.onUndoAction);
		ActionUtils.bindButtonWithAction(this.redo, Event.ONCLICK, this.onRedoAction);
		ActionUtils.bindButtonWithAction(this.redoButton, Event.ONCLICK, this.onRedoAction);
		ActionUtils.bindButtonWithAction(this.groupModules, Event.ONCLICK, this.onGroupAction);
		ActionUtils.bindButtonWithAction(this.ungroupModules, Event.ONCLICK, this.onUngroupAction);
		
		/** CHAPTERS */
		ActionUtils.bindButtonWithAction(this.addChapter, Event.ONCLICK, this.onChapterAddAction);
		ActionUtils.bindButtonWithAction(this.removeChapter, Event.ONCLICK, this.onChapterRemoveAction);
		
		/** PAGES */
		ActionUtils.bindButtonWithAction(this.addEmptyPage, Event.ONCLICK, this.onAddEmptyPageAction);
		ActionUtils.bindButtonWithAction(this.addEmptyPageButton, Event.ONCLICK, this.onAddEmptyPageAction);
		ActionUtils.bindButtonWithAction(this.addPageFromTemplate, Event.ONCLICK, this.onAddPageFromTemplateAction);
		ActionUtils.bindButtonWithAction(this.addPageFromTemplateButton, Event.ONCLICK, this.onAddPageFromTemplateAction);
		ActionUtils.bindButtonWithAction(this.removePage, Event.ONCLICK, this.onRemovePageAction);
		ActionUtils.bindButtonWithAction(this.removePageButton, Event.ONCLICK, this.onRemovePageAction);
		ActionUtils.bindButtonWithAction(this.duplicatePage, Event.ONCLICK, this.onDuplicatePageAction);
		ActionUtils.bindButtonWithAction(this.duplicatePageButton, Event.ONCLICK, this.onDuplicatePageAction);
		ActionUtils.bindButtonWithAction(this.movePageDown, Event.ONCLICK, this.onMovePageDownAction);
		ActionUtils.bindButtonWithAction(this.movePageDownButton, Event.ONCLICK, this.onMovePageDownAction);
		ActionUtils.bindButtonWithAction(this.movePageUp, Event.ONCLICK, this.onMovePageUpAction);
		ActionUtils.bindButtonWithAction(this.movePageUpButton, Event.ONCLICK, this.onMovePageUpAction);
		ActionUtils.bindButtonWithAction(this.movePageToCommons, Event.ONCLICK, this.onMovePageToCommonsAction);
		ActionUtils.bindButtonWithAction(this.movePageToNavigation, Event.ONCLICK, this.onMovePageToNavigationAction);
		ActionUtils.bindButtonWithAction(this.copyPage, Event.ONCLICK, this.onPageCopyAction);
		ActionUtils.bindButtonWithAction(this.copyPageButton, Event.ONCLICK, this.onPageCopyAction);
		ActionUtils.bindButtonWithAction(this.pastePage, Event.ONCLICK, this.onPagePasteAction);
		ActionUtils.bindButtonWithAction(this.pastePageButton, Event.ONCLICK, this.onPagePasteAction);
		
		/** GRID */
		ActionUtils.bindButtonWithAction(this.gridVisibilityButton, Event.ONCLICK, this.onGridChangeVisibilityAction);
		ActionUtils.bindButtonWithAction(this.gridSnappingButton, Event.ONCLICK, this.onGridSnappingAction);
		ActionUtils.bindButtonWithAction(this.gridSize, Event.ONCHANGE, this.onChangeGridSizeAction);
		
		/** RULERS */
		ActionUtils.bindButtonWithAction(this.rulersVisibilityButton, Event.ONCLICK, this.onRulersChangeVisibilityAction);
		ActionUtils.bindButtonWithAction(this.rulersSnappingButton, Event.ONCLICK, this.onRulerSnappingAction);
		
		ActionUtils.bindButtonWithAction(this.favouriteModulesButton, Event.ONCLICK, this.onFavouriteModulesPreferences);
		ActionUtils.bindButtonWithAction(this.manageFavourites, Event.ONCLICK, this.onManageFavourites);
	}

	public void setActionFactory(ActionFactory actionFactory) {
		this.actionFactory = actionFactory;
		
		this.onSaveAction = actionFactory.getAction(ActionType.save);
		this.onEditCSSAction = actionFactory.getAction(ActionType.editCSS);
		this.onEditLayoutsAction = actionFactory.getAction(ActionType.showSemiResponsivePanel);
		this.onSettingsAction = actionFactory.getAction(ActionType.preferences);
		this.onAddWCAGAction = actionFactory.getAction(ActionType.addWCAG);
		this.onSelectTemplateAction = actionFactory.getAction(ActionType.selectTemplate);
		this.onCloseAction = actionFactory.getAction(ActionType.closeEditor);
		this.onAddModuleAction = actionFactory.getAction(ActionType.addModule);
		this.onRemoveModuleAction = actionFactory.getAction(ActionType.removeModule);
		this.onMoveModuleUpAction = actionFactory.getAction(ActionType.moveModuleUp);
		this.onMoveModuleDownAction = actionFactory.getAction(ActionType.moveModuleDown);
		this.onSendBackModuleAction = actionFactory.getAction(ActionType.sendBackModule);
		this.onBringModuleToFrontAction = actionFactory.getAction(ActionType.bringToFrontModule);
		this.onCopyAction = actionFactory.getAction(ActionType.copy);
		this.onPasteAction = actionFactory.getAction(ActionType.paste);
		this.onUndoAction = actionFactory.getAction(ActionType.undo);
		this.onRedoAction = actionFactory.getAction(ActionType.redo);
		this.onGroupAction = actionFactory.getAction(ActionType.groupModules);
		this.onUngroupAction = actionFactory.getAction(ActionType.ungroupModules);
		
		/** CHAPTERS */
		this.onChapterAddAction = actionFactory.getAction(ActionType.addChapter);
		this.onChapterRemoveAction = actionFactory.getAction(ActionType.removeChapter);
		
		/** PAGES */
		this.onAddEmptyPageAction = actionFactory.getAction(ActionType.addEmptyPage);
		this.onAddPageFromTemplateAction = actionFactory.getAction(ActionType.addPageFromTemplate);
		this.onDuplicatePageAction = actionFactory.getAction(ActionType.duplicatePage);
		this.onMovePageUpAction = actionFactory.getAction(ActionType.pageUp);
		this.onMovePageDownAction = actionFactory.getAction(ActionType.pageDown);
		this.onMovePageToCommonsAction = actionFactory.getAction(ActionType.moveNaviToCommons);
		this.onMovePageToNavigationAction = actionFactory.getAction(ActionType.moveCommonsToNavi);
		this.onRemovePageAction = actionFactory.getAction(ActionType.removePage);
		this.onPageCopyAction = actionFactory.getAction(ActionType.copyPage);
		this.onPagePasteAction = actionFactory.getAction(ActionType.pastePage);
		
		/** GRID */
		this.onGridChangeVisibilityAction = (ChangeGridVisibilityAction) actionFactory.getAction(ActionType.changeGridVisibility);
		this.onGridSnappingAction = (SnappingModuleToGrid) actionFactory.getAction(ActionType.gridSnapping);
		this.onChangeGridSizeAction = (ChangeGridSizeAction) actionFactory.getAction(ActionType.changeGridSize);
		
		/** SNAPPING */
		this.onRulersChangeVisibilityAction = (ChangeRulersVisibilityAction) actionFactory.getAction(ActionType.changeRulersVisibility);
		this.onRulerSnappingAction = (SnappingModuleToRulerAction) actionFactory.getAction(ActionType.rulerSnapping);
		
		this.onFavouriteModulesPreferences = actionFactory.getAction(ActionType.editFavouriteModules);
		this.onManageFavourites = actionFactory.getAction(ActionType.editFavouriteModules);
		
		this.connectHandlers();
	}

	private static native void initJavaScriptAPI(MenuWidget x) /*-{
		$wnd.iceChangeGridVisibility = function(isGridVisibilityButtonPressed) {
			x.@com.lorepo.iceditor.client.ui.widgets.MenuWidget::onChangeGridVisibility(Z)(isGridVisibilityButtonPressed);
		};
		
		$wnd.iceChangeGridSize = function(size) {
			x.@com.lorepo.iceditor.client.ui.widgets.MenuWidget::onChangeGridSize(I)(size);
		};
		
		$wnd.iceShouldSnappingToGrid = function(isSnappingButtonPressed) {
			x.@com.lorepo.iceditor.client.ui.widgets.MenuWidget::onShouldSnappingToGrid(Z)(isSnappingButtonPressed);
		};
		
		$wnd.iceChangeRulersVisibility = function(isRulersVisibilityButtonPressed) {
			x.@com.lorepo.iceditor.client.ui.widgets.MenuWidget::onChangeRulersVisibility(Z)(isRulersVisibilityButtonPressed);
		};
		
		$wnd.iceShouldSnappingToRulers = function(isSnappingButtonPressed) {
			x.@com.lorepo.iceditor.client.ui.widgets.MenuWidget::onShouldSnappingToRulers(Z)(isSnappingButtonPressed);
		};
	}-*/;
	
	private void onChangeGridVisibility(boolean gridVisibilityButtonPressed) {
		this.isGridVisibleButtonPressed = gridVisibilityButtonPressed;
		this.onGridChangeVisibilityAction.execute(gridVisibilityButtonPressed);
	}
	
	private void onChangeGridSize(int size) {
		this.onChangeGridSizeAction.execute(size);
	}
	
	private void onShouldSnappingToGrid(boolean snappingButtonPressed) {
		this.isSnappingButtonPressed = snappingButtonPressed;
		this.onGridSnappingAction.execute(snappingButtonPressed);
	}

	private void onChangeRulersVisibility(boolean rulersVisibilityButtonPressed) {
		this.isRulersVisibleButtonPressed = rulersVisibilityButtonPressed;
		this.onRulersChangeVisibilityAction.execute(rulersVisibilityButtonPressed);
	}
	
	private void onShouldSnappingToRulers(boolean snappingRulersButtonPressed) {
		this.isSnappingRulersButtonPressed = snappingRulersButtonPressed;
		this.onRulerSnappingAction.execute(snappingRulersButtonPressed);
	}
	
	private String validGridSize(String gridSize) {
		try {
			int gridSizeAsNumber = Integer.parseInt(gridSize);
			
			return gridSizeAsNumber < 2 ? "2" : gridSize;
			
		} catch (NumberFormatException e){
			return "20";
		}
	}
	
	public void setGridOptions(Content content) {
		boolean shouldGridVisible = Boolean.parseBoolean(content.getMetadataValue("useGrid"));
		boolean shouldSnapping = Boolean.parseBoolean(content.getMetadataValue("snapToGrid"));
		String gridSize = this.validGridSize(content.getMetadataValue("gridSize"));
		
		this.setGridVisible(shouldGridVisible);
		final String initialGridSize = "20";
		
		if (gridSize == null || Integer.parseInt(gridSize) < 2) {
			gridSize = initialGridSize;
		}
		this.setGridSize(gridSize);
		this.setSnappingModuleToGrid(shouldSnapping);
	}
	
	public void setRulersOptions(Content content) {
		boolean shouldRulersVisible = Boolean.parseBoolean(content.getMetadataValue("useRulers"));
		boolean shouldSnapping = Boolean.parseBoolean(content.getMetadataValue("snapToRulers"));
		
		this.setRulersVisible(shouldRulersVisible);
		this.setSnappingModuleToRulers(shouldSnapping);
	}
	
	private void setRulersVisible(boolean shouldRulersVisible) {
		if ((shouldRulersVisible && !this.isRulersVisibleButtonPressed) || (!shouldRulersVisible && this.isRulersVisibleButtonPressed)) {
			triggerClick("rulersVisibility");
		}
	}
	
	private void setSnappingModuleToRulers(boolean shouldSnapping) {
		if ((shouldSnapping && !this.isSnappingRulersButtonPressed) || (!shouldSnapping && this.isSnappingRulersButtonPressed)) {
			triggerClick("rulersSnapping");
		}
	}	
	
	protected static native void triggerClick(String button) /*-{
		if(typeof $wnd.iceTriggerClick == 'function') {
		  $wnd.iceTriggerClick(button);
		}
	}-*/;
	
	private static native void iceGridOn(String size) /*-{
		if(typeof $wnd.iceGridOn == 'function') {
		  $wnd.iceGridOn(size);
		}
	}-*/;
	
	private void setGridVisible(boolean shouldGridVisible) {
		if ((shouldGridVisible && !this.isGridVisibleButtonPressed) || (!shouldGridVisible && this.isGridVisibleButtonPressed)) {
			triggerClick("gridVisibility");
		}
	}
	
	private void setSnappingModuleToGrid(boolean shouldSnapping) {
		if ((shouldSnapping && !this.isSnappingButtonPressed) || (!shouldSnapping && this.isSnappingButtonPressed)) {
			triggerClick("gridSnapping");
		}
	}
	
	private void setGridSize(String size) {
		final String initialSize = "20";
		
		if (size == null) {
			size = initialSize;
		}
		
		this.gridSize.setValue(size);
		iceGridOn(size);
	}

	public void setModulesInfoUtils(ModulesInfoUtils modulesInfoUtils) {
		this.fillModuleMenu(this.favourite, modulesInfoUtils.getCategory(DictionaryWrapper.get("favourite_menu")));
		this.fillModuleMenu(this.activities, modulesInfoUtils.getCategory(DictionaryWrapper.get("activities_menu")));
		this.fillModuleMenu(this.games, modulesInfoUtils.getCategory(DictionaryWrapper.get("games_menu")));
		this.fillModuleMenu(this.reporting, modulesInfoUtils.getCategory(DictionaryWrapper.get("reporting_menu")));
		this.fillModuleMenu(this.learnpen, modulesInfoUtils.getCategory(DictionaryWrapper.get("learn_pen_menu")));
		this.fillModuleMenu(this.navigation, modulesInfoUtils.getCategory(DictionaryWrapper.get("navigation_menu")));
		this.fillModuleMenu(this.media, modulesInfoUtils.getCategory(DictionaryWrapper.get("media_menu")));
		this.fillModuleMenu(this.scripting, modulesInfoUtils.getCategory(DictionaryWrapper.get("scripting_menu")));
	}

	public void updateFavouriteModulesMenu(HashMap<String, ModuleInfo> modules) {
		this.panel.clear();
		this.favourite.clear();
		
		for (ModuleInfo moduleInfo : modules.values()) {
			AddFavouriteModuleWidget moduleWidget = new AddFavouriteModuleWidget();
			moduleWidget.setModule(moduleInfo);
			this.panel.add(moduleWidget);
			
			MainMenuItemWidget item = new MainMenuItemWidget();
			item.setName(moduleInfo.name);
			item.setCommand(moduleInfo.command);
			
			this.favourite.add(item);
		}
	}
	
	private void fillModuleMenu(HTMLPanel container, List<ModuleInfo> category) {
		for (ModuleInfo moduleInfo : category) {
			MainMenuItemWidget item = new MainMenuItemWidget();
			item.setName(moduleInfo.name);
			item.setCommand(moduleInfo.command);
			
			container.add(item);
		}
	}

	public void setPrivateAddons(List<AddonEntry> entries) {
		List<MainMenuItemWidget> uiFields = new ArrayList<MainMenuItemWidget>();
		for (AddonEntry entry : entries) {
			MainMenuItemWidget item = new MainMenuItemWidget();

			String name = entry.getName();
			if (DictionaryWrapper.contains(name)) {
				name = DictionaryWrapper.get(name);
			}
			item.setName(name);
			
			item.setCommand(this.actionFactory.getInsertAddonAction(entry));
			
			uiFields.add(item);
		}
		
		Collections.sort(uiFields, new Comparator<MainMenuItemWidget>() {
	        @Override
	        public int compare(MainMenuItemWidget field2, MainMenuItemWidget field1)
	        {
	            return  field2.getName().compareTo(field1.getName());
	        }
	    });
		
		for (MainMenuItemWidget field : uiFields) {
			this.privateAddons.add(field);
		}
	}
	
	public void updateElementsTexts() {
		// Presentation
		this.save.setInnerText(DictionaryWrapper.get("save_menu"));
		this.selectTemplate.setInnerText(DictionaryWrapper.get("select_template_menu"));
		this.editCSS.setInnerText(DictionaryWrapper.get("edit_css_menu"));
		this.editLayouts.setInnerText(DictionaryWrapper.get("edit_layouts_menu"));
		this.settings.setInnerText(DictionaryWrapper.get("preferences"));
		this.addWCAG.setInnerText(DictionaryWrapper.get("wcag"));
		this.close.setInnerText(DictionaryWrapper.get("close_menu"));
		
		// Edit
		this.undo.setInnerText(DictionaryWrapper.get("undo_menu"));
		this.redo.setInnerText(DictionaryWrapper.get("redo_menu"));
		this.copy.setInnerText(DictionaryWrapper.get("copy_menu"));
		this.paste.setInnerText(DictionaryWrapper.get("paste_menu"));
		this.copyPage.setInnerText(DictionaryWrapper.get("export_page_menu"));
		this.pastePage.setInnerText(DictionaryWrapper.get("import_page_menu"));
		
		// Chapter
		this.addChapter.setInnerText(DictionaryWrapper.get("add_chapter_menu"));
		this.removeChapter.setInnerText(DictionaryWrapper.get("add_remove_chapter_menu"));
		
		//Help
		documentation.setInnerHTML(DictionaryWrapper.get("documentation_menu"));
		interactiveTutorials.setInnerHTML(DictionaryWrapper.get("interactive_tutorials_menu"));
		modulesExamples.setInnerHTML(DictionaryWrapper.get("modules_examples"));

		// Page
		this.addEmptyPage.setInnerText(DictionaryWrapper.get("add_empty_page_menu"));
		this.addPageFromTemplate.setInnerText(DictionaryWrapper.get("add_page_from_template_menu"));
		this.duplicatePage.setInnerText(DictionaryWrapper.get("duplicate_page_menu"));
		this.movePageUp.setInnerText(DictionaryWrapper.get("move_up_menu"));
		this.movePageDown.setInnerText(DictionaryWrapper.get("move_down_menu"));
		this.movePageToCommons.setInnerText(DictionaryWrapper.get("move_to_commons_menu"));
		this.movePageToNavigation.setInnerText(DictionaryWrapper.get("move_to_navigation_menu"));
		this.removePage.setInnerText(DictionaryWrapper.get("remove_page_menu"));
		
		// Menu
		this.presentationMenu.setInnerText(DictionaryWrapper.get("presentation_menu"));
		this.editMenu.setInnerText(DictionaryWrapper.get("edit_menu"));
		this.chapterMenu.setInnerText(DictionaryWrapper.get("chapter_menu"));
		this.pageMenu.setInnerText(DictionaryWrapper.get("page_menu"));
		this.moduleMenu.setInnerText(DictionaryWrapper.get("module_menu"));
		helpMenu.setInnerText(DictionaryWrapper.get("help_menu"));
		
		// Additional menu panel page
		this.pageAddiotonalMenuPanel.setInnerText(DictionaryWrapper.get("page_menu"));
		this.moduleAddiotonalMenuPanel.setInnerText(DictionaryWrapper.get("module_menu"));
		this.gridAddiotonalMenuPanel.setInnerText(DictionaryWrapper.get("grid"));
		this.gridSizeText.setInnerText(DictionaryWrapper.get("size"));
		this.rulersAddiotonalMenuPanel.setInnerText(DictionaryWrapper.get("rulers"));
		this.favouriteModulesPanelLabel.setInnerText(DictionaryWrapper.get("favourite_menu"));
		
		this.addEmptyPageButton.setAttribute("data-tooltip", DictionaryWrapper.get("add_empty_page_menu"));
		this.addPageFromTemplateButton.setAttribute("data-tooltip", DictionaryWrapper.get("add_page_from_template_menu"));
		this.duplicatePageButton.setAttribute("data-tooltip", DictionaryWrapper.get("duplicate_page_menu"));
		this.copyPageButton.setAttribute("data-tooltip", DictionaryWrapper.get("export_page_menu"));
		this.pastePageButton.setAttribute("data-tooltip", DictionaryWrapper.get("import_page_menu"));
		this.removePageButton.setAttribute("data-tooltip", DictionaryWrapper.get("remove_page_menu"));
		this.movePageUpButton.setAttribute("data-tooltip", DictionaryWrapper.get("move_page_up_menu"));
		this.movePageDownButton.setAttribute("data-tooltip", DictionaryWrapper.get("move_page_down_menu"));
		this.undoButton.setAttribute("data-tooltip", DictionaryWrapper.get("undo_menu"));
		
		this.addModuleButton.setAttribute("data-tooltip", DictionaryWrapper.get("add_module_panel"));
		this.removeModuleButton.setAttribute("data-tooltip", DictionaryWrapper.get("remove_module_panel"));
		this.copyModuleButton.setAttribute("data-tooltip", DictionaryWrapper.get("copy_module_panel"));
		this.pasteModuleButton.setAttribute("data-tooltip", DictionaryWrapper.get("paste_module_panel"));
		this.redoButton.setAttribute("data-tooltip", DictionaryWrapper.get("redo_menu"));
		
		this.gridVisibilityButton.setAttribute("data-tooltip", DictionaryWrapper.get("grid_visibility"));
		this.gridSnappingButton.setAttribute("data-tooltip", DictionaryWrapper.get("grid_snapping"));
		this.gridSize.setAttribute("data-tooltip", DictionaryWrapper.get("grid_size_menu"));
		
		this.rulersVisibilityButton.setAttribute("data-tooltip", DictionaryWrapper.get("rulers_visibility"));
		this.rulersSnappingButton.setAttribute("data-tooltip", DictionaryWrapper.get("rulers_snapping"));
		
		this.favouriteModulesButton.setAttribute("data-tooltip", DictionaryWrapper.get("select_fav_modules"));
		
		$(this.addModule).parent().find("a").text(DictionaryWrapper.get("add_module_menu"));
		$(this.manageFavourites).parent().find("a").text(DictionaryWrapper.get("manage_favourites"));
		$(this.activities).parent().find("a").text(DictionaryWrapper.get("activities_menu"));
		$(this.games).parent().find("a").text(DictionaryWrapper.get("games_menu"));
		$(this.reporting).parent().find("a").text(DictionaryWrapper.get("reporting_menu"));
		$(this.learnpen).parent().find("a").text(DictionaryWrapper.get("learn_pen_menu"));
		$(this.navigation).parent().find("a").text(DictionaryWrapper.get("navigation_menu"));
		$(this.media).parent().find("a").text(DictionaryWrapper.get("media_menu"));
		$(this.scripting).parent().find("a").text(DictionaryWrapper.get("scripting_menu"));
		$(this.privateAddons).parent().find("a").text(DictionaryWrapper.get("private_menu"));
		$(this.groupModules).parent().find("a").text(DictionaryWrapper.get("group_modules_menu"));
		$(this.ungroupModules).parent().find("a").text(DictionaryWrapper.get("ungroup_modules_menu"));
		$(this.bringToFront).parent().find("a").text(DictionaryWrapper.get("bring_to_front_menu"));
		$(this.sendBack).parent().find("a").text(DictionaryWrapper.get("send_back_menu"));
		$(this.moveModuleUp).parent().find("a").text(DictionaryWrapper.get("move_module_up_menu"));
		$(this.moveModuleDown).parent().find("a").text(DictionaryWrapper.get("move_module_down_menu"));
		$(this.removeModule).parent().find("a").text(DictionaryWrapper.get("remove_menu"));
		$(this.favourite).parent().find("a").text(DictionaryWrapper.get("favourite_menu"));
	}

	public void setEditorConfig(EditorConfig config) {
		if (!config.showTemplates) {
			this.selectTemplate.getStyle().setDisplay(Display.NONE);
		}
	}

	public boolean getRulerVisibility() {
		return this.isRulersVisibleButtonPressed;
	}

	public boolean getRulerSnapping() {
		return this.isSnappingRulersButtonPressed;
	}
}
