package com.lorepo.iceditor.client.actions;

import java.util.HashMap;

import com.google.gwt.user.client.Timer;
import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.widgets.content.EditCSSWidget;
import com.lorepo.iceditor.client.ui.widgets.content.MainPageEventListener;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationType;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.CssStyle;

public class EditCSSAction extends AbstractAction{
	final EditCSSWidget editCSS = getServices().getAppController().getAppFrame().getEditCSS();

	public EditCSSAction(AppController controller) {
		super(controller);
	}

	@Override
	public void execute() {
		Content content = getModel();
		HashMap<String, CssStyle> styles = content.getStyles();
		
		editCSS.setStyles(styles);
		editCSS.setActualStyleID(content.getActualSemiResponsiveLayoutID());
		
		editCSS.setListener(new MainPageEventListener() {
			@Override
			public void onSave() {
				runSaveCSS();
				editCSS.hide();
			}
			
			@Override
			public void onApply() {
				runSaveCSS();
			}
		});
		
		editCSS.show();
	}
	
	private void runSaveCSS() {
		getServices().getAppController().getAppFrame().getNotifications().addMessage(DictionaryWrapper.get("saving_css"), NotificationType.notice, false);
		// saving large CSS might cause the editor to momentarily slow down
		// Without the timeout saving_css notification would only appear once the file was already saved
		Timer t = new Timer() {
	      @Override
	      public void run() {
	    	  saveCSS();
	      }
	    };
	    t.schedule(50);
	}

	private void saveCSS() {
		IAppController appController = getServices().getAppController();
		HashMap<String, CssStyle> styles = editCSS.getStyles();

		
		getServices().getModel().setStyles(styles);

		Content content = getModel();
		String actualStyle = content.getActualStyle();
		
		appController.getAppFrame().getStyles().setCSS(actualStyle);
		appController.getAppFrame().getStyles().refresh();
	
		appController.refreshStyles(actualStyle);
		appController.setIsSavingStyles(true);
    	appController.saveContent();
	}

}
