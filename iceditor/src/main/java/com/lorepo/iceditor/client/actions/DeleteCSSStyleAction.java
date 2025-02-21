package com.lorepo.iceditor.client.actions;

import java.util.HashMap;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.widgets.modals.QuestionModalListener;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationType;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.CssStyle;

public class DeleteCSSStyleAction extends SemiResponsiveAbstractAction {
	private AppFrame appFrame = getServices().getAppController().getAppFrame();
	private CssStyle styleToDelete;

	public DeleteCSSStyleAction(AppController controller) {
		super(controller);
	}
	
	public void setStyleToDelete(CssStyle styleToDelete) {
		this.styleToDelete = styleToDelete;
	}
	
	@Override
	public void execute() {
		String question = DictionaryWrapper.get("delete_css_style_question");
		appFrame.getModals().addModal(question, new QuestionModalListener() {
			
			@Override
			public void onDecline() {}
			
			@Override
			public void onAccept() {
				try {
					deleteStyle(styleToDelete);
					refreshSemiResponsiveEditingWidgets();
					refreshCurrentCssStyleOnly();
				} catch (IllegalArgumentException e) {
					getNotifications().addMessage(e.getMessage(), NotificationType.error, true);
				}
			}
		});
	}
	
	public void setStyleToDelete(String styleID) {
		Content contentModel = this.getModel();
		this.setStyleToDelete(contentModel.getStyle(styleID));
	}
	
	private void deleteStyle(CssStyle styleToDelete) {
		Content contentModel = this.getModel();
		HashMap<String, CssStyle> styles = contentModel.getStyles();
		
		if (styles.size() <= 1) {
			throw new IllegalArgumentException(DictionaryWrapper.get("delete_style_error_not_enough_styles_to_delete"));
		}
		
		if (!styles.containsKey(styleToDelete.getID())) {
			throw new IllegalArgumentException(DictionaryWrapper.get("delete_style_error_style_does_not_exists"));
		}
		
		CssStyle styleToDeleteFromContent = styles.get(styleToDelete.getID());
		
		if (styleToDeleteFromContent.isDefault()) {
			throw new IllegalArgumentException(DictionaryWrapper.get("delete_style_error_style_is_default"));
		}
		
		styles.remove(styleToDeleteFromContent.getID());
		contentModel.setStyles(styles);
		contentModel.removeFromLayoutsStyle(styleToDelete);
	}
}
