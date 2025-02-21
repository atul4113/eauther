package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.widgets.content.PresentationWidget;
import com.lorepo.iceditor.client.ui.widgets.modals.QuestionModalListener;
import com.lorepo.iceditor.client.ui.widgets.properties.PropertiesWidget;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.page.Page;

public class ChangePageHeightAction extends AbstractAction{
	private int clickPosition;
	private AppFrame appFrame = getServices().getAppController().getAppFrame();
	
	public ChangePageHeightAction(AppController controller) {
		super(controller);
	}

	@Override
	public void execute() {
		String[] textContent = {"amount", "", DictionaryWrapper.get("outstretch_height")};
		
		appFrame.getModals().addPrompt("", textContent, new QuestionModalListener() {
			@Override
			public void onDecline() {

			}
			
			@Override
			public void onAccept() {
				changePageHeight();
				appFrame.getPresentation().refreshView();
			}
		});
	}
	
	private static native int getPageHeight() /*-{
		return $wnd.$(".ic_main").height();
	}-*/;
	
	protected void changePageHeight() {
		PresentationWidget presentation = appFrame.getPresentation();
		Page page = getServices().getAppController().getCurrentPage();
		PropertiesWidget properties = appFrame.getProperties();
		String promptValue = appFrame.getModals().getPromptValue().trim();
		int value = 0;
		int pageHeight = page.getHeight();

		if (pageHeight == 0) {
			pageHeight = getPageHeight();
		}

		if (!promptValue.equals("")) {
			value = Integer.parseInt(promptValue);
		}

		int increasedHeight = pageHeight + value;

		if(increasedHeight > 0) {
			page.setHeight(increasedHeight);
			page.outstreachHeight(clickPosition, value);
			properties.setPage(page);
			getServices().getAppController().saveCurrentPageAndContent();
			getServices().getAppController().getUndoManager().add(page.toXML());
			presentation.refreshView();
		}
		else{
			getServices().showMessage(DictionaryWrapper.get("page_height_size_message"));
		}
	}

	public void setPosition(int position){
		clickPosition = position;
	}
}
