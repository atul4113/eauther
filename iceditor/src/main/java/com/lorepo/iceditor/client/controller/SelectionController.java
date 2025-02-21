package com.lorepo.iceditor.client.controller;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.user.client.DOM;
import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.AbsolutePanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.SimplePanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.actions.AbstractAction;
import com.lorepo.iceditor.client.actions.ActionFactory;
import com.lorepo.iceditor.client.actions.ActionFactory.ActionType;
import com.lorepo.iceditor.client.actions.UIModuleSelectedAction;
import com.lorepo.iceditor.client.actions.api.ISelectionController;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.widgets.content.PresentationWidget;
import com.lorepo.iceditor.client.ui.widgets.modules.ModulesWidget;
import com.lorepo.iceditor.client.ui.widgets.utils.MainPageUtils;
import com.lorepo.iceditor.client.ui.widgets.utils.PresentationUtils;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.model.page.group.Group;
import com.lorepo.icplayer.client.module.api.IModuleModel;
import com.lorepo.icplayer.client.module.api.player.IContentNode;

public class SelectionController implements ISelectionController{
	private final AppController appController;

	private SimplePanel contentWrapper;
	private Element contentElement;

	private AbsolutePanel presentationPanel;

	private AbstractAction onPageSelectedAction;
	private UIModuleSelectedAction onModuleSelectedAction;

	private int	mouseLastX;
	private int	mouseLastY;
	private Widget dynamicModuleSelector = null;
	private Widget selectionBox = null;

	private IContentNode selectedNode;
	private List<IModuleModel> selectedModules = new ArrayList<IModuleModel>();
	private final HashMap<String, Integer> selectionPosition = new HashMap<String, Integer>();

	private boolean isMouseMoving = false;
	private final HashMap<String,List<Group>> groupedModules = new HashMap<String, List<Group>>();

	private IModuleModel selectedModule = null;
	private List<Group> selectedGroups = new ArrayList<Group>();
	private boolean captureEvents = true;
	private boolean isGroupSelection = false;
	private String currentModuleID = "";

	public SelectionController(AppController appController) {
		this.appController = appController;
	}

	public void initJavaScriptAPI() {
		initJavaScriptAPI(this);
	}

	private static native void initJavaScriptAPI(SelectionController x) /*-{
		$wnd.shouldSelectorControllerCaptureEvents = function(captureEvents) {
			x.@com.lorepo.iceditor.client.controller.SelectionController::shouldCaptureEvents(Z)(captureEvents);
		}

		$wnd.adjustSelectionBox = function(findRelatedModules) {
			x.@com.lorepo.iceditor.client.controller.SelectionController::adjustSelectionBox(Z)(findRelatedModules);
		}
	}-*/;

	private void shouldCaptureEvents(boolean captureEvents) {
		this.captureEvents = captureEvents;
	}

	@Override
	public void selectModule(IModuleModel module) {
		selectedModules.add(module);

		adjustSelectionBox(true);
	}

	@Override
	/**
	 * There are situations when regardless of module association with group
	 * we want to select only provided module. In cases like that this method
	 * should be used instead of selectModule().
	 */
	public void selectSingleModule(IModuleModel module) {
		selectedModules.clear();
		selectedModules.add(module);

		adjustSelectionBox(false);
	}

	@Override
	public void addModule(IModuleModel module) {
		selectedModules.add(module);
	}

	private static native boolean isClickedOnCellList() /*-{
		return $wnd.isModuleClickedOnCellList;
	}-*/;

	@Override
	public void clearSelectedModules() {
		selectedModules.clear();
	}

	@Override
	public void clearSelectedGroups() {
		selectedGroups.clear();
	}
	
	@Override
	public void deselectModule(IModuleModel module) {
		if (!selectedModules.contains(module)) {
			return;
		}

		selectedModules.remove(module);
		adjustSelectionBox(true);
	};

	private static native boolean setModuleSelectorSelected(String moduleID, boolean shouldSelect) /*-{
		return $wnd.setModuleSelectorSelected(moduleID, shouldSelect);
	}-*/;

	private final native void assignModuleAndSelector(String moduleId) /*-{
		$wnd.assignModuleAndSelector(moduleId);
	}-*/;

	private final native void removeAssignModuleAndSelector() /*-{
		$wnd.removeAssignModuleAndSelector();
	}-*/;

	private final native void onKeyboardEventsCallback() /*-{
		$wnd.onKeyboardEventsCallback();
	}-*/;

	private final native boolean anyModuleShouldNotBeLocked() /*-{
		return $wnd.shouldBeUnlocked;
	}-*/;

	public static native void removeShoulBeUnlocked() /*-{
		$wnd.shouldBeUnlocked = false;
	}-*/;

	public static native void unlockModule(String id) /*-{
		if (id.indexOf("'") > -1){
			var module = $doc.getElementById(id);
			var selector = $wnd.$(module).next();
		} else {
			var selector = $wnd.$("[id='" + id + "']").next();
		} 
		
		selector.resizable("enable");
	}-*/;

	public static native void lockModule(String id) /*-{
		if (id.indexOf("'") > -1){
			var module = $doc.getElementById(id);
			var selector = $wnd.$(module).next();
		} else {
			var selector = $wnd.$("[id='" + id + "']").next();
		} 
		
		selector.resizable("disable");
	}-*/;

	public void adjustSelectionBox(boolean findRelatedModules) {
		if(selectedModules.size() == 1){
			if(!currentModuleID.equals(selectedModules.get(0).getId())){
				removeShoulBeUnlocked();
			}
		}

		AppFrame appFrame = appController.getAppFrame();

		removeSelectionBox();
		removeDynamicSelector();

		if (findRelatedModules && !anyModuleShouldNotBeLocked()) {
			selectAllModulesReleatedToSelection();
		}

		switch (selectedModules.size()) {
			case 0:
				removeShoulBeUnlocked();
				setModuleSelectorSelected(null, false);
				MainPageUtils.restore();
				onPageSelectedAction.execute();
				removeAssignModuleAndSelector();
				onKeyboardEventsCallback();
				break;
			case 1:
				currentModuleID = selectedModules.get(0).getId();
				onKeyboardEventsCallback();
				appFrame.getPresentation().onPageSelected();
				appFrame.setModule(selectedModules.get(0));
				setModuleSelectorSelected(selectedModules.get(0).getId(), true);

				if (selectedModule != null && !selectedModule.getId().equals(selectedModules.get(0).getId())) {
					MainPageUtils.restore();
				}

				if (!SelectionControllerUtils.isModuleInAnyGroup(selectedModules.get(0), (Page) selectedNode)) {
					showHiddenModuleSelectors();
				}

				selectedModule = selectedModules.get(0);

				assignModuleAndSelector(selectedModules.get(0).getId());
				if(anyModuleShouldNotBeLocked()){
					if(selectedModules.get(0).isLocked()){
						lockModule(selectedModules.get(0).getId());
					}else{
						unlockModule(selectedModules.get(0).getId());
					}
				}
				break;
			default:
				removeShoulBeUnlocked();
				MainPageUtils.executeOnPageSelection();
				createSelectionBox();
				setModuleSelectorSelected(null, false);
				MainPageUtils.restore();

				ModulesWidget modules = appFrame.getModules();
				modules.clearSelection();
				for (IModuleModel module : selectedModules) {
					modules.setModule(module);
				}

				appFrame.getStyles().setModule(null);

				if (selectedGroups.size() == 1 && selectedGroups.get(0).size() == selectedModules.size()) {
					// All selected modules belongs to single group
					appFrame.getProperties().setGroup(selectedGroups.get(0));
					appFrame.getStyles().setGroup(selectedGroups.get(0));
				} else {
					appFrame.getProperties().clear();
				}
				break;
		}

		addToDrag();
	}
	
	public static native void addToDrag() /*-{
		if($wnd.onAddToDragAction){
			$wnd.onAddToDragAction();
		}
	}-*/;

	public void clearSelectionBox() {
		removeSelectionBox();
		removeDynamicSelector();
	}

	/**
	 * When single or multiple modules are selected in UI (regardless if it was
	 * done with click or dynamic selection) we need to find all modules related to
	 * this selection. If any module selected belongs to group - all modules belonging
	 * to that group need to be selected as well.
	 *
	 * Only after figuring out which modules should actually be selected we can make a
	 * selection box for them.
	 */
	private void selectAllModulesReleatedToSelection() {
		List<IModuleModel> modulesToBeSelected = new ArrayList<IModuleModel>();
		List<Group> pageGroups = ((Page) selectedNode).getGroupedModules();

		selectedGroups = new ArrayList<Group>();

		for (IModuleModel module : selectedModules) {
			Group groupWithModule = SelectionControllerUtils.getGroupWithModule(module, pageGroups);

			if (groupWithModule != null) {
				for (IModuleModel moduleInGroup : groupWithModule) {
					if (!modulesToBeSelected.contains(moduleInGroup)) {
						modulesToBeSelected.add(moduleInGroup);
					}
				}

				if (!selectedGroups.contains(groupWithModule)) {
					selectedGroups.add(groupWithModule);
				}

				continue;
			}

			if (!modulesToBeSelected.contains(module)) {
				modulesToBeSelected.add(module);
			}
		}

		selectedModules = modulesToBeSelected;
	}

	@Override
	public Iterator<IModuleModel> getSelectedModules() {
		return selectedModules.iterator();
	}

	@Override
	public List<IModuleModel> getSelectedModulesList() {
		return selectedModules;
	}

	@Override
	public IContentNode getSelectedContent() {
		return selectedNode;
	}

	@Override
	public void clearSelection() {
		selectedModules.clear();
		adjustSelectionBox(false);
	}

	@Override
	public void setContentNode(IContentNode node) {
		this.selectedNode = node;

		removeDynamicSelector();
		removeSelectionBox();
	}

	@Override
	public List<Group> getSelectedGroups() {
		return selectedGroups;
	}

	@Override
	public Group getSelectedGroupOfModules() {
		Group selectedGroup = new Group();

		selectedGroup.addAll(selectedModules);

		return selectedGroup;
	}

	public void setActionFactory(ActionFactory actionFactory) {
		onPageSelectedAction = actionFactory.getAction(ActionType.uiPageSelected);
		onModuleSelectedAction = (UIModuleSelectedAction) actionFactory.getAction(ActionType.uiModuleSelected);
	}

	private final native void shouldDisableDrag(boolean disableModules) /*-{
		if(typeof $wnd.iceShowHiddenModuleSelectors == 'function') {
			$wnd.shouldDisableDrag(disableModules);
		}
	}-*/;

	public void setContentWrapper(SimplePanel contentWrapper) {
		this.contentWrapper = contentWrapper;
		this.contentElement = contentWrapper.getElement();

		DOM.sinkEvents(contentElement, Event.ONMOUSEDOWN | Event.ONMOUSEUP | Event.ONMOUSEMOVE | Event.ONMOUSEOVER);
		Event.setEventListener(contentElement, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if (!captureEvents) {
					return;
				}

				if (!(selectedNode instanceof Page)) {
					return;
				}

				if (isModuleInAction()) {
					return;
				}

				if (!shouldHandleEvent(event)) {
					return;
				}

				final int eventCode = DOM.eventGetType(event);

				event.preventDefault();
				event.stopPropagation();

				switch (eventCode) {
					case Event.ONMOUSEDOWN:
						onMouseDown(event);
						break;
					case Event.ONMOUSEMOVE:
						onMouseMove(event);
						break;
					case Event.ONMOUSEUP:
						if(selectedModules.size() > 0){
							unfocusInputs();
						}
						onMouseUp();
						isGroupSelection = false;
						break;
					case Event.ONCLICK:
						onClick();
						break;
				}
			}
		});
	}

	private final native boolean unfocusInputs() /*-{
		$wnd.$("input").blur();
	}-*/;

	public void setPresentationWidget(PresentationWidget presentation) {
		presentationPanel = presentation.getMainPagePanel();
	}

	private final native boolean isModuleInAction() /*-{
		return $wnd.isModuleInAction;
	}-*/;

	private native String SVGAnimatedStringToString(String string)/*-{
		if (string.baseVal != null) return string.baseVal;
		return string;
	}-*/;
	
	private boolean shouldHandleEvent(Event event) {
		Element target = getEventTarget(event);

		if (isMouseMoving) {
			return true;
		}

		String className = SVGAnimatedStringToString(target.getClassName().toString());

		return className.startsWith("ic_page ic_main") || target.getId().equals("content") || className.equals("dynamicModuleSelector");
	}

	private Element getEventTarget(Event event) {
		return (Element) Element.as(event.getEventTarget());
	}

	private void onMouseDown(Event event) {
		int scrollTop = Math.round(getScrollTop());
		mouseLastX = event.getClientX();
		mouseLastY = event.getClientY()+ scrollTop;
		isMouseMoving = true;

		createDynamicSelector(mouseLastX, mouseLastY);

		DOM.setCapture(contentElement);
	}

	private void createDynamicSelector(int clientX, int clientY) {
		int x = clientX - presentationPanel.getAbsoluteLeft();
		int y = clientY - presentationPanel.getAbsoluteTop();

		dynamicModuleSelector = new HTML();
		dynamicModuleSelector.setStyleName("dynamicModuleSelector");
		dynamicModuleSelector.setPixelSize(0, 0);

		presentationPanel.add(dynamicModuleSelector, x, y);
	}

	private void onMouseMove(Event event) {
		int scrollTop = Math.round(getScrollTop());
		if (dynamicModuleSelector != null) {
			resizeSelectionBox(event.getClientX(), event.getClientY()+scrollTop);
		}

		mouseLastX = event.getClientX();
		mouseLastY = event.getClientY()+ scrollTop;

		if(isMouseMoving){
			isGroupSelection = true;
		}
	}

	private void resizeSelectionBox(int clientX, int clientY) {
		int x = clientX - presentationPanel.getAbsoluteLeft();
		int y = clientY - presentationPanel.getAbsoluteTop();

		int width = x - presentationPanel.getWidgetLeft(dynamicModuleSelector);
		int height = y - presentationPanel.getWidgetTop(dynamicModuleSelector);

		dynamicModuleSelector.setPixelSize(width, height);
	}

	private void onMouseUp() {
		makeSelection();
		removeDynamicSelector();

		isMouseMoving = false;
		DOM.releaseCapture(contentElement);
	}

	private void removeDynamicSelector() {
		if (dynamicModuleSelector == null) {
			return;
		}

		presentationPanel.remove(dynamicModuleSelector);
		dynamicModuleSelector = null;
	}

	static class SelectionBoundries extends JavaScriptObject {
		protected SelectionBoundries() {}

		public final native int getTop()  /*-{ return this.top;  }-*/;
		public final native int getBottom()  /*-{ return this.bottom;  }-*/;
		public final native int getLeft()  /*-{ return this.left;  }-*/;
		public final native int getRight()  /*-{ return this.right;  }-*/;
	}

	static class SelectedModule extends SelectionBoundries {
		protected SelectedModule() {}

		public final native String getID() /*-{ return this.id; }-*/;
	}

	static class SelectedModulesArray<E extends JavaScriptObject> extends JavaScriptObject {
		protected SelectedModulesArray() { }
		public final native int length() /*-{ return this.length; }-*/;
		public final native E get(int i) /*-{ return this[i];     }-*/;
	}

	private final native float getScrollTop() /*-{
		return $wnd.$($wnd).scrollTop();
	}-*/;

	private void makeSelection() {
		if (dynamicModuleSelector == null) {
			return;
		}

		removeSelectionBox();

		int scrollTop = Math.round(getScrollTop());
		String left = dynamicModuleSelector.getElement().getStyle().getLeft();
		int x1 = (int) Math.round(Double.valueOf(left.substring(0, left.length() - 2))); // Removing "px" suffix
		String top = dynamicModuleSelector.getElement().getStyle().getTop();
		int y1 = (int) Math.round(Double.valueOf(top.substring(0, top.length() - 2))) + scrollTop; // Removing "px" suffix

		int x2 = x1 + dynamicModuleSelector.getOffsetWidth();
		int y2 = y1 + dynamicModuleSelector.getOffsetHeight();

		SelectedModulesArray<SelectedModule> modules = executeFindModulesInBoundries(x1, y1, x2, y2);

		selectedModules.clear();

		Page page = (Page) selectedNode;

		for (int i = 0; i < modules.length(); i++) {
			IModuleModel selectedModule = page.getModules().getModuleById(modules.get(i).getID());
			if (selectedModule.isModuleInEditorVisible()) {
				selectedModules.add(selectedModule);
			}
		}

		adjustSelectionBox(true);
	}

	private void createSelectionBox() {
		ArrayList<String> idsList = new ArrayList<String>();
		for (int i = 0; i < selectedModules.size(); i++) {
			final IModuleModel selectedModule = selectedModules.get(i);
			if (selectedModule.isModuleInEditorVisible()) {
				idsList.add(selectedModule.getId());
			}
		}

		String[] ids = idsList.toArray(new String[idsList.size()]);

		SelectionBoundries boundries = executeGetSelectedModulesBoundries(ids);

		selectionBox = new HTML();
		selectionBox.setStyleName("multipleModuleSelector");
		selectionBox.setPixelSize(boundries.getRight() - boundries.getLeft(), boundries.getBottom() - boundries.getTop());
		presentationPanel.add(selectionBox, boundries.getLeft(), boundries.getTop());

		PresentationUtils.hideModuleSelectors();
		makeDraggable(ids);
	}

	private static native void makeDraggable(String[] ids) /*-{
		if (typeof $wnd.makeDraggable == 'function') {
			$wnd.makeDraggable(ids);
		}
	}-*/;

	private static native SelectedModulesArray<SelectedModule> executeFindModulesInBoundries(int x1, int y1, int x2, int y2) /*-{
		if(typeof $wnd.iceFindModulesInBoundries == 'function') {
			return $wnd.iceFindModulesInBoundries(x1, y1, x2, y2);
		}

		return [];
	}-*/;

	private static native SelectionBoundries executeGetSelectedModulesBoundries(String[] ids) /*-{
		if (typeof $wnd.iceGetSelectedModulesBoundries == 'function') {
			return $wnd.iceGetSelectedModulesBoundries(ids);
		}

		return {top: 0, bottom: 0, left: 0, right: 0};
	}-*/;

	private void removeSelectionBox() {
		if (selectionBox != null) {
			presentationPanel.remove(selectionBox);
			showHiddenModuleSelectors();
			selectionBox = null;
		}
	}

	private static native void showHiddenModuleSelectors() /*-{
		if(typeof $wnd.iceShowHiddenModuleSelectors == 'function') {
			$wnd.iceShowHiddenModuleSelectors();
		}
	}-*/;

	private void onClick() {
		if (dynamicModuleSelector != null) {
			onMouseUp();
		}

		removeSelectionBox();

		onPageSelectedAction.execute();
	}

	private void setSelectionPosition(String position, int value) {
		selectionPosition.put("startTop", value);
	}

	@Override
	public Group findGroup(IModuleModel module) {
		if (!(selectedNode instanceof Page)) {
			return null;
		}

		String pageID = ((Page) selectedNode).getId();

		for (Group group : groupedModules.get(pageID)) {
			if (group.contains(module)) {
				return group;
			}
		}

		return null;
	}

	@Override
	public void addGroupedModules(String pageID, Group modules) {
		if (!groupedModules.containsKey(pageID)) {
			List<Group> newGroup = new ArrayList<Group>();
			newGroup.add(modules);

			groupedModules.put(pageID, newGroup);
		} else if (!groupedModules.get(pageID).contains(modules)){
			groupedModules.get(pageID).add(modules);
		}
	}

	@Override
	public void removeGroup(String pageID, Iterator<IModuleModel> selectedModules) {
		List<Group> groupsList = groupedModules.get(pageID);

		while (selectedModules.hasNext()) {
			IModuleModel module = selectedModules.next();
			for (Group group : groupsList) {
				if (group.contains(module)) {
					groupedModules.get(pageID).remove(group);
					
					break;
				}
			}
		}
	}

	@Override
	public List<Group> getPageGroups(String pageID) {
		if(groupedModules.get(pageID) == null) {
			groupedModules.put(pageID, new ArrayList<Group>());
		}
		return groupedModules.get(pageID);
	}
	
	public List<Group> getPageGroupsCopy(String pageID) {
		List<Group> groups = groupedModules.get(pageID);
		if (groups == null) {
			return new ArrayList<Group>();
		}
		List <Group> groupModules = new ArrayList<Group>();
		for (int i = 0; i < groups.size(); i++) {
			if (!groups.get(i).isEmpty()) {
				groupModules.add(groups.get(i));
			}
		}
		return groupModules;
	}

	public void setGroupedModulesFromXML(Page page) {
		if (page.getGroupedModules() != null) {
			groupedModules.put(page.getId(), page.getGroupedModules());
		}else if(groupedModules.get(page.getId()) == null) {
			groupedModules.put(page.getId(), new ArrayList<Group>());
		}
	}

	@Override
	public Group getGroupById(Page page, String groupId) {
		List<Group> groupsList = getPageGroups(page.getId());
		if (groupsList != null) {
			for (Group group : groupsList) {
				if (group.getId().equals(groupId)) {
					return group;
				}
			}
		}

		return null;
	}
	
}
