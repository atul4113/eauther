package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.widgets.content.PresentationWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.PropertiesWidget;
import com.lorepo.icplayer.client.module.api.IModuleModel;

public class UIModuleDimensionsChangedAction extends AbstractPageAction{
	public UIModuleDimensionsChangedAction(AppController controller) {
		super(controller);
	}

	public void execute(String height, String width, String deltaLeft, String deltaTop, String deltaRight, String deltaBottom, boolean submit) {
		int roundedHeight = (int) Math.round(Double.parseDouble(height));
		int roundedWidth = (int) Math.round(Double.parseDouble(width));
		height = Integer.toString(roundedHeight);
		width = Integer.toString(roundedWidth);		
		
		AppFrame appFrame = getServices().getAppController().getAppFrame();
		PresentationWidget presentation = appFrame.getPresentation();
		PropertiesWidget properties = appFrame.getProperties();
		IModuleModel module = getServices().getAppController().getSelectionController().getSelectedModules().next();
		
		if (module == null) {
			return;
		}
		
		if (module != null && !properties.isModuleSet() && submit) {
			properties.setModule(module);
		}

		//if top and bottom OR left and right are null, height or width will be set from layout
		if (deltaTop != null && deltaBottom != null) {
			height = null;
		}
		
		if (deltaLeft != null && deltaRight != null) {
			width = null;
		}

		int left = (int) (Math.round(module.getLeft()) + Math.round(Double.valueOf(deltaLeft != null ? deltaLeft : "0")));
		int top = (int) (Math.round(module.getTop()) + Math.round(Double.valueOf(deltaTop != null ? deltaTop : "0")));
		int right = (int) (Math.round(module.getRight()) + Math.round(Double.valueOf(deltaRight != null ? deltaRight : "0")));
		int bottom = (int) (Math.round(module.getBottom()) + Math.round(Double.valueOf(deltaBottom != null ? deltaBottom : "0")));

		String leftValue = deltaLeft != null ? Integer.toString(left) : null;
		String topValue = deltaTop != null ? Integer.toString(top) : null;
		String rightValue = deltaRight != null ? Integer.toString(right) : null;
		String bottomValue = deltaBottom != null ? Integer.toString(bottom) : null;
		
		properties.setNewPosition(leftValue, topValue, rightValue, bottomValue, submit);
		properties.setNewDimensions(height, width, submit);

		if(module != null && submit) {
			presentation.refreshView();
		}
	}
}