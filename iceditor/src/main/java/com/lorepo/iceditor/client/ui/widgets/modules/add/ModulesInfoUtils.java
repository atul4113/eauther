package com.lorepo.iceditor.client.ui.widgets.modules.add;

import com.google.gwt.core.client.GWT;
import com.lorepo.iceditor.client.actions.AbstractAction;
import com.lorepo.iceditor.client.actions.ActionFactory;
import com.lorepo.iceditor.client.actions.ActionFactory.ActionType;
import com.lorepo.iceditor.client.actions.InsertAddonAction;
import com.lorepo.iceditor.client.actions.InsertButtonAction;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.dlg.ModuleInfo;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.addon.AddonEntry;
import com.lorepo.icplayer.client.module.button.ButtonModule.ButtonType;

import java.util.*;

public class ModulesInfoUtils {
	private HashMap<String, List<ModuleInfo>> moduleInfos;

	private ActionFactory actionFactory;
	private AppController appController;

	public ModulesInfoUtils(ActionFactory actionFactory, AppController appController) {
		this.actionFactory = actionFactory;
		this.appController = appController;

		initModuleInfos();
		addModules();
		addAddons();
	}

	private void initModuleInfos() {
		moduleInfos = new HashMap<String, List<ModuleInfo>>();
		moduleInfos.put(DictionaryWrapper.get("favourite_menu"), new ArrayList<ModuleInfo>());
		moduleInfos.put(DictionaryWrapper.get("activities_menu"), new ArrayList<ModuleInfo>());
		moduleInfos.put(DictionaryWrapper.get("games_menu"), new ArrayList<ModuleInfo>());
		moduleInfos.put(DictionaryWrapper.get("reporting_menu"), new ArrayList<ModuleInfo>());
		moduleInfos.put(DictionaryWrapper.get("navigation_menu"), new ArrayList<ModuleInfo>());
		moduleInfos.put(DictionaryWrapper.get("media_menu"), new ArrayList<ModuleInfo>());
		moduleInfos.put(DictionaryWrapper.get("scripting_menu"), new ArrayList<ModuleInfo>());
	}

	private void addModules() {
		List<ModuleInfo> category;
		InsertButtonAction action;;
		String base = GWT.getModuleBaseURL() + "theme/old/modules/";

		category = moduleInfos.get(DictionaryWrapper.get("reporting_menu"));
		addModule(category, "error_counter_menu",
				actionFactory.getAction(ActionType.insertErrorCounterModule),
				base + "error_counter.png",
				DictionaryWrapper.get("error_counter_info"));

		addModule(category, "check_counter_menu",
				actionFactory.getAction(ActionType.insertCheckCounterModule),
				base + "check_counter.png",
				DictionaryWrapper.get("check_counter_info"));

		addModule(category, "lesson_report_menu",
				actionFactory.getAction(ActionType.insertReportModule),
				base + "report.png",
				DictionaryWrapper.get("lesson_report_info"));

		addModule(category, "page_progress_menu",
				actionFactory.getAction(ActionType.insertPageProgressModule),
				base + "page_progress.png",
				DictionaryWrapper.get("page_progress_info"));

		addModule(category, "check_answers_button_menu",
				actionFactory.getAction(ActionType.insertCheckModule),
				base + "btn_check.png",
				DictionaryWrapper.get("check_answers_button_info"));

		addModule(category, "limited_check_menu",
				actionFactory.getAction(ActionType.insertLimitedCheckModule),
				base + "btn_limited_check.png",
				DictionaryWrapper.get("Limited_Check_info"));

		addModule(category, "limited_reset_menu",
				actionFactory.getAction(ActionType.insertLimitedResetModule),
				base + "btn_limited_reset.png",
				DictionaryWrapper.get("Limited_Reset_info"));

		addModule(category, "lesson_reset_menu",
				actionFactory.getAction(ActionType.insertLessonResetModule),
				base + "reset_global.png",
				DictionaryWrapper.get("Lesson_Reset_info"));

		action = actionFactory.getInsertButtonAction();
		action.setButtonType(ButtonType.reset);
		addModule(category, "reset_button_menu", action,
				base + "btn_reset.png",
				DictionaryWrapper.get("reset_button_info"));

		category = moduleInfos.get(DictionaryWrapper.get("navigation_menu"));
		action = actionFactory.getInsertButtonAction();
		action.setButtonType(ButtonType.nextPage);
		addModule(category, "next_page_button_menu", action,
				base + "btn_next.png",
				DictionaryWrapper.get("next_page_button_info"));
		action = actionFactory.getInsertButtonAction();
		action.setButtonType(ButtonType.prevPage);
		addModule(category, "previous_page_button_menu", action,
				base + "btn_prev.png",
				DictionaryWrapper.get("previous_page_button_info"));
		action = actionFactory.getInsertButtonAction();
		action.setButtonType(ButtonType.gotoPage);
		addModule(category, "go_to_page_button_menu", action,
				base + "btn_goto.png",
				DictionaryWrapper.get("go_to_page_button_info"));
		action = actionFactory.getInsertButtonAction();
		action.setButtonType(ButtonType.popup);
		addModule(category, "open_popup_button_menu", action,
				base + "btn_popup.png",
				DictionaryWrapper.get("open_popup_button_info"));
		action = actionFactory.getInsertButtonAction();
		action.setButtonType(ButtonType.cancel);
		addModule(category, "close_popup_button_menu", action,
				base + "btn_close.png",
				DictionaryWrapper.get("close_popup_button_info"));

		category = moduleInfos.get(DictionaryWrapper.get("activities_menu"));
		addModule(category, "choice_menu",
				actionFactory.getAction(ActionType.insertChoiceModule),
				base + "choice.png",
				DictionaryWrapper.get("choice_info"));

		addModule(category, "image_source_menu",
				actionFactory.getAction(ActionType.insertImageSourceModule),
				base + "image_source.png",
				DictionaryWrapper.get("image_source_info"));

		addModule(category, "image_gap_menu",
				actionFactory.getAction(ActionType.insertImageGapModule),
				base + "image_gap.png",
				DictionaryWrapper.get("image_gap_info"));

		addModule(category, "ordering_menu",
				actionFactory.getAction(ActionType.insertOrderingModule),
				base + "ordering.png",
				DictionaryWrapper.get("ordering_info"));

		addModule(category, "source_list_menu",
				actionFactory.getAction(ActionType.insertSourceListModule),
				base + "sourcelist.png",
				DictionaryWrapper.get("source_list_info"));

		addModule(category, "text_menu",
				actionFactory.getAction(ActionType.insertTextModule),
				base + "text.png",
				DictionaryWrapper.get("text_info"));

		category = moduleInfos.get(DictionaryWrapper.get("media_menu"));
		addModule(category, "image_menu",
				actionFactory.getAction(ActionType.insertImageModule),
				base + "image.png",
				DictionaryWrapper.get("image_info"));

		addModule(category, "shape_menu",
				actionFactory.getAction(ActionType.insertShapeModule),
				base + "shape.png",
				DictionaryWrapper.get("shape_info"));
	}

