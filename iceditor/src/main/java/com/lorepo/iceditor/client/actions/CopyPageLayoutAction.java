package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.semi.responsive.CopyPageLayoutTask;
import com.lorepo.iceditor.client.ui.widgets.modals.QuestionModalListener;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.page.Page;


public class CopyPageLayoutAction extends AbstractAction {	
	
	public CopyPageLayoutAction(AppController controller) {
		super(controller);
	}
	
	public void execute(final String newSourceLayoutID) {

		getAppFrame().getProperties().getLayoutsCopier().refreshList();
		String sourceLayoutName = this.getAppController().getModel().getLayouts().get(newSourceLayoutID).getName();
		
		this.getModals().addModal(DictionaryWrapper.get("copy_page_layout_question") + sourceLayoutName, new QuestionModalListener() {
			
			@Override
			public void onDecline() {}
			
			@Override
			public void onAccept() {
				copyPageLayout(newSourceLayoutID);
			}
			
		});
		
	}
	
	private void copyPageLayout(String sourceLayoutID) {
		
		Content model = this.getModel();
		Page page = this.getCurrentPage();
		String targetLayoutID = model.getActualSemiResponsiveLayoutID();
		
		CopyPageLayoutTask task = new CopyPageLayoutTask();
		task.execute(page, sourceLayoutID, targetLayoutID);
		
		getAppController().saveCurrentPageAndContent();
		getAppController().getUndoManager().add(page.toXML());
		
		this.getAppFrame().getStyles().refresh();
		this.refreshView();
		
	}
	
}
