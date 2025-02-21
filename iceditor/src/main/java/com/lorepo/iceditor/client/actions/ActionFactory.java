package com.lorepo.iceditor.client.actions;

import java.util.HashMap;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.icplayer.client.model.addon.AddonEntry;

public class ActionFactory {

	public enum ActionType{
	
		// Presentation actions
		addChapter,
		removeChapter,
		editChapter,
		save,
		showPreview,
		hidePreview,
		showPreviewInNewTab,
		abandonChanges,
		closeEditor,
		selectTemplate,
		editCSS,
		showSemiResponsivePanel,
		modalOpened,
		addTTSToPresentation,
		addWCAG,
		loadMissingWCAGProperties,
		// Page Actions
		editPage,
		addPage,
		addPageFromTemplate,
		addEmptyPage,
		duplicatePage,
		copyPage, 
		pastePage,
		changePageHeight,
		insertModule,
		pageDown,
		pageUp,
		removePage,
		renamePage,
		pageSelected,
		moveNaviToCommons,
		moveCommonsToNavi,
		pageStylesChanged,
		// Page UI actions
		uiPageSelected,
		uiSingleModuleSelected,
		uiModuleSelected,
		uiModuleDeselected,
		uiModulePositionChanged,
		uiModuleDimensionsChanged,
		uiPageDimensionsChanged,
		uiShowModuleEditor,
		// Edit menu
		undo,
		redo,
		copy,
		paste,
		addModule,
		// Insert module actions
		insertCheckModule,
		insertChoiceModule,
		insertFeedbackModule,
		insertImageModule,
		insertImageSourceModule,
		insertImageGapModule,
		insertCheckCounterModule,
		insertErrorCounterModule,
		insertLimitedCheckModule,
		insertLimitedResetModule,
		insertOrderingModule,
		insertReportModule,
		insertPageProgressModule,
		insertShapeModule,
		insertTextModule,
		insertSourceListModule,
		insertYoutubeModule,
		// Module actions
		editModule,
		moduleStylesChanged,
		bringToFrontModule,
		sendBackModule,
		removeModule, moveModuleUp, moveModuleDown, sortModules,   
		groupModules, ungroupModules, 
		preferences, splitPage, lockModule, unlockModule,
		showModuleInEditor, hideModuleInEditor, insertLessonResetModule,
		editModulePosition,
		addAllTextToSpeech, sortModulesTextToSpeech,
		// Grid actions
		changeGridVisibility, gridSnapping, changeGridSize,
		// Ruler actions
		changeRulersVisibility, rulerSnapping, uiChangeRulerPosition, updateRulersPositions, editFavouriteModules,
		// Layout actions
		addNewCssStyle, deleteCssStyle, setAsDefaultCSSStyle, addSemiResponsiveLayout, deleteSemiResponsiveLayout, setAsDefaultSemiResponsiveLayout,
		refreshSemiResponsiveLayoutEditingWidgets, changeCurrentContentSemiResponsiveLayout, syncCurrentPageSemiResponsiveLayouts,
		setSemiResponsiveLayoutStyle, refreshSemiResponsiveCSSStyle, copyLastSeenLayoutConfiguration, markAsVisited, changePageSemiResponsiveLayout,
		copyPageLayout, listAvailableLayouts,
		// Notifications
		showNotification
	};
	
	private HashMap<ActionType, AbstractAction>	actions;
	private AppController appController;
	
	
	public ActionFactory(AppController controller){
		appController = controller;
		initStaticActions();
	}


