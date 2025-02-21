package com.lorepo.iceditor.client.ui.widgets.modals.semi.responsive;

import com.lorepo.icf.screen.DeviceOrientation;

public class PageLayoutData {
	public String name;
	public String treshold;
	public boolean useDeviceOrientation;
	public DeviceOrientation deviceOrientation;
	
	public PageLayoutData (String name, String treshold, boolean useDeviceOrientation, DeviceOrientation deviceOrientation) {
		this.name = name;
		this.treshold = treshold;
		this.useDeviceOrientation = useDeviceOrientation;
		this.deviceOrientation = deviceOrientation;
	}
}
