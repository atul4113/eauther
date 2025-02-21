package com.lorepo.iceditor.client.semi.responsive.ui.widgets;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.SpanElement;
import com.google.gwt.event.logical.shared.ValueChangeEvent;
import com.google.gwt.event.logical.shared.ValueChangeHandler;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.icf.screen.DeviceOrientation;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;

public class SemiResponsiveOrientationDeviceSelectorWidget extends Composite {

	private static SemiResponsiveOrientationDeviceSelectorWidgetUiBinder uiBinder = GWT.create(SemiResponsiveOrientationDeviceSelectorWidgetUiBinder.class);

	interface SemiResponsiveOrientationDeviceSelectorWidgetUiBinder extends
			UiBinder<Widget, SemiResponsiveOrientationDeviceSelectorWidget> {
	}
	
	@UiField SpanElement useDeviceLabel;
	@UiField SpanElement orientationLabel;
	
	@UiField CheckBox useDeviceOrientation;
	@UiField DeviceOrientationWidget deviceOrientation;
	
	public SemiResponsiveOrientationDeviceSelectorWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		this.updateElementsText();
		this.connectHandlers();
		this.blockDeviceOrientation();
	}

	private void connectHandlers() {
		this.useDeviceOrientation.addValueChangeHandler(new ValueChangeHandler<Boolean>() {
			@Override
			public void onValueChange(ValueChangeEvent<Boolean> event) {
				if (event.getValue()) {
					unblockDeviceOrientation();
				} else {
					blockDeviceOrientation();
				}
			}
		});
	}
	
	public boolean getUseDeviceOrientation() {
		return this.useDeviceOrientation.getValue();
	}
	
	public DeviceOrientation getDeviceOrientation() {
		return this.deviceOrientation.getOrientation();
	}
	
	public void setUseDeviceOrientation(boolean useDeviceOrientation) {
		this.useDeviceOrientation.setValue(useDeviceOrientation);
		if (useDeviceOrientation) {
			this.unblockDeviceOrientation();
		} else {
			this.blockDeviceOrientation();
		}
	}
	
	public void setDeviceOrientation(DeviceOrientation deviceOrientation) {
		this.deviceOrientation.setValue(deviceOrientation);
	}
	
	private void blockDeviceOrientation () {
		this.deviceOrientation.getElement().getFirstChildElement().setAttribute("disabled", "disabled");
	}
	
	private void unblockDeviceOrientation () {
		this.deviceOrientation.getElement().getFirstChildElement().removeAttribute("disabled");
	}

	private void updateElementsText() {
		this.useDeviceLabel.setInnerText(DictionaryWrapper.get("semi_responsive_use_device_orientation_in"));
		this.orientationLabel.setInnerText(DictionaryWrapper.get("semi_responsive_orientation"));
	}
}
