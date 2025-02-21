package com.lorepo.iceditor.client.utils.ui.styleeditor;

import com.lorepo.icplayer.client.framework.module.IStyledModule;

public class StyleEditorPresenterUtils {
	
	public static boolean shouldAddButtonClass(String className, String modulePrefix) {

		if (className.startsWith("button_")) {
			int pos = className.indexOf("_");
			className = className.substring(pos + 1);

			if (className.startsWith("go_to_page")) {
				className = className.replaceFirst("go_to_page", "gotopage");
			} else if (!className.startsWith("reset") && !className.startsWith("popup") && !className.startsWith("cancel")) {
				className = className.replaceFirst("_", "");
			}
			
			// For compatibility sake we allow 
			if (className.startsWith("prev") && !className.startsWith("previous")) {
				className = className.replaceAll("prev", "previous");
			} else if (className.startsWith("popup") && !className.startsWith("openpopup") && !className.startsWith("close")) {
				className = className.replaceAll("popup", "openpopup");
			} else if (className.startsWith("cancel")) {
				className = className.replaceAll("cancel", "closepopup");
			}
		}
		
		if (className.startsWith(modulePrefix+"_")) {
			return true;
		}

		return false;
	}
	
	public static String getModuleClassNamePrefix(IStyledModule module) {
		
		String prefix = module.getClassNamePrefix().toLowerCase();

		if (prefix.equals("popup")) {
			prefix = "openpopup";
		} else if (prefix.equals("cancel")) {
			prefix = "closepopup";
		} else if (prefix.equals("prevpage")) {
			prefix = "previouspage";
		}

		return prefix.replace(" ", "");
	}
}