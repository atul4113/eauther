package com.lorepo.iceditor.client.ui.widgets.content;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArrayInteger;
import com.google.gwt.dom.client.Style.Display;
import com.google.gwt.query.client.GQuery;
import com.google.gwt.query.client.GQuery.Offset;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.ui.AbsolutePanel;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.actions.*;
import com.lorepo.iceditor.client.actions.ActionFactory.ActionType;
import com.lorepo.iceditor.client.controller.CalculateMaxScore;
import com.lorepo.iceditor.client.controller.SelectionControllerUtils;
import com.lorepo.iceditor.client.module.api.IEditorServices;
import com.lorepo.iceditor.client.ui.page.EditorServicesImpl;
import com.lorepo.iceditor.client.ui.page.ModuleViewFactory;
import com.lorepo.iceditor.client.ui.page.ModulesDesignerModel;
import com.lorepo.iceditor.client.ui.page.ProxyWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.PropertiesWidget;
import com.lorepo.iceditor.client.ui.widgets.utils.MainPageUtils;
import com.lorepo.icf.uidesigner.DesignerModel;
import com.lorepo.icf.uidesigner.IDesignerModel;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.model.page.Page.PageScoreWeight;
import com.lorepo.icplayer.client.model.page.group.Group;
import com.lorepo.icplayer.client.module.api.ILayoutDefinition;
import com.lorepo.icplayer.client.module.api.ILayoutDefinition.Property;
import com.lorepo.icplayer.client.module.api.IModuleModel;
import com.lorepo.icplayer.client.module.api.player.IChapter;
import com.lorepo.icplayer.client.ui.Ruler;
import com.lorepo.icplayer.client.utils.DOMUtils;
import com.lorepo.icplayer.client.utils.MathJax;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static com.google.gwt.query.client.GQuery.$;

public class PresentationWidget extends Composite {

	private static ContentWidgetUiBinder uiBinder = GWT
			.create(ContentWidgetUiBinder.class);

	interface ContentWidgetUiBinder extends UiBinder<Widget, PresentationWidget> {
	}

	@UiField HTMLPanel panel;
	@UiField AbsolutePanel innerPanel;
	@UiField AbsolutePanel headerPanel;
	@UiField AbsolutePanel footerPanel;
	@UiField HTMLPanel headerLock;
	@UiField HTMLPanel footerLock;
	public PropertiesWidget propertiesWidget;

	private Content contentModel;
	private final List<IModuleModel> modulesOnPage = new ArrayList<IModuleModel>();
	private CalculateMaxScore calculateMaxScore = new CalculateMaxScore();
	private Map<String, AbsolutePanel> groupWidgets = new HashMap<String, AbsolutePanel>();

	private Page currentPage = null;
	private Page headerPage = null;
	private Page footerPage = null;

	private IModuleModel currentModule;
	private IDesignerModel<IModuleModel> model = new DesignerModel<IModuleModel>();
	private final ModulesDesignerModel modulesModel = new ModulesDesignerModel();
	private IEditorServices editorServices;
	private ModuleViewFactory widgetFactory;
	private final Map<IModuleModel, Integer> widgetsIndexes = new HashMap<IModuleModel, Integer>();
	private final Map<String,HashMap<String,ProxyWidget>> widgets = new HashMap<String, HashMap<String, ProxyWidget>>();

	//Actions
	private UIModuleSelectedAction onModuleSelectedAction;
	private UIModulePositionChangedAction onModulePositionChanged;
	private UIModuleDimensionsChangedAction onModuleDimensionsChanged;
	private AbstractAction onPageSelectedAction;
	private UIPageDimensionsChangedAction onPageDimensionsChanged;
	private AbstractAction onChangePageHeight;
	private SplitPageAction onSplitPage;
	private UIShowModuleDefaultPropertyEditorAction onShowModuleEditor;
	private ChangeRulerPositionAction onChangeRulerPosition;
	private UpdateRulersPositionsAction onUpdateRulersPositions;
	
	//SemiResponsiveActions
	private AbstractAction syncCurrentPageSemiResponsiveLayouts;
	private RefreshSemiResponsiveCSSStyle onRefreshSemiResponsiveCSSStyles;
	private MarkLayoutAsVisitedAction onMarkLayoutAsVisitedAction;
	private AbstractAction onCopyLastSeenConfiguration;
	private AbstractAction onChangePageSemiResponsiveLayoutID;
	private AbstractAction updateLayoutCopier;

	
	public IEditorServices getEditorServices(){
		return editorServices;
	}
	
	public PresentationWidget() {
		initWidget(uiBinder.createAndBindUi(this));

		panel.getElement().setId("presentation");
		headerLock.getElement().setId("headerLock");
		showHeader(false);
		footerLock.getElement().setId("footerLock");
		showFooter(false);

		updateElementsTexts();
		initJavaScriptAPI(this);
	}

	public AbsolutePanel getMainPagePanel() {
		return innerPanel;
	}

	public void setContent(Content content) {
		this.editorServices = new EditorServicesImpl(content);
		this.widgetFactory = new ModuleViewFactory(editorServices);
		this.contentModel = content;
	}

	public void setPage(Page newPage) {
		this.currentPage = newPage;
		this.currentModule = null;
		this.modulesModel.setModuleList(newPage.getModules());
		this.setModel(modulesModel);
		this.setPresentationToolsVisibility(true);
		this.refreshView();
	}

	private void setPresentationToolsVisibility(boolean isVisible) {
		String elementsDisplay = isVisible ? "block" : "none";

		panel.getElement().getStyle().setDisplay(isVisible ? Display.BLOCK : Display.NONE);

		$("#ruler_horizontal").css("display", elementsDisplay);
		$("#ruler_vertical").css("display", elementsDisplay);
		$("#presentationResizer-vertical").css("display", elementsDisplay);
		$("#presentationResizer-horizontal").css("display", elementsDisplay);
	}

	public Page getPage() {
		return currentPage;
	}

	public void setModel(IDesignerModel<IModuleModel> model){
		this.model = model;
	}
	
	public int getPageMaxScore(){
		return calculateMaxScore.getMaxScore();
	}

	public void refreshViewMain() {
		removeAllModules();
		DOMUtils.applyInlineStyle(innerPanel.getElement(), currentPage.getInlineStyle());
		innerPanel.setStyleName("ic_page ic_main");
		
		String styleClass = currentPage.getStyleClass();
		if(styleClass != null && !styleClass.isEmpty()){
			innerPanel.addStyleName(styleClass);
		}

		resizePanel();
		calculateMaxScore.clear();
		for(Group group : this.currentPage.getGroupedModules()) {
			if(group.isDiv()) {
				AddGroupToPanel(innerPanel, group);
			}
		}
		List<String> visibleModulesIds = addModulesToPanel();

		if (currentPage.getPageScoreWeight() == PageScoreWeight.maxPageScore) {
			currentPage.setPageWeight(calculateMaxScore.getMaxScore());
		}
		refreshMathJax(innerPanel.getElement());
		executeOnPageChangedFunction();
		MainPageUtils.updatePageResizers();
		updateSelectorPositionAndDimensionFromRenderedView(visibleModulesIds);
	}

	private List<String> addModulesToPanel() {
		int widgetIndex = 0;
		List<String> visibleModulesIds = new ArrayList<String>();
		for (int i = 0; i < model.getItemsCount(); i++) {
			IModuleModel module = model.getItem(i);
			widgetsIndexes.put(module, widgetIndex);
			ProxyWidget proxy = widgetFactory.getWidget(module);
			Group group = getGroupIntoDiv(module);
			if(group == null) {
				addModuleToPanel(currentPage.getId(), innerPanel, proxy);
				createModuleSelector(innerPanel, proxy, module, visibleModulesIds);
			}else {
				AbsolutePanel groupWidget = groupWidgets.get(group.getId());
				addModuleToPanel(currentPage.getId(), groupWidget, proxy);
				createModuleSelector(groupWidget, proxy, module, visibleModulesIds);
			}
			calculateMaxScore.addMaxScore(proxy.getMaxScore());

			widgetIndex += 2;
			if(module.isLocked()){
				addDisableClass(module.getId());
			}
		}
		return visibleModulesIds;
	}


	private Group getGroupIntoDiv(IModuleModel module) {
		Group group = null;
		if(module.hasGroup()) {
			Group g = SelectionControllerUtils.getGroupWithModule(module, currentPage.getGroupedModules());
			if(g!=null && g.isDiv()) {
				group = g;
			}
		}
		return group;
	}

	private void createModuleSelector(AbsolutePanel panel, ProxyWidget proxy, IModuleModel module, List<String> visibleModulesIds) {
		if (module.isModuleInEditorVisible()) {
			ModuleSelectorWidget selector = createAndAttachModuleSelector(panel, proxy);
			updateModulePositionAndDimensionsFromLayout(currentPage.getId(), panel, proxy, selector);
			visibleModulesIds.add(module.getId());
		}
	}

	private static native void addDisableClass(String id) /*-{
		if(id.indexOf("'") > -1) {
			var module = $doc.getElementById(id);
			$wnd.$(module).next().addClass("ui-state-disabled");
		} else {
			$wnd.$("[id='" + id + "']").next().addClass("ui-state-disabled");
		}
	}-*/;
	
	public void refreshView() {
		this.syncCurrentPageSemiResponsiveLayouts.execute();
		this.onChangePageSemiResponsiveLayoutID.execute();
		this.onCopyLastSeenConfiguration.execute();
		this.updateLayoutCopier.execute();
		
		this.onMarkLayoutAsVisitedAction.setSemiResponsiveLayoutID(this.contentModel.getActualSemiResponsiveLayoutID());
		this.onMarkLayoutAsVisitedAction.execute();
		
		this.onRefreshSemiResponsiveCSSStyles.setLayoutID(this.contentModel.getActualSemiResponsiveLayoutID()).execute();

		refreshViewMain();
		this.refreshHeaderFooter();
		adjustView(true);
		this.onPageEnter();
	}
	
	public native void onPageEnter() /*-{
		$wnd.iceEditorApplication.PageEnterSizesTimeout.run();
	}-*/;
	
	public void onRefreshPageDimensionsOnEnter(String width, String height) {
		propertiesWidget.setNewPageDimensions(height, width);
		currentPage.setHeight(Integer.valueOf(height));
		currentPage.setWidth(Integer.valueOf(width));
	}
	
