package com.lorepo.iceditor.client.ui.widgets.modules;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.AnchorElement;
import com.google.gwt.dom.client.SpanElement;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.actions.AbstractAction;
import com.lorepo.iceditor.client.actions.ActionFactory;
import com.lorepo.iceditor.client.actions.ActionFactory.ActionType;
import com.lorepo.iceditor.client.actions.HideModuleInEditorAction;
import com.lorepo.iceditor.client.actions.LockModuleAction;
import com.lorepo.iceditor.client.actions.ShowModuleInEditorAction;
import com.lorepo.iceditor.client.actions.UIModuleDeselectedAction;
import com.lorepo.iceditor.client.actions.UISingleModuleSelectedAction;
import com.lorepo.iceditor.client.actions.UnlockModuleAction;
import com.lorepo.iceditor.client.controller.SelectionController;
import com.lorepo.iceditor.client.controller.SelectionControllerUtils;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.ModuleList;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.api.IModuleModel;

public class ModulesWidget extends Composite {

	private static ModulesWidgetUiBinder uiBinder = GWT.create(ModulesWidgetUiBinder.class);

	interface ModulesWidgetUiBinder extends UiBinder<Widget, ModulesWidget> {
	}

	@UiField HTMLPanel panel;
	@UiField HTMLPanel modulesList;
	@UiField AnchorElement showModules;
	@UiField AnchorElement hideModules;
	@UiField AnchorElement lockModules;
	@UiField AnchorElement unlockModules;
	@UiField AnchorElement moduleUp;
	@UiField AnchorElement moduleDown;
	@UiField AnchorElement sortModules;
	@UiField SpanElement title;
	@UiField AnchorElement bringToFront;
	@UiField AnchorElement sendBack;

	private SelectionController selectionController;

	private final List<IModuleModel> selectedModules = new ArrayList<IModuleModel>();
	private final Map<IModuleModel, ModuleWidget> modulesWidgets = new HashMap<IModuleModel, ModuleWidget>();

	private HideModuleInEditorAction onModuleHide;
	private ShowModuleInEditorAction onModuleShow;
	private LockModuleAction onModuleLock;
	private UnlockModuleAction onModuleUnlock;
	private AbstractAction onModuleUp;
	private AbstractAction onModuleDown;
	private UISingleModuleSelectedAction onSingleModuleSelected;
	private UIModuleDeselectedAction onModuleDeselected;
	public ModuleList refreshModules;
	private Page currentPage;
	private AbstractAction onBringToFront;
	private AbstractAction onSendBack;
	private AbstractAction onSortModules;

	public ModulesWidget() {
		initWidget(uiBinder.createAndBindUi(this));

		modulesList.getElement().setId("modulesList");
		showModules.setId("showModules");
		hideModules.setId("hideModules");
		lockModules.setId("lockModules");
		unlockModules.setId("unlockModules");
		moduleUp.setId("moduleUp");
		moduleDown.setId("moduleDown");
		bringToFront.setId("bringToFront");
		sendBack.setId("sendBack");
		sortModules.setId("sortModules");

		updateElementsText();

		connectHandlers();
		isModuleLockedJS(this);
	}

	private void connectHandlers() {
		Event.sinkEvents(showModules, Event.ONCLICK);
		Event.setEventListener(showModules, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if (Event.ONCLICK != event.getTypeInt()) {
					return;
				}

				for (IModuleModel module : selectedModules) {
					modulesWidgets.get(module).setVisible(true);

				}

				onModuleShow.execute();
			}
		});

		Event.sinkEvents(hideModules, Event.ONCLICK);
		Event.setEventListener(hideModules, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if (Event.ONCLICK != event.getTypeInt()) {
					return;
				}

				for (IModuleModel module : selectedModules) {
					modulesWidgets.get(module).setVisible(false);
				}

				onModuleHide.execute();
				selectionController.clearSelectionBox();
			}
		});

		Event.sinkEvents(lockModules, Event.ONCLICK);
		Event.setEventListener(lockModules, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if (Event.ONCLICK != event.getTypeInt()) {
					return;
				}

				for (IModuleModel module : selectedModules) {
					modulesWidgets.get(module).setLocked(true);

				}

				onModuleLock.execute();
			}
		});

		Event.sinkEvents(unlockModules, Event.ONCLICK);
		Event.setEventListener(unlockModules, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if (Event.ONCLICK != event.getTypeInt()) {
					return;
				}

				for (IModuleModel module : selectedModules) {
					modulesWidgets.get(module).setLocked(false);
				}

				onModuleUnlock.execute();
			}
		});

		Event.sinkEvents(moduleUp, Event.ONCLICK);
		Event.setEventListener(moduleUp, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if (Event.ONCLICK != event.getTypeInt()) {
					return;
				}

				onModuleUp.execute();
			}
		});

		Event.sinkEvents(moduleDown, Event.ONCLICK);
		Event.setEventListener(moduleDown, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if (Event.ONCLICK != event.getTypeInt()) {
					return;
				}

				onModuleDown.execute();
			}
		});
		
		Event.sinkEvents(bringToFront, Event.ONCLICK);
		Event.setEventListener(bringToFront, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if (Event.ONCLICK != event.getTypeInt()) {
					return;
				}

				onBringToFront.execute();
			}
		});
		
		Event.sinkEvents(sendBack, Event.ONCLICK);
		Event.setEventListener(sendBack, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if (Event.ONCLICK != event.getTypeInt()) {
					return;
				}

				onSendBack.execute();
			}
		});
		
		Event.sinkEvents(sortModules, Event.ONCLICK);
		Event.setEventListener(sortModules, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if (Event.ONCLICK != event.getTypeInt()) {
					return;
				}

				onSortModules.execute();
			}
		});
	}

	private void deselectCurrentModules() {
		for (IModuleModel selectedModule : selectedModules) {
			modulesWidgets.get(selectedModule).setSelected(false);
		}

		selectionController.clearSelection();
		selectedModules.clear();
	}

	private boolean isModuleSelected(IModuleModel module) {
		for (IModuleModel selectedModule : selectedModules) {
			if (selectedModule.getId().equals(module.getId())) {
				return true;
			}
		}

		return false;
	}

	private boolean hasVisibleModule(List<IModuleModel> selectedModules) {
		for (IModuleModel module: selectedModules) {
			if (module.isModuleInEditorVisible()) {
				return true;
			}
		}

		return false;
	}

	public void setPage(Page page) {
		clear();
		currentPage = page;
		ModuleList modules = page.getModules();
		refreshModules = modules;
		setModulesList(modules);
	}

	public void setActionFactory(ActionFactory actionFactory) {
		onModuleHide = (HideModuleInEditorAction) actionFactory.getAction(ActionType.hideModuleInEditor);
		onModuleShow = (ShowModuleInEditorAction) actionFactory.getAction(ActionType.showModuleInEditor);
		onModuleLock = (LockModuleAction) actionFactory.getAction(ActionType.lockModule);
		onModuleUnlock = (UnlockModuleAction) actionFactory.getAction(ActionType.unlockModule);
		onModuleUp = actionFactory.getAction(ActionType.moveModuleUp);
		onModuleDown = actionFactory.getAction(ActionType.moveModuleDown);
		onSortModules = actionFactory.getAction(ActionType.sortModules);

		onSingleModuleSelected = (UISingleModuleSelectedAction) actionFactory.getAction(ActionType.uiSingleModuleSelected);
		onModuleDeselected = (UIModuleDeselectedAction) actionFactory.getAction(ActionType.uiModuleDeselected);
		
		onBringToFront = actionFactory.getAction(ActionType.bringToFrontModule);
		onSendBack = actionFactory.getAction(ActionType.sendBackModule);
	}

	private void selectAllBetween(IModuleModel startModule, IModuleModel endModule) {
		boolean isSelectionStarted = false;

		for (IModuleModel item : modulesWidgets.keySet()) {
			if (item.equals(startModule) || item.equals(endModule)) {
				if (isSelectionStarted) {
					modulesWidgets.get(item).setSelected(true);
					selectedModules.add(item);
					selectionController.selectModule(item);
					return;
				}

				isSelectionStarted = true;
			}
			if (isSelectionStarted) {
				modulesWidgets.get(item).setSelected(true);
				selectedModules.add(item);
				selectionController.selectModule(item);
			}
		}
	}

	private void selectModulesWithShiftKey(IModuleModel module) {
		IModuleModel firstSelectedModule = null;
		IModuleModel lastSelectedModule = null;
		int i = 0;

		for (IModuleModel item : modulesWidgets.keySet()) {
			if (modulesWidgets.get(item).isSelected() && i == 0) {
				firstSelectedModule = item;
				lastSelectedModule = item;
				i++;
			} else if (modulesWidgets.get(item).isSelected()) {
				lastSelectedModule = item;
			}
		}

		if (module.equals(lastSelectedModule)) {
			lastSelectedModule = firstSelectedModule;
		}

		selectAllBetween(module, lastSelectedModule);
	}

	public void setModule(IModuleModel module) {
		if (isModuleSelected(module)) {
			return;
		}

		modulesWidgets.get(module).setSelected(true);
		selectedModules.add(module);
	}

	public void updateElementsText() {
		showModules.setAttribute("data-tooltip", DictionaryWrapper.get("show_module_tooltip"));
		hideModules.setAttribute("data-tooltip", DictionaryWrapper.get("hide_module_tooltip"));
		lockModules.setAttribute("data-tooltip", DictionaryWrapper.get("lock_module_menu"));
		unlockModules.setAttribute("data-tooltip", DictionaryWrapper.get("unlock_module_menu"));
		moduleUp.setAttribute("data-tooltip", DictionaryWrapper.get("move_module_up_menu"));
		moduleDown.setAttribute("data-tooltip", DictionaryWrapper.get("move_module_down_menu"));
		bringToFront.setAttribute("data-tooltip", DictionaryWrapper.get("bring_to_front_menu"));
		sendBack.setAttribute("data-tooltip", DictionaryWrapper.get("send_back_menu"));
		sortModules.setAttribute("data-tooltip", DictionaryWrapper.get("sort_modules"));
		title.setInnerText(DictionaryWrapper.get("modules"));
	}

	public void clear() {
		clearSelection();

		modulesList.clear();
		modulesWidgets.clear();
	}

	public void setModulesList(ModuleList pageModules) {
		for (int i = pageModules.size() - 1; i >= 0; i--) {
			final IModuleModel module = pageModules.get(i);

			ModuleWidget moduleWidget = new ModuleWidget();
			moduleWidget.setId(module.getId());
			moduleWidget.setVisible(module.isModuleInEditorVisible());
			moduleWidget.setLocked(module.isLocked());
			if(module.isLocked()){
				addDisableClass(module.getId());
			}
			moduleWidget.setListener(new ModuleChangeListener() {
				@Override
				public void onVisibilityChanged(boolean isVisible) {
					if (isVisible) {
						onModuleShow.execute(module);
					} else {
						onModuleHide.execute(module);
					}
				}

				@Override
				public void onSelected(boolean isCtrlPressed, boolean isShiftPressed) {
					if (isModuleSelected(module) && isCtrlPressed) {
						modulesWidgets.get(module).setSelected(false);
						onModuleDeselected.execute(module);
						return;
					}

					if (isShiftPressed) {
						selectModulesWithShiftKey(module);
						return;
					}

					if (!isCtrlPressed) {
						deselectCurrentModules();
					}

					// Crtl Pressed + module is not selected
					modulesWidgets.get(module).setSelected(true);
					selectedModules.add(module);

					if (selectedModules.size() == 1) {
						onSingleModuleSelected.execute(module);
					} else {
						selectionController.selectModule(module);
						if (!hasVisibleModule(selectedModules)) {
							selectionController.clearSelectionBox();
						}
					}

					if(SelectionControllerUtils.isModuleInAnyGroup(selectedModules.get(0), currentPage)){
						makeModuleUnlocked(module.getId());
					}
				}

				@Override
				public void onLockedChanged(boolean isLocked) {
					if (isLocked) {
						onModuleLock.execute(module);
					} else {
						onModuleUnlock.execute(module);
					}
				}
			});

			modulesList.add(moduleWidget);
			modulesWidgets.put(module, moduleWidget);
		}
	}

	private static native void addDisableClass(String id) /*-{
		if (id.indexOf("'") > -1){
			var module = $doc.getElementById(id);
			$wnd.$(module).next().addClass("ui-state-disabled");
		} else {
			$wnd.$("[id='" + id + "']").next().addClass("ui-state-disabled");
		} 
		
		
		var module = $doc.getElementById(id);
		$wnd.$(module).next().addClass("ui-state-disabled");
	}-*/;

	private static native void makeModuleUnlocked(String id) /*-{
		$wnd.shouldBeUnlocked = true;
		if (id.indexOf("'") > -1){
			var module = $doc.getElementById(id);
			var selector = $wnd.$(module).next();
		} else {
			var selector = $wnd.$("[id='" + id + "']").next();
		} 
		
		$wnd.addListerToSelector(selector);
		if($wnd.isModuleLocked(id)){
			selector.resizable("disable");
		}
	}-*/;

	private static native boolean isModuleLockedJS(ModulesWidget x) /*-{
        $wnd.isModuleLocked = function(id) {
          return x.@com.lorepo.iceditor.client.ui.widgets.modules.ModulesWidget::isModuleLocked(Ljava/lang/String;)(id);
        };
	}-*/;

	public boolean isModuleLocked (String id){
		IModuleModel module = refreshModules.getModuleById(id);
		return module.isLocked();
	}

	public void refreshModulesList() {
		clear();
		setModulesList(refreshModules);
	}

	public void clearSelection() {
		for (IModuleModel selectedModule : selectedModules) {
			modulesWidgets.get(selectedModule).setSelected(false);
		}

		selectedModules.clear();
	}

	public void setSelectionController(SelectionController selectionController) {
		this.selectionController = selectionController;
	}
}