	private void initStaticActions() {
		actions = new HashMap<ActionFactory.ActionType, AbstractAction>();

		actions.put(ActionType.addChapter, new AddChapterAction(appController.getActionServices()));
		actions.put(ActionType.removeChapter, new RemoveChapterAction(appController.getActionServices()));
		actions.put(ActionType.editChapter, new EditChapterAction(appController));
		actions.put(ActionType.selectTemplate, new SelectTemplateAction(appController));
		actions.put(ActionType.addTTSToPresentation, new AddTTSToPresentationAction(appController));
		actions.put(ActionType.addWCAG, new AddWCAGAction(appController));
		actions.put(ActionType.loadMissingWCAGProperties, new LoadMissingWCAGPropertiesAction(appController));
		actions.put(ActionType.editCSS, new EditCSSAction(appController));
		actions.put(ActionType.showSemiResponsivePanel, new ShowSemiResponsivePanel(appController));
		actions.put(ActionType.closeEditor, new CloseEditorAction(appController.getActionServices()));
		actions.put(ActionType.showPreview, new PreviewAction(appController.getActionServices()));
		actions.put(ActionType.hidePreview, new HidePreviewAction(appController.getActionServices()));
		actions.put(ActionType.showPreviewInNewTab, new PreviewInNewTabAction(appController.getActionServices()));
		actions.put(ActionType.abandonChanges, new AbandonChangesAction(appController.getActionServices()));
		actions.put(ActionType.modalOpened, new ModalOpenedAction(appController));
		
		actions.put(ActionType.editPage, new EditPageAction(appController));
		actions.put(ActionType.addPage, new AddPageAction(appController.getActionServices()));
		actions.put(ActionType.addEmptyPage, new AddEmptyPageAction(appController.getActionServices()));
		actions.put(ActionType.addPageFromTemplate, new AddPageFromTemplateAction(appController.getActionServices()));
		actions.put(ActionType.duplicatePage, new DuplicatePageAction(appController.getActionServices()));
		actions.put(ActionType.copyPage, new ExportPageAction(appController.getActionServices()));
		actions.put(ActionType.pastePage, new ImportPageAction(appController.getActionServices()));
		actions.put(ActionType.changePageHeight, new ChangePageHeightAction(appController));
		actions.put(ActionType.splitPage, new SplitPageAction(appController.getActionServices()));
		actions.put(ActionType.copy, new CopyAction(appController));
		actions.put(ActionType.undo, new UndoAction(appController.getActionServices()));
		actions.put(ActionType.redo, new RedoAction(appController.getActionServices()));
		actions.put(ActionType.removePage, new RemovePageAction(appController));
		actions.put(ActionType.renamePage, new RenamePageAction(appController));
		actions.put(ActionType.pageUp, new PageUpAction(appController));
		actions.put(ActionType.pageDown, new PageDownAction(appController));
		actions.put(ActionType.moveNaviToCommons, new MoveNaviToCommonsAction(appController));
		actions.put(ActionType.moveCommonsToNavi, new MoveCommonsToNaviAction(appController));
		actions.put(ActionType.paste, new PasteAction(appController));
		actions.put(ActionType.save, new SaveAction(appController.getActionServices()));
		actions.put(ActionType.preferences, new PreferencesAction(appController.getActionServices()));
		actions.put(ActionType.pageSelected, new PageSelectedAction(appController));
		actions.put(ActionType.pageStylesChanged, new PageStylesChangedAction(appController));
		
		actions.put(ActionType.uiPageSelected, new UIPageSelectedAction(appController));
		actions.put(ActionType.uiSingleModuleSelected, new UISingleModuleSelectedAction(appController));
		actions.put(ActionType.uiModuleSelected, new UIModuleSelectedAction(appController));
		actions.put(ActionType.uiModuleDeselected, new UIModuleDeselectedAction(appController));
		actions.put(ActionType.uiModulePositionChanged, new UIModulePositionChangedAction(appController));
		actions.put(ActionType.uiModuleDimensionsChanged, new UIModuleDimensionsChangedAction(appController));
		actions.put(ActionType.uiPageDimensionsChanged, new UIPageDimensionsChangedAction(appController));
		actions.put(ActionType.uiShowModuleEditor, new UIShowModuleDefaultPropertyEditorAction(appController));

		actions.put(ActionType.addModule, new AddModuleAction(appController));
		actions.put(ActionType.insertChoiceModule, new InsertModuleAction(appController, "choiceModule"));
		actions.put(ActionType.insertCheckModule, new InsertModuleAction(appController, "checkModule"));
		actions.put(ActionType.insertFeedbackModule, new InsertModuleAction(appController, "feedbackModule"));
		actions.put(ActionType.insertImageModule, new InsertModuleAction(appController, "imageModule"));
		actions.put(ActionType.insertImageSourceModule, new InsertModuleAction(appController, "imageSourceModule"));
		actions.put(ActionType.insertImageGapModule, new InsertModuleAction(appController, "imageGapModule"));
		actions.put(ActionType.insertLimitedCheckModule, new InsertModuleAction(appController, "limitedCheckModule"));
		actions.put(ActionType.insertLimitedResetModule, new InsertModuleAction(appController, "limitedResetModule"));
		actions.put(ActionType.insertLessonResetModule, new InsertModuleAction(appController, "lessonResetModule"));
		actions.put(ActionType.insertOrderingModule, new InsertModuleAction(appController, "orderingModule"));
		actions.put(ActionType.insertReportModule, new InsertModuleAction(appController, "reportModule"));
		actions.put(ActionType.insertCheckCounterModule, new InsertModuleAction(appController, "checkCounterModule"));
		actions.put(ActionType.insertErrorCounterModule, new InsertModuleAction(appController, "errorCounterModule"));
		actions.put(ActionType.insertShapeModule, new InsertModuleAction(appController, "shapeModule"));
		actions.put(ActionType.insertPageProgressModule, new InsertModuleAction(appController, "pageProgressModule"));
		actions.put(ActionType.insertSourceListModule, new InsertModuleAction(appController, "sourceListModule"));
		actions.put(ActionType.insertTextModule, new InsertModuleAction(appController, "textModule"));
		actions.put(ActionType.insertYoutubeModule, new InsertModuleAction(appController, "youtubeModule"));
		
		actions.put(ActionType.editModule, new EditModuleAction(appController));
		actions.put(ActionType.moduleStylesChanged, new ModuleStylesChangedAction(appController));
		actions.put(ActionType.bringToFrontModule, new BringToFrontModuleAction(appController));
		actions.put(ActionType.sendBackModule, new SendBackModuleAction(appController));
		actions.put(ActionType.moveModuleDown, new MoveModuleDownAction(appController));
		actions.put(ActionType.moveModuleUp, new MoveModuleUpAction(appController));
		actions.put(ActionType.sortModules, new SortModulesAction(appController));
		actions.put(ActionType.removeModule, new RemoveModuleAction(appController));
		actions.put(ActionType.groupModules, new GroupModulesAction(appController));
		actions.put(ActionType.ungroupModules, new UnGroupModulesAction(appController));
		actions.put(ActionType.lockModule, new LockModuleAction(appController));
		actions.put(ActionType.unlockModule, new UnlockModuleAction(appController));
		actions.put(ActionType.showModuleInEditor, new ShowModuleInEditorAction(appController));
		actions.put(ActionType.hideModuleInEditor, new HideModuleInEditorAction(appController));
		actions.put(ActionType.editModulePosition, new EditModuleMainPropertiesAction(appController));
		actions.put(ActionType.addAllTextToSpeech, new AddAllTextToSpeechAction(appController));
		actions.put(ActionType.sortModulesTextToSpeech, new SortModulesTextToSpeechAction(appController));
		
		actions.put(ActionType.changeGridVisibility, new ChangeGridVisibilityAction(appController));
		actions.put(ActionType.gridSnapping, new SnappingModuleToGrid(appController));
		actions.put(ActionType.changeGridSize, new ChangeGridSizeAction(appController));
		
		actions.put(ActionType.changeRulersVisibility, new ChangeRulersVisibilityAction(appController));
		actions.put(ActionType.rulerSnapping, new SnappingModuleToRulerAction(appController));
		actions.put(ActionType.uiChangeRulerPosition, new ChangeRulerPositionAction(appController));
		actions.put(ActionType.updateRulersPositions, new UpdateRulersPositionsAction(appController));
		
		actions.put(ActionType.editFavouriteModules, new EditFavouriteModules(appController));
		
		//Semi-Responsive Actions
		actions.put(ActionType.addNewCssStyle, new AddNewCSSStyleAction(appController));
		actions.put(ActionType.deleteCssStyle, new DeleteCSSStyleAction(appController));
		actions.put(ActionType.setAsDefaultCSSStyle, new SetAsDefaultCSSStyleAction(appController));
		actions.put(ActionType.addSemiResponsiveLayout, new AddSemiResponsiveLayoutAction(appController));
		actions.put(ActionType.deleteSemiResponsiveLayout, new DeleteSemiResponsiveLayoutAction(appController));
		actions.put(ActionType.setAsDefaultSemiResponsiveLayout, new SetAsDefaultSemiResponsiveLayout(appController));
		actions.put(ActionType.refreshSemiResponsiveLayoutEditingWidgets, new RefreshSemiResponsiveLayoutEditingWidgetsAction(appController));
		actions.put(ActionType.changeCurrentContentSemiResponsiveLayout, new ChangeCurrentContentSemiResponsiveLayoutAction(appController));
		actions.put(ActionType.syncCurrentPageSemiResponsiveLayouts, new SyncCurrentPageSemiResponsiveLayoutsAction(appController));
		actions.put(ActionType.setSemiResponsiveLayoutStyle, new SetSemiResponsiveLayoutStyleAction(appController));
		actions.put(ActionType.refreshSemiResponsiveCSSStyle, new RefreshSemiResponsiveCSSStyle(appController));
		actions.put(ActionType.copyLastSeenLayoutConfiguration, new CopyLastSeenLayoutConfigurationAction(appController));
		actions.put(ActionType.markAsVisited, new MarkLayoutAsVisitedAction(appController));
		actions.put(ActionType.changePageSemiResponsiveLayout, new ChangePageSemiResponsiveLayoutID(appController));
		actions.put(ActionType.copyPageLayout, new CopyPageLayoutAction(appController));
		actions.put(ActionType.listAvailableLayouts, new ListAvailableLayoutsAction(appController));
		
		//Notifications
		actions.put(ActionType.showNotification, new ShowNotificationAction(appController));
	}
	
	public AbstractAction getAction(ActionType type){
		return actions.get(type);
	}
	
	public AddPageAction getAddPageAction(){
		return new AddPageAction(appController.getActionServices());
	}
	
	public InsertButtonAction getInsertButtonAction(){
		return new InsertButtonAction(appController);
	}
	
	
	public InsertAddonAction getInsertAddonAction(AddonEntry entry){
		return new InsertAddonAction(appController, entry);
	}
	
	public UISingleModuleSelectedAction getSingleModuleSelectedAction() {
		return (UISingleModuleSelectedAction) actions.get(ActionType.uiSingleModuleSelected);
	}
	
	public UIPageSelectedAction getPageSelectedAction() {
		return (UIPageSelectedAction) actions.get(ActionType.uiPageSelected);
	}
}
