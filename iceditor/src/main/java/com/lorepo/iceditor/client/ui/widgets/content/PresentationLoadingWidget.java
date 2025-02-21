package com.lorepo.iceditor.client.ui.widgets.content;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.DivElement;
import com.google.gwt.dom.client.Style.Display;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;

import static com.google.gwt.query.client.GQuery.$;

public class PresentationLoadingWidget extends Composite {

	private static PresentationLoadingWidgetUiBinder uiBinder = GWT
			.create(PresentationLoadingWidgetUiBinder.class);

	interface PresentationLoadingWidgetUiBinder extends
			UiBinder<Widget, PresentationLoadingWidget> {
	}
	
	@UiField HTMLPanel panel;
	@UiField DivElement logoLoading;

	public PresentationLoadingWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		
		panel.getElement().setId("presentationLoadingPage");
		logoLoading.setId("mAuthorLogoLoading");
	}

	public void show() {
		panel.getElement().getStyle().setDisplay(Display.BLOCK);
		WidgetLockerController.show();
	}
	
	public static native void hide() /*-{
		function onWindowLoaded() {
			$wnd.$('#presentationLoadingPage').css('display', 'none');
			$wnd.iceHideWidgetLocker();
		}

		// We're waiting for window.loaded event because some of the JavaScript (main.js)
		// functionalities (like f.e. hovered menu) is initialized after it.
		if ($doc.readyState == "complete") {
			onWindowLoaded();
			return;
		}

		$wnd.$($wnd).load(function() {
			onWindowLoaded();
		});
	}-*/;
	
	public void setLoadingLogo(String url) {
		logoLoading.getStyle().setProperty("background", "url("+ url + ") no-repeat");
		logoLoading.getStyle().setProperty("background-size", "220px 75px");
		logoLoading.getStyle().setProperty("background-position", "center center");
	}
	
	public boolean isLoadingPresentationVisible() {
		return $(panel.getElement()).is(":visible");
	}
}
