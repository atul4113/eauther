package com.lorepo.iceditor.client.actions;

import java.util.HashMap;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.semi.responsive.SemiResponsiveModificationsHistory;
import com.lorepo.iceditor.client.ui.widgets.modals.QuestionModalListener;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationType;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.CssStyle;
import com.lorepo.icplayer.client.model.layout.PageLayout;

public class DeleteSemiResponsiveLayoutAction extends SemiResponsiveAbstractAction {
	private String layoutID;

	public DeleteSemiResponsiveLayoutAction(AppController controller) {
		super(controller);
	}
	
	public void setPageLayoutID(String layoutID) {
		this.layoutID = layoutID;
	}
	
	public void execute() {
		if (this.layoutToDeleteIsDefault()) {
			this.showInformationThatDefaultCantBeDeleted();
		} else {
			this.performDelete();	
		}
	}

	private void showInformationThatDefaultCantBeDeleted() {
		String message = DictionaryWrapper.get("delete_semi_responsive_layout_warning_default_cant_be_deleted");
		getNotifications().addMessage(message, NotificationType.warning, false);
	}

	private void performDelete() {
		String question = DictionaryWrapper.get("delete_semi_responsive_layout_question");
		this.getModals().addModal(question, new QuestionModalListener() {
			
			@Override
			public void onDecline() {}
			
			@Override
			public void onAccept() {
				try {
					deleteLayoutAndItsCssStyle();
					syncCurrentSemiResponsiveLayouts();
					setDefaultSemiResponsiveLayoutAsCurrent();
					getNotifications().addMessage(DictionaryWrapper.get("delete_semi_responsive_layout_success"), NotificationType.success, false);
					refreshSemiResponsiveEditingWidgets();
				} catch (IllegalArgumentException e) {
					getNotifications().addMessage(e.getMessage(), NotificationType.error, true);
				}
			}
		});
	}

	private boolean layoutToDeleteIsDefault() {
		Content model = this.getModel();
		HashMap<String, PageLayout> layouts = model.getLayouts();
		PageLayout pageLayout = layouts.get(this.layoutID);
		return pageLayout.isDefault();
	}

	private void deleteLayoutAndItsCssStyle() {
		Content contentModel = this.getModel();
		HashMap<String, PageLayout> layouts = contentModel.getLayouts();
		
		if (layouts.size() <= 1) {
			throw new IllegalArgumentException(DictionaryWrapper.get("delete_semi_responsive_layout_error_not_enough_layouts"));
		}
		
		Boolean notFound = false;
		String cssStyleID = "";
		for (PageLayout pageLayout : layouts.values()) {
			if (pageLayout.getID() == this.layoutID) {
				cssStyleID = pageLayout.getStyleID();
				layouts.remove(pageLayout.getID());
				contentModel.setSemiResponsiveLayouts(layouts);
				notFound = false;
				break;
			}
		}
		
		if (notFound) {
			throw new IllegalArgumentException(DictionaryWrapper.get("delete_semi_responsive_layout_error_does_not_exists"));	
		}
		
		
		HashMap<String, CssStyle> styles = contentModel.getStyles();
		styles.remove(cssStyleID);
		contentModel.setStyles(styles);
		SemiResponsiveModificationsHistory.removeSemiResponsiveLayout(this.layoutID);
	}
}