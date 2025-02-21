package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.actions.api.IActionService;
import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.ui.widgets.content.MainPageEventListener;
import com.lorepo.iceditor.client.ui.widgets.content.SettingsWidget;
import com.lorepo.icplayer.client.model.Content;

public class PreferencesAction extends AbstractAction{
	private IAppController appController = this.getServices().getAppController();
	private SettingsWidget settings = this.appController.getAppFrame().getSettings();
	
	public PreferencesAction(IActionService services) {
		super(services);
	}

	@Override
	public void execute() {
		this.initPreferences();

		this.settings.setListener(new MainPageEventListener() {
			@Override
			public void onSave() {
				setPreferences();
				settings.hide();
			}
			
			@Override
			public void onApply() {
				setPreferences();
			}
		});
		
		this.settings.show();
	}

	private String validGridSize(String gridSize) {
		try {
			int gridSizeAsNumber = Integer.parseInt(gridSize);

			return gridSizeAsNumber < 2 ? "2" : gridSize;
			
		} catch (NumberFormatException e){
			return "20";
		}
	}
	
	private String validateLang(String lang) {
		if (lang.compareTo("undefined") == 0) {
			return "";
		} else {
			return lang;
		}
	}

	private void initPreferences() {
		Content content = this.getModel();
		String gridSize = this.validGridSize(content.getMetadataValue("gridSize"));
		final String initialGridSize = "20";
		
		if (gridSize == null || Integer.parseInt(gridSize) < 2) {
			gridSize = initialGridSize;
		}
		
		this.settings.setStaticHeaderSelected(Boolean.valueOf(content.getMetadataValue("staticHeader")));
		this.settings.setStaticFooterSelected(Boolean.valueOf(content.getMetadataValue("staticFooter")));
		
		this.settings.setUseGridSelected(Boolean.valueOf(content.getMetadataValue("useGrid")));
		this.settings.setGridSnappingSelected(Boolean.valueOf(content.getMetadataValue("snapToGrid")));
		this.settings.setGridSize(gridSize);
		
		this.settings.setUseRulersSelected(Boolean.valueOf(content.getMetadataValue("useRulers")));
		this.settings.setRulersSnappingSelected(Boolean.valueOf(content.getMetadataValue("snapToRulers")));

		settings.setLang(validateLang(content.getMetadataValue("lang")));

		settings.setEnableTabindexSelected(Boolean.valueOf(content.getMetadataValue("enableTabindex")));
		settings.setSortRightToLeftSelected(Boolean.valueOf(content.getMetadataValue("sortRightToLeft")));

	}

	
	protected void setPreferences() {
		Content content = this.getModel();
		content.setMetadataValue("staticHeader", String.valueOf(this.settings.isStaticHeaderSelected()));
		content.setMetadataValue("staticFooter", String.valueOf(this.settings.isStaticFooterSelected()));
		
		content.setMetadataValue("useGrid", String.valueOf(this.settings.isUseGridSelected()));
		content.setMetadataValue("gridSize", String.valueOf(this.settings.getGridSize()));
		content.setMetadataValue("snapToGrid", String.valueOf(this.settings.isGridSnappingSelected()));
		
		content.setMetadataValue("useRulers", String.valueOf(this.settings.isUseRulersSelected()));
		content.setMetadataValue("snapToRulers", String.valueOf(this.settings.isRulersSnappingSelected()));

		content.setMetadataValue("lang", String.valueOf(settings.getLang()));

		content.setMetadataValue("enableTabindex", String.valueOf(settings.isEnableTabindexSelected()));
		content.setMetadataValue("sortRightToLeft", String.valueOf(settings.isSortRightToLeftSelected()));

		this.appController.initEditorOptions();
		this.appController.saveContent();
	}

}
