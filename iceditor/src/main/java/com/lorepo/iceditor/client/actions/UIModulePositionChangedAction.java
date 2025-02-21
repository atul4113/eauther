package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.widgets.properties.PropertiesWidget;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.model.page.group.Group;
import com.lorepo.icplayer.client.module.api.IModuleModel;

public class UIModulePositionChangedAction extends AbstractPageAction{
	public UIModulePositionChangedAction(AppController controller) {
		super(controller);
	}

	/**
	 * Save new module position calculated from JavaScript into content (XML).
	 * 
	 * If module doesn't have relative position set to any other modules, strict CSS position values will be passed.
	 * IF module is relative in its position to another, relative position will be passed. We assume here that passed values
	 * are those set in content (XML).
	 * 
	 * @param deltaLeft new position value in pixels, regardless of fact if module is relative to other or not in its position
	 * @param deltaTop new position value in pixels, regardless of fact if module is relative to other or not in its position
	 * @param submit
	 */

	public void execute(String moduleID, String deltaLeft, String deltaTop, String deltaRight, String deltaBottom, boolean submit, boolean addToHisory) {
		AppFrame appFrame = getServices().getAppController().getAppFrame();
		PropertiesWidget properties = appFrame.getProperties();
		IModuleModel module = getServices().getAppController().getCurrentPage().getModules().getModuleById(moduleID);
		Group group = getServices().getAppController().getCurrentPage().getGroupById(moduleID);

		
		if (module != null) {

			int left = module.getLeft() + (deltaLeft == null ? 0 : Integer.valueOf(deltaLeft));
			int top = module.getTop() + (deltaTop == null ? 0 : Integer.valueOf(deltaTop));
			int right = module.getRight() + (deltaRight == null ? 0 : Integer.valueOf(deltaRight));
			int bottom = module.getBottom() + (deltaBottom == null ? 0 : Integer.valueOf(deltaBottom));

			String leftValue = deltaLeft != null ? Integer.toString(left) : null;
			String topValue = deltaTop != null ? Integer.toString(top) : null;
			String rightValue = deltaRight != null ? Integer.toString(right) : null;
			String bottomValue = deltaBottom != null ? Integer.toString(bottom) : null;

			if (properties.isModuleSet()) {
				properties.setNewPosition(leftValue, topValue, rightValue, bottomValue, submit);
			}

			if (submit) {
				if (deltaLeft != null) {
					module.setLeft(left);
				}

				if (deltaTop != null) {
					module.setTop(top);
				}

				if (deltaRight != null) {
					module.setRight(right);
				}

				if (deltaBottom != null) {
					module.setBottom(bottom);
				}
			}

		}

		if(group != null&&group.isDiv()) {
			int left = deltaLeft == null ? 0 : Integer.valueOf(deltaLeft);
			int top = deltaTop == null ? 0 : Integer.valueOf(deltaTop);
			group.setLeft(left);
			group.setTop(top);
		}

		if(addToHisory) {
				IAppController appController = getServices().getAppController();
				Page page = getServices().getAppController().getCurrentPage();
				appController.getUndoManager().add(page.toXML());
		}
	}
}