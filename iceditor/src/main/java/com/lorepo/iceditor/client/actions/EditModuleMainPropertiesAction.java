package com.lorepo.iceditor.client.actions;

import com.google.gwt.core.client.JavaScriptObject;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.widgets.content.PresentationWidget;
import com.lorepo.iceditor.client.ui.widgets.modules.ModulesWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.PropertiesWidget;
import com.lorepo.icplayer.client.module.api.IModuleModel;

public class EditModuleMainPropertiesAction extends AbstractPageAction{
	private String moduleID;
	private AppController appController;
	
	public EditModuleMainPropertiesAction(AppController controller) {
		super(controller);
		this.appController = controller;
	}
	
	static class Dimensions extends JavaScriptObject {
		protected Dimensions() {}

		public final native int getLeft() /*-{ return this.left; }-*/;
		public final native int getTop() /*-{ return this.top; }-*/;
		public final native int getWidth() /*-{ return this.width; }-*/;
		public final native int getHeight() /*-{ return this.height; }-*/;
	}
	
	private static native Dimensions getDimensions(int left, int top, int width, int height) /*-{
		function parseValue(value, defaultValue) {
			if (isNaN(parseInt(value, 10))) {
				return defaultValue;
			} else {
				return parseInt(value, 10);
			}
		};

		var $module =  $wnd.jQueryManager.getSelectedModule();
		
		return {left: parseValue($module.css('left'), left), top: parseValue($module.css('top'), top), width: parseValue($module.outerWidth(), width), height: parseValue($module.outerHeight(), height)};
	}-*/;
	
	private static native boolean compareDimensions(int left, int top, int width, int height, String moduleID) /*-{
		function parseValue(value) {
			var newValue = value.replace("px", "");
			return Math.round(newValue);
		};
		
		var $module =  $wnd.jQueryManager.getSelectedModule();

		$module.css({
			'left': left,
			'top': top,
			'width': width,
			'height': height
		});
		
		//This values are checked due to problems with rounding while page is zoomed
		if((parseValue($module.css('left')) - left) > 1 || (left - parseValue($module.css('left'))) > 1) return true;
		if((parseValue($module.css('top')) - top) > 1 || (top - parseValue($module.css('top'))) > 1) return true;
		if((parseValue($module.css('width')) - width) > 1 || (width - parseValue($module.css('width'))) > 1) return true;
		if((parseValue($module.css('height')) - height) > 1 || (height - parseValue($module.css('height'))) > 1) return true;
		
		return false;
	}-*/;
	
	public void execute(IModuleModel module) {
		AppFrame appFrame = getServices().getAppController().getAppFrame();
		PresentationWidget presentation = appFrame.getPresentation();
		PropertiesWidget properties = appFrame.getProperties();
		ModulesWidget modulesWidget = appFrame.getModules();
		
		if (module != null) {
			moduleID = module.getId();

			int left = module.getLeft();
			int top = module.getTop(); 
			int width = module.getWidth();
			int height = module.getHeight();

			boolean isImportantUsed = compareDimensions(left, top, width, height, moduleID);
			
			if (isImportantUsed) {
				Dimensions dimensions = getDimensions(left, top, width, height);

				properties.setNewDimensions(Integer.toString(dimensions.getHeight()), Integer.toString(dimensions.getWidth()), true);
				properties.setNewPosition(Integer.toString(dimensions.getLeft()), Integer.toString(dimensions.getTop()), null, null, true);
			}
			modulesWidget.refreshModulesList();
		}
		
		presentation.refreshView();
	}
}