	public static native void adjustSelectionBox(boolean findRelatedModules) /*-{
		$wnd.adjustSelectionBox(findRelatedModules);
	}-*/;

	public native void adjustView(boolean findRelatedModules) /*-{
		$wnd.adjustSelectionBox(findRelatedModules);
		if(typeof $wnd.iceAdjustGridView == 'function') {
			$wnd.iceAdjustGridView();
		}
	}-*/;

	private void resizePanel() {
		int height = currentPage.getHeight();

		if (height != 0) {
			innerPanel.setHeight(height + "px");
			panel.setHeight(height + "px");
		}

		int width = currentPage.getWidth();
		if (width != 0) {
			innerPanel.setWidth(width + "px");
			panel.setWidth(width + "px");
		}
	}

	public static native void cleanModulesSelectorsHandlers() /*-{
		$wnd.cleanModuleSelectorsHandlers();
	}-*/;


	public void removeAllModules() {
		cleanModulesSelectorsHandlers();
		widgetsIndexes.clear();
		groupWidgets.clear();
		widgets.put(currentPage.getId(), new HashMap<String, ProxyWidget>());
		innerPanel.clear();

		currentModule = null;
	}

	static class OuterDimensions extends JavaScriptObject {
		protected OuterDimensions() {}

		public final native int getWidth() /*-{ return this.width; }-*/;
		public final native int getHeight() /*-{ return this.height; }-*/;
	}

	private static native OuterDimensions getOuterDimensions(Element module) /*-{
		var $module = module,
			operationsUtils = $wnd.DOMOperationsUtils,
			calculatedOuterDistances = operationsUtils.calculateOuterDistances(operationsUtils.getOuterDimensions($module)),
			width = calculatedOuterDistances.vertical,
			height = calculatedOuterDistances.horizontal;

		return {width: width, height: height};
	}-*/;

	private boolean shouldLockModuleSelector(IModuleModel module) {
		return module.isLocked() || SelectionControllerUtils.isModuleInAnyGroup(module, currentPage);
	}

	public void addModuleToPanel(String pageID, AbsolutePanel panel, ProxyWidget proxy) {
		IModuleModel module = proxy.getModel();

		if (!module.isModuleInEditorVisible()) {
			proxy.getInnerElement().addClassName("ice_module_hide_module_in_editor");
		}

		proxy.setPixelSize(proxy.getWidth(), proxy.getHeight());
		panel.add(proxy, proxy.getLeft(), proxy.getTop());

		widgets.get(pageID).put(module.getId(), proxy);
	}

	public void AddGroupToPanel( AbsolutePanel panel, Group group) {
		AbsolutePanel groupWidget = new AbsolutePanel();
		groupWidget.getElement().setClassName("modules_group");
		if(group.isModificatedHeight()) {
			groupWidget.addStyleName("modificated_height");
		}
		if(group.isModificatedWidth()) {
			groupWidget.addStyleName("modificated_width");
		}
		String styleClass = group.getStyleClass();
		String inlineStyle = group.getInlineStyle();
		if(styleClass != null && !styleClass.isEmpty()){
			groupWidget.addStyleName(styleClass);
		}
		if(inlineStyle != null) {
			DOMUtils.applyInlineStyle(groupWidget.getElement(), inlineStyle);
		}
		
		groupWidget.setVisible(group.isModuleInEditorVisible());
		
		groupWidget.getElement().setId(group.getId());
		groupWidget.setPixelSize(group.getWidth()+2, group.getHeight()+2);
		groupWidgets.put(group.getId(), groupWidget);
		panel.add(groupWidget,group.getLeft(),group.getTop());
	}

	public ModuleSelectorWidget createAndAttachModuleSelector(AbsolutePanel panel, ProxyWidget proxy) {
		IModuleModel module = proxy.getModel();
		GQuery $module = $(proxy.getInnerElement());

		int moduleWidth = $module.width();
		int moduleHeight = $module.height();
		int moduleLeft = $module.isVisible() ? $module.position().left : proxy.getModel().getLeft();
		int moduleTop = $module.isVisible() ? $module.position().top : proxy.getModel().getTop();

		OuterDimensions outerDimensions = getOuterDimensions(proxy.getElement());
		int outerWidth = outerDimensions.getWidth() + moduleWidth;
		int outerHeight = outerDimensions.getHeight() + moduleHeight;

		ModuleSelectorWidget selectorWidget = new ModuleSelectorWidget();
		selectorWidget.setPixelSize(outerWidth, outerHeight);

		if (shouldLockModuleSelector(module)) {
			selectorWidget.getElement().addClassName("moduleSelector-locked");
		}

		panel.add(selectorWidget, moduleLeft, moduleTop);

		return selectorWidget;
	}

	private static native void initJavaScriptAPI(PresentationWidget x) /*-{
		$wnd.iceModuleSelected = function(moduleID, clearSelection) {
			x.@com.lorepo.iceditor.client.ui.widgets.content.PresentationWidget::onModuleSelected(Ljava/lang/String;Z)(moduleID, clearSelection);
		};

		$wnd.iceModulePositionChanged = function(moduleID, left, top, right, bottom, submit, addToHistory) {
			x.@com.lorepo.iceditor.client.ui.widgets.content.PresentationWidget::onModulePositionChanged(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ZZ)(moduleID, left, top, right, bottom, submit, addToHistory);
		}

		$wnd.iceModuleDimentionsChanged = function(height, width, left, top, right, bottom, submit) {
			x.@com.lorepo.iceditor.client.ui.widgets.content.PresentationWidget::onModuleDimensionsChanged(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Z)(height, width, left, top, right, bottom, submit);
		}

		$wnd.icePageSelected = function() {
			x.@com.lorepo.iceditor.client.ui.widgets.content.PresentationWidget::executeOnPageSelectedAction()();
		};

		$wnd.icePageDimensionsChanged = function(width, height, submit) {
			x.@com.lorepo.iceditor.client.ui.widgets.content.PresentationWidget::onPageDimensionsChanged(Ljava/lang/String;Ljava/lang/String;Z)(height, width, submit);
		};

		$wnd.iceChangePageHeight = function(clickPosition) {
			x.@com.lorepo.iceditor.client.ui.widgets.content.PresentationWidget::onChangePageHeight(I)(clickPosition);
		};

		$wnd.iceSplitPage = function(clickPosition) {
			x.@com.lorepo.iceditor.client.ui.widgets.content.PresentationWidget::onSplitPage(I)(clickPosition);
		};

		$wnd.iceShowModuleEditor = function(moduleID) {
			x.@com.lorepo.iceditor.client.ui.widgets.content.PresentationWidget::onShowModuleEditor(Ljava/lang/String;)(moduleID);
		};

		$wnd.iceShowRulerPositionModal = function(position, value) {
			x.@com.lorepo.iceditor.client.ui.widgets.content.PresentationWidget::onShowModalRulerPosition(Ljava/lang/String;Ljava/lang/String;)(position, value);
		};

		$wnd.iceUpdateRulersPositions = function(verticals, horizontals) {
			x.@com.lorepo.iceditor.client.ui.widgets.content.PresentationWidget::onUpdateRulersPositions(Lcom/google/gwt/core/client/JsArrayInteger;Lcom/google/gwt/core/client/JsArrayInteger;)(verticals, horizontals);
		};
		
		$wnd.iceRefreshView = function(verticals, horizontals) {
			x.@com.lorepo.iceditor.client.ui.widgets.content.PresentationWidget::refreshView()();
		};
		
		$wnd.iceRefreshPageDimensionsOnEnter = function (width, height) {
			x.@com.lorepo.iceditor.client.ui.widgets.content.PresentationWidget::onRefreshPageDimensionsOnEnter(Ljava/lang/String;Ljava/lang/String;)(width, height);
		}
 	}-*/;

	private static native void executeOnPageChangedFunction() /*-{
		if(typeof $wnd.iceOnPageChanged == 'function') {
		  $wnd.iceOnPageChanged();
		}
	}-*/;

	private static native void executeOnModuleChangedFunction(String moduleID, boolean isSelected) /*-{
		if(typeof $wnd.iceOnModuleChanged == 'function') {
		  $wnd.iceOnModuleChanged(moduleID, isSelected);
		}
	}-*/;

	private static native void executeOnModuleSelectedFunction(String moduleID) /*-{
		if(typeof $wnd.iceOnModuleSelected == 'function') {
		  $wnd.iceOnModuleSelected(moduleID);
		}
	}-*/;

	private static native void setRulers(boolean isVisible, int[] verticals, int[] horizontals) /*-{
		if(typeof $wnd.iceInitSavedRulers == 'function') {
			$wnd.iceInitSavedRulers(isVisible, verticals, horizontals);
		}
	}-*/;

	public void setRulers(Content content, HashMap<String, List<Ruler>> rulers) {
		boolean isVisible = Boolean.parseBoolean(content.getMetadataValue("useRulers"));
		List<Ruler> verticalRulers;
		List<Ruler> horizontalRulers;
		int[] verticals = {0};
		int[] horizontals = {0};

		if (rulers != null) {
			verticalRulers = rulers.get("verticals");
			horizontalRulers = rulers.get("horizontals");

			for (int i = 0; i < verticalRulers.size(); i++) {
				verticals[i] = verticalRulers.get(i).getPosition();
			}

			for (int i = 0; i < horizontalRulers.size(); i++) {
				horizontals[i] = horizontalRulers.get(i).getPosition();
			}
		}

		setRulers(isVisible, verticals, horizontals);
	}

