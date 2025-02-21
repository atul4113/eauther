package com.lorepo.iceditor.client.actions.patchers;

import org.mockito.Mockito;

import com.google.gwt.core.client.JavaScriptObject;
import com.googlecode.gwt.test.patchers.PatchClass;
import com.googlecode.gwt.test.patchers.PatchMethod;
import com.lorepo.iceditor.client.actions.InsertAddonAction;

@PatchClass(InsertAddonAction.class)
public class InsertAddonActionPatcher {
	
	@PatchMethod
	public static boolean isAddToDrag () {
		return false;
	}

}