	private void addAddons() {
		Collection<AddonEntry> entries = appController.getAddonList();
		String base = GWT.getModuleBaseURL() + "addons/";

		for(AddonEntry entry : entries){
			if(entry.getCategory().equals("not_visible"))
				continue;

			String categoryName = DictionaryWrapper.get(entry.getCategory());
			List<ModuleInfo> category = moduleInfos.get(categoryName);
			if(category == null){
				category = new ArrayList<ModuleInfo>();
				moduleInfos.put(categoryName, category);
			}
			String name = entry.getName();
			String originalName = entry.getId() + "_name";

			if(DictionaryWrapper.contains(name)){
				name = DictionaryWrapper.get(name);
			}

			AbstractAction action = new InsertAddonAction(appController, entry);
			addModule(category, originalName, action,
					base + entry.getId() + ".png", DictionaryWrapper.get(entry.getId() + "_info"));
		}
	}

	private static void addModule(List<ModuleInfo> category, String originalName, AbstractAction action,
			String imageURL, String about) {

		String title = DictionaryWrapper.get(originalName);

		ModuleInfo info = new ModuleInfo();
		info.name = title;
		info.originalName = originalName;
		info.command = action;
		info.imageUrl = imageURL;
		info.info = about;

		category.add(info);
	}

	public Set<String> getCategories() {
		return moduleInfos.keySet();
	}

	public List<ModuleInfo> getCategory(String category) {
		return moduleInfos.get(category);
	}

	public void addFavouritiesModules() {
		HashMap<String, ModuleInfo> favourities = appController.getFavouriteModules();
		List<ModuleInfo> modules = new ArrayList<ModuleInfo>();

		for (ModuleInfo moduleInfo : favourities.values()) {
			modules.add(moduleInfo);
		}

		moduleInfos.put(DictionaryWrapper.get("favourite_menu"), modules);
	}

	public HashMap<String, ModuleInfo> getTranslatedAddonsAndModules() {
		TreeMap<String, ModuleInfo> orderedModules = new TreeMap<String, ModuleInfo>();
		HashMap<String, ModuleInfo> modules = new HashMap<String, ModuleInfo>();

		for (String key : moduleInfos.keySet()) {
			if (key.equals(DictionaryWrapper.get("favourite_menu"))) continue;

			for(ModuleInfo moduleInfo : moduleInfos.get(key)) {
				orderedModules.put(moduleInfo.name, moduleInfo);
			}
		}

		modules.putAll(orderedModules);

		return modules;
	}

	public HashMap<String, ModuleInfo> getAddonsAndModules() {
		TreeMap<String, ModuleInfo> orderedModules = new TreeMap<String, ModuleInfo>();
		HashMap<String, ModuleInfo> modules = new HashMap<String, ModuleInfo>();

		for (String key : moduleInfos.keySet()) {
			if (key.equals(DictionaryWrapper.get("favourite_menu"))) continue;

			for(ModuleInfo moduleInfo : moduleInfos.get(key)) {
				orderedModules.put(moduleInfo.originalName, moduleInfo);
			}
		}

		modules.putAll(orderedModules);

		return modules;
	}

	public void setModules(String category, HashMap<String, ModuleInfo> modules) {
		List<ModuleInfo> infos = new ArrayList<ModuleInfo>();

		for (ModuleInfo moduleInfo : modules.values()) {
			infos.add(moduleInfo);
		}

		moduleInfos.put(category, infos);
	}
}
