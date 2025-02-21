package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.widgets.modals.QuestionModalListener;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;

public class ChangeRulerPositionAction extends AbstractPageAction {
	private AppFrame appFrame = getServices().getAppController().getAppFrame();

	public ChangeRulerPositionAction(AppController controller) {
		super(controller);
	}
	
	private static native void changeRulerPosition(String position, String value) /*-{
		$wnd.iceChangeRulerPosition(position, value);
	}-*/;
	
	public void execute(final String position, final String value) {
		String[] textContent = {"", "px", DictionaryWrapper.get("ruler_position")};
		
		appFrame.getModals().addPrompt(value, textContent, new QuestionModalListener() {
			@Override
			public void onDecline() {

			}
			
			@Override
			public void onAccept() {
				String promptValue = appFrame.getModals().getPromptValue();
				changeRulerPosition(position, promptValue);
			}
		});
	}
}
