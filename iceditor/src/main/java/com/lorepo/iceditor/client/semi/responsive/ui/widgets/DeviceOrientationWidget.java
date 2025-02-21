package com.lorepo.iceditor.client.semi.responsive.ui.widgets;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.icf.screen.DeviceOrientation;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;

public class DeviceOrientationWidget extends Composite {

	private static DeviceOrientationWidgetUiBinder uiBinder = GWT.create(DeviceOrientationWidgetUiBinder.class);
	
	@UiField ListBox deviceOrientationList;
	
	interface DeviceOrientationWidgetUiBinder extends
			UiBinder<Widget, DeviceOrientationWidget> {
	}

	public DeviceOrientationWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		this.deviceOrientationList.addItem(DictionaryWrapper.get("orientation_type_vertical"), DeviceOrientation.vertical.toString());
		this.deviceOrientationList.addItem(DictionaryWrapper.get("orientation_type_horizontal"), DeviceOrientation.horizontal.toString());
	}
	
	public DeviceOrientation getOrientation() {
		int index = this.deviceOrientationList.getSelectedIndex();
		String value = this.deviceOrientationList.getValue(index);
		
		return DeviceOrientation.valueOf(value);
	}

	public void setValue(DeviceOrientation deviceOrientation) {
		if (deviceOrientation == DeviceOrientation.vertical) {
			this.deviceOrientationList.setSelectedIndex(0);
		} else {
			this.deviceOrientationList.setSelectedIndex(1);			
		}
	}
}
