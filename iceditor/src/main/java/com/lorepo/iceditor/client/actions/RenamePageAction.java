package com.lorepo.iceditor.client.actions;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icf.widgets.EditValueDialog;
import com.lorepo.icplayer.client.model.page.Page;

public class RenamePageAction extends AbstractAction{

	private EditValueDialog dlg;
	
	public RenamePageAction(AppController controller) {
		super(controller);
	}

	@Override
	public void execute() {
		final Page page = getServices().getAppController().getCurrentPage();
		
		dlg = new EditValueDialog(DictionaryWrapper.get("rename_page"), DictionaryWrapper.get("name"));
		dlg.getTextBox().setText(page.getName());
		
		dlg.getSaveButton().addClickHandler(new ClickHandler() {
			
			@Override
			public void onClick(ClickEvent event) {
	
				String name = dlg.getTextBox().getText();
				page.setName(name);
				dlg.hide();
				getServices().getAppController().saveContent();
			}
		});
		
		dlg.show();
	}

}
