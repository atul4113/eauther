package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.actions.api.IActionService;
import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.page.PageList;

public class AddChapterAction extends AbstractAction{

	public AddChapterAction(IActionService service) {
		super(service);
	}

	@Override
	public void execute() {
		IAppController appController = getServices().getAppController();
		PageList rootChapter = getCurrentChapter();
		
		if (rootChapter == getModel().getCommonPages()) {
			return;
		}

		PageList chapter = new PageList(DictionaryWrapper.get("new_chapter_name"));
		rootChapter.add(chapter);
		appController.saveContent();
		
		appController.getAppFrame().getPages().refresh();
		getServices().getAppController().getAppFrame().getPages().selectChapter(chapter);
	}

}
