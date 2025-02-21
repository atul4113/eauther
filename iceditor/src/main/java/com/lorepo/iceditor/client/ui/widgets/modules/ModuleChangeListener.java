package com.lorepo.iceditor.client.ui.widgets.modules;

public interface ModuleChangeListener {
	void onSelected(boolean isCtrlPressed, boolean isShiftPressed);
	void onLockedChanged(boolean isLocked);
	void onVisibilityChanged(boolean isVisible);
}