	public void setActionFactory(ActionFactory actionFactory) {
		this.onModuleSelectedAction = (UIModuleSelectedAction) actionFactory.getAction(ActionType.uiModuleSelected);
		this.onModulePositionChanged = (UIModulePositionChangedAction) actionFactory.getAction(ActionType.uiModulePositionChanged);
		this.onModuleDimensionsChanged = (UIModuleDimensionsChangedAction) actionFactory.getAction(ActionType.uiModuleDimensionsChanged);
		this.onPageSelectedAction = actionFactory.getAction(ActionType.uiPageSelected);
		this.onPageDimensionsChanged = (UIPageDimensionsChangedAction) actionFactory.getAction(ActionType.uiPageDimensionsChanged);
		this.onChangePageHeight = actionFactory.getAction(ActionType.changePageHeight);
		this.onSplitPage = (SplitPageAction) actionFactory.getAction(ActionType.splitPage);
		this.onShowModuleEditor = (UIShowModuleDefaultPropertyEditorAction) actionFactory.getAction(ActionType.uiShowModuleEditor);
		this.onChangeRulerPosition = (ChangeRulerPositionAction) actionFactory.getAction(ActionType.uiChangeRulerPosition);
		this.onUpdateRulersPositions = (UpdateRulersPositionsAction) actionFactory.getAction(ActionType.updateRulersPositions);
		
		this.syncCurrentPageSemiResponsiveLayouts = actionFactory.getAction(ActionType.syncCurrentPageSemiResponsiveLayouts);
		this.onRefreshSemiResponsiveCSSStyles = (RefreshSemiResponsiveCSSStyle) actionFactory.getAction(ActionType.refreshSemiResponsiveCSSStyle);
		this.onMarkLayoutAsVisitedAction = (MarkLayoutAsVisitedAction) actionFactory.getAction(ActionType.markAsVisited);
		this.onCopyLastSeenConfiguration = actionFactory.getAction(ActionType.copyLastSeenLayoutConfiguration);
		this.onChangePageSemiResponsiveLayoutID = actionFactory.getAction(ActionType.changePageSemiResponsiveLayout);
		this.updateLayoutCopier = actionFactory.getAction(ActionType.listAvailableLayouts);
	}

	private void onUpdateRulersPositions(JsArrayInteger verticals, JsArrayInteger horizontals) {
		List<Integer> verticalsPositions = new ArrayList<Integer>();
		List<Integer> horizontalsPositions = new ArrayList<Integer>();

		for (int i = 0; i < verticals.length(); i++) {
			verticalsPositions.add(verticals.get(i));
		}

		for (int i = 0; i < horizontals.length(); i++) {
			horizontalsPositions.add(horizontals.get(i));
		}

		onUpdateRulersPositions.execute(verticalsPositions, horizontalsPositions);
    }

	private void onShowModalRulerPosition(String position, String value) {
		onChangeRulerPosition.execute(position, value);
	}

	private void onChangePageHeight(int clickPosition) {
		ChangePageHeightAction outstretchAction = (ChangePageHeightAction) onChangePageHeight;
		outstretchAction.setPosition(clickPosition);
		onChangePageHeight.execute();
	}

	private void onSplitPage(int position) {
		onSplitPage.execute(position);
	}

	private void onModuleSelected(String moduleID, boolean clearSelection) {
		IModuleModel selectedModule = currentPage.getModules().getModuleById(moduleID);

		if (selectedModule == null || isModuleSelected(selectedModule)) {
			return;
		}

		currentModule = selectedModule;

		onModuleSelectedAction.execute(selectedModule, clearSelection);
	}

	private void onShowModuleEditor(String moduleID) {
		IModuleModel module = currentPage.getModules().getModuleById(moduleID);

		if (module == null) {
			return;
		}

		onShowModuleEditor.execute(module);
	}

	public void setModule(IModuleModel module) {
		if (currentModule != null && currentModule.getId().equals(module.getId())) {
			return;
		}

		executeOnModuleSelectedFunction(module.getId());
	}

	public void onPageSelected() {
		currentModule = null;
	}

	private void executeOnPageSelectedAction() {
		if (currentModule == null) {
			return;
		}

		onPageSelectedAction.execute();
	}

	public void setPropertiesWidget(PropertiesWidget properties) {
		this.propertiesWidget = properties;
	}

	public HashMap<String, Integer> calculatePosition(String pageID, IModuleModel module) {
		int left, right, bottom, top;

		right = 0;
		bottom = 0;

		HashMap<String, Integer> positions = new HashMap<String, Integer>();

		ILayoutDefinition layout = module.getLayout();

		// Module can have left, right or both relatives selected, never none of them.
		if (layout.hasLeft() && layout.hasRight()) {
			left = calculateLeftPosition(pageID, layout.getLeftRelativeTo(), layout.getLeftRelativeToProperty(), module.getLeft());
			right = calculateRightPosition(pageID, layout.getRightRelativeTo(), layout.getRightRelativeToProperty(), -module.getRight());
		} else if (layout.hasLeft()) {
			left = calculateLeftPosition(pageID, layout.getLeftRelativeTo(),  layout.getLeftRelativeToProperty(), module.getLeft());
		} else {
			right = calculateRightPosition(pageID, layout.getRightRelativeTo(), layout.getRightRelativeToProperty(), -module.getRight());
			left = right-module.getWidth();
		}

		// Module can have top, bottom or both relatives selected, never none of them.
		if (layout.hasTop() && layout.hasBottom()) {
			top = calculateTopPosition(pageID, layout.getTopRelativeTo(), layout.getTopRelativeToProperty(), module.getTop());
			bottom = calculateBottomPosition(pageID, layout.getBottomRelativeTo(), layout.getBottomRelativeToProperty(), -module.getBottom());
		} else if (layout.hasTop()) {
			top = calculateTopPosition(pageID, layout.getTopRelativeTo(), layout.getTopRelativeToProperty(), module.getTop());
		} else {
			bottom = calculateBottomPosition(pageID, layout.getBottomRelativeTo(), layout.getBottomRelativeToProperty(), -module.getBottom());
			top = bottom-module.getHeight();
		}

		positions.put("left", left);
		positions.put("right", right);
		positions.put("top", top);
		positions.put("bottom", bottom);

		return positions;
	}

	private int getPageHeight(String pageID) {
		Content model = this.getEditorServices().getContent();
		
		Page page = (Page)model.getPageById(pageID);
		if(page == null){
			page = (Page)model.getCommonPageById(pageID);
		}
		
		if(page != null) {
			return page.getHeight();
		}
		
		return 0;
	}
	
	private int calculateTopPosition(String pageID, String relatedWidgetName, Property sideProperty, int modulePos) {
		ProxyWidget widget = widgets.get(pageID).get(relatedWidgetName);
		GQuery $module = null;

		if (widget != null) {
			$module = $(widget.getInnerElement());
		}

		int returnPos = modulePos;
		int pageHeight = getPageHeight(pageID);

		if (sideProperty == Property.top) {
			if (widget != null) {
				returnPos = $module.position().top + modulePos;
			} else{
				returnPos = modulePos;
			}
		} else if (sideProperty == Property.bottom) {
			if (widget != null) {
				returnPos = $module.position().top + $module.outerHeight() + modulePos;
			} else {
				returnPos = pageHeight + modulePos;
			}
		}

		return returnPos;
	}
	
	private int calculateBottomPosition(String pageID, String relatedWidgetName, Property sideProperty, int modulePos) {
		ProxyWidget widget = widgets.get(pageID).get(relatedWidgetName);
		GQuery $module = null;

		if (widget != null) {
			$module = $(widget.getInnerElement());
		}

		int returnPos = modulePos;
		int pageHeight = getPageHeight(pageID);

		if (sideProperty == Property.top) {
			if (widget != null) {
				returnPos =  $module.position().top + modulePos;
			} else{
				returnPos = modulePos;
			}
		} else if (sideProperty == Property.bottom) {
			if (widget != null) {
				returnPos = $module.position().top + $module.outerHeight() + modulePos;
			} else {
				returnPos = pageHeight + modulePos;
			}
		}

		return returnPos;
	}

	private int calculateLeftPosition(String pageID, String relatedWidgetName, Property sideProperty, int modulePos) {
		ProxyWidget widget = widgets.get(pageID).get(relatedWidgetName);
		GQuery $module = null;

		if (widget != null) {
			$module = $(widget.getInnerElement());
		}

		int returnPos = modulePos;
		int pageWidth = getElement().getPropertyInt("clientWidth");

		if (sideProperty == Property.left) {
			if (widget != null) {
				returnPos = $module.position().left + modulePos;
			} else {
				returnPos = modulePos;
			}
		} else if (sideProperty == Property.right) {
			if (widget != null) {
				returnPos = $module.position().left + $module.outerWidth() + modulePos;
			} else {
				returnPos = pageWidth + modulePos;
			}
		}

		return returnPos;
	}

	private int calculateRightPosition(String pageID, String relatedWidgetName, Property sideProperty, int modulePos) {
		ProxyWidget widget = widgets.get(pageID).get(relatedWidgetName);
		GQuery $module = null;

		if (widget != null) {
			$module = $(widget.getInnerElement());
		}

		int returnPos = modulePos;
		int pageWidth = getElement().getPropertyInt("clientWidth");

		if (sideProperty == Property.left) {
			if(widget != null) {
				returnPos = $module.position().left + modulePos;
			} else {
				returnPos = modulePos;
			}
		} else if(sideProperty == Property.right) {
			if(widget != null){
				returnPos = $module.position().left + $module.outerWidth() + modulePos;
			} else{
				returnPos = pageWidth + modulePos;
			}
		}

		return returnPos;
	}

	private HashMap<String, Integer> calculateDimensions(String pageID, IModuleModel module) {
		int width, height;

		HashMap<String, Integer> dimensions = new HashMap<String, Integer>();

		ILayoutDefinition layout = module.getLayout();

		width = calculateWidth(pageID, module, layout);
		height = calculateHeight(pageID, module, layout);

		dimensions.put("width", width);
		dimensions.put("height", height);

		return dimensions;
	}

	private int calculateWidth(String pageID, IModuleModel module, ILayoutDefinition layout) {
		int width;

		if (layout.hasLeft() && layout.hasRight()) {
			int left = calculateLeftPosition(pageID, layout.getLeftRelativeTo(), layout.getLeftRelativeToProperty(), module.getLeft());
			int right = calculateRightPosition(pageID, layout.getRightRelativeTo(), layout.getRightRelativeToProperty(), -module.getRight());

			width = right-left;
		} else {
			width = module.getWidth();
		}

		return width;
	}

	private int calculateHeight(String pageID, IModuleModel module, ILayoutDefinition layout) {
		int height;

		if (layout.hasTop() && layout.hasBottom()) {
			int top = calculateTopPosition(pageID, layout.getTopRelativeTo(), layout.getTopRelativeToProperty(), module.getTop());
			int bottom = calculateBottomPosition(pageID, layout.getBottomRelativeTo(), layout.getBottomRelativeToProperty(), -module.getBottom());
			height = bottom-top;
		} else {
			height = module.getHeight();
		}

		return height;
	}

	private void setPosition(AbsolutePanel panel, ProxyWidget proxy, HashMap<String, Integer> position, ModuleSelectorWidget selectorWidget) {
		panel.setWidgetPosition(proxy, position.get("left"), position.get("top"));

		if (selectorWidget != null) {
			panel.setWidgetPosition(selectorWidget, position.get("left"), position.get("top"));
		}
	}

	private void setSize(ProxyWidget proxy, HashMap<String, Integer> dimensions, ModuleSelectorWidget selectorWidget) {
		OuterDimensions outerDimensions = getOuterDimensions(proxy.getElement());

		proxy.setPixelSize(dimensions.get("width"), dimensions.get("height"));

		if (selectorWidget != null) {
			selectorWidget.setPixelSize(dimensions.get("width") + outerDimensions.getWidth(), dimensions.get("height") + outerDimensions.getHeight());
		}
	}

	public void updateModulePositionAndDimensionsFromLayout(String pageID,  AbsolutePanel panel, ProxyWidget proxy, ModuleSelectorWidget selector) {
		IModuleModel module = proxy.getModel();
		HashMap<String, Integer> position = calculatePosition(pageID, module);
		HashMap<String, Integer> dimensions = calculateDimensions(pageID, module);
		
		setPosition(panel, proxy, position, selector);
		setSize(proxy, dimensions, selector);

		executeOnModuleChangedFunction(module.getId(), isModuleSelected(module));
	}
	
	// After refresh module with set important its selector is in another position. We must restore it.
	private void updateSelectorPosition(String id) {
		GQuery $renderedElements = $("div#" + id);
		for (int i = 0; i<$renderedElements.length(); i++) {
			GQuery $renderedElement = $($renderedElements.get(i));
			GQuery $renderedSelector = $renderedElement.next();
			
			if ($renderedSelector.hasClass("moduleSelector")) {
				if ($renderedElement.isVisible()) {
					Offset position = $renderedElement.position();
					
					$renderedSelector.css("top", position.top + "px");
					$renderedSelector.css("left", position.left + "px");
					$renderedSelector.css("width", $renderedElement.outerWidth() + "px");
					$renderedSelector.css("height", $renderedElement.outerHeight() + "px");	
				}
			}
		}
	}
	
	private void updateSelectorPositionAndDimensionFromRenderedView(List<String> ids) {
		for (String id : ids) {
			updateSelectorPosition(id);
		}
	}

	public void refreshModule(IModuleModel module) {
		int beforeIndex = widgetsIndexes.get(module);

		innerPanel.remove(beforeIndex);

		ProxyWidget proxy = widgetFactory.getWidget(module);

		int proxyWidth = proxy.getWidth();
		int proxyHeight = proxy.getHeight();

		proxy.setPixelSize(proxyWidth, proxyHeight);

		if (!module.isModuleInEditorVisible()) {
			proxy.addStyleName("ice_module_hide_module_in_editor");
		}

		innerPanel.insert(proxy, proxy.getLeft(), proxy.getTop(), beforeIndex);

		innerPanel.remove(beforeIndex + 1);

		if (module.isModuleInEditorVisible()) {
			ModuleSelectorWidget selectorWidget = new ModuleSelectorWidget();
			OuterDimensions outerDimensions = getOuterDimensions(proxy.getElement());

			selectorWidget.setPixelSize(proxyWidth + outerDimensions.getWidth(), proxyHeight + outerDimensions.getHeight());

			if (shouldLockModuleSelector(module)) {
				selectorWidget.getElement().addClassName("moduleSelector-locked");
			}

			innerPanel.insert(selectorWidget, proxy.getLeft(), proxy.getTop(), beforeIndex + 1);
		}

		updateSelectorPosition(module.getId());
		
		executeOnModuleChangedFunction(module.getId(), isModuleSelected(module));
		adjustView(true);
	}

	private void onModulePositionChanged(String moduleID, String left, String top, String right, String bottom, boolean submit, boolean addToHistory) {
		onModulePositionChanged.execute(moduleID, left, top, right, bottom, submit, addToHistory);
	}

	private void onModuleDimensionsChanged(String height, String width, String left, String top, String right, String bottom, boolean submit) {
		onModuleDimensionsChanged.execute(height, width, left, top, right, bottom, submit);
	}

	private void onPageDimensionsChanged(String width, String height, boolean submit) {
		onPageDimensionsChanged.execute(width, height, submit);
	}

	private boolean isModuleSelected(IModuleModel module) {
		if (currentModule == null) {
			return false;
		}

		return currentModule.getId().equals(module.getId());
	}

	public int getPageScrollTopPosition() {
		return readPageScrollTopPosition();
	}

	private static native int readPageScrollTopPosition() /*-{
		if (typeof $wnd.iceGetPageScrollTopPosition == 'function') {
			return $wnd.iceGetPageScrollTopPosition();
		}

		return 0;
	}-*/;

	public void showHeader(boolean show) {
		headerPanel.getElement().getStyle().setDisplay(show ? Display.BLOCK : Display.NONE);
		headerLock.getElement().getStyle().setDisplay(show ? Display.BLOCK : Display.NONE);

		if (!show) {
			headerPanel.clear();
		}
	}

	public void setHeader(Page header) {
		headerPage = header;

		applyCommonsStyles(headerPage, headerPanel, "ic_header");
		loadCommonModules(headerPage, headerPanel);
		executeOnPageChangedFunction();
		adjustLocks();
	}

	public void showFooter(boolean show) {
		footerPanel.getElement().getStyle().setDisplay(show ? Display.BLOCK : Display.NONE);
		footerLock.getElement().getStyle().setDisplay(show ? Display.BLOCK : Display.NONE);

		if (!show) {
			footerPanel.clear();
		}
	}

	public void setFooter(Page footer) {
		footerPage = footer;

		applyCommonsStyles(footerPage, footerPanel, "ic_footer");
		loadCommonModules(footerPage, footerPanel);
		executeOnPageChangedFunction();
		adjustLocks();
	}

	private static native int adjustLocks() /*-{
		if (typeof $wnd.iceUpdateCommonsLocks == 'function') {
			$wnd.iceUpdateCommonsLocks();
		}
	}-*/;

	private void applyCommonsStyles(Page page, AbsolutePanel panel, String mainStyle) {
		String styles = "position:relative;overflow:hidden;";
		if (page.getInlineStyle() != null) {
			styles += page.getInlineStyle();

		}
		DOMUtils.applyInlineStyle(panel.getElement(), styles);
		panel.setStyleName(mainStyle + " ic_page");
		if (!page.getStyleClass().isEmpty()) {
			panel.addStyleName(page.getStyleClass());
		}

		if (page.getWidth() > 0) {
			panel.setWidth(page.getWidth() + "px");
		}
		if (page.getHeight() > 0) {
			panel.setHeight(page.getHeight() + "px");
		}
	}

	private void loadCommonModules(Page page, AbsolutePanel panel) {
		panel.clear();
		widgets.put(page.getId(), new HashMap<String, ProxyWidget>());

		String semiResponsiveLayoutID = this.contentModel.getActualSemiResponsiveLayoutID();
		for (IModuleModel module : page.getModules()) {
			module.setSemiResponsiveLayoutID(semiResponsiveLayoutID);
			modulesOnPage.add(module);

			ProxyWidget proxy = widgetFactory.getWidget(module);
			addModuleToPanel(page.getId(), panel, proxy);

			if (module.isModuleInEditorVisible()) {
				updateModulePositionAndDimensionsFromLayout(page.getId(), panel, proxy, null);
			}
		}
	}

	public List<IModuleModel> getModules() {
		return modulesOnPage;
	}

	public IModuleModel findModuleById(String moduleID) {
		return currentPage.getModules().getModuleById(moduleID);
	}

	private void refreshMathJax(Element element) {
		MathJax.refreshMathJax(element);
	}

	public void setChapter(IChapter chapter) {
		innerPanel.clear();
		innerPanel.setStyleName("ic_page ic_main");

		setPresentationToolsVisibility(false);
	}

	public void updateElementsTexts() {
		GQuery options = $(panel.getElement()).find("#ruler_vertical_options");

		options.find("a").get(0).setInnerText(DictionaryWrapper.get("outstretch_height"));
		options.find("a").get(1).setInnerText(DictionaryWrapper.get("split_page"));
	}

	public void groupModules(Group group, boolean isPageToSave) {
		modulesModel.setModified(isPageToSave);
		modulesModel.createGroup(group);
	}

	public void removeGroupModules(Group group) {
		modulesModel.removeGroup(group);
		modulesModel.setModified(true);
	}

	public void unGroupSelection(IModuleModel item) {
		modulesModel.setModified(true);
		modulesModel.removeGroupWithItem(item);
	}

	public void refreshHeaderFooter() {
		String actualLayoutID = this.contentModel.getActualSemiResponsiveLayoutID();
		this.refreshFooter(actualLayoutID);
		this.refreshHeader(actualLayoutID);
	}
	
	private void refreshHeader(String actualLayoutID) {
		Content content = this.editorServices.getContent();
	
		if (content.isCommonPage(this.currentPage)) {
			this.showHeader(false);
		} else { 
			Page header = null;
			
			if (this.currentPage.hasHeader()) {
				header = content.getHeader(this.currentPage);
			}
			
			if (header != null) {
				header.setSemiResponsiveLayoutID(actualLayoutID);
				this.setHeader(header);
				this.showHeader(true);
			} else {
				this.showHeader(false);
			}
		}
	}
	
	private void refreshFooter(String actualLayoutID) {
		Content content = this.editorServices.getContent();
		
		if (content.isCommonPage(this.currentPage)) {
			this.showFooter(false);
		} else {
			Page footer = null;
			
			if (this.currentPage.hasFooter()) {
				footer = content.getFooter(this.currentPage);
			}
		
			if (footer != null) {
				footer.setSemiResponsiveLayoutID(actualLayoutID);
				this.setFooter(footer);
				this.showFooter(true);
			} else {
				this.showFooter(false);
			}
		}
	}
			
}
