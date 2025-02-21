package com.lorepo.iceditor.client.ui.widgets.content;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.Document;
import com.google.gwt.dom.client.IFrameElement;
import com.google.gwt.dom.client.Style.Display;
import com.google.gwt.dom.client.Style.Overflow;

import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.ui.widgets.utils.MainPageUtils;

public class PreviewWidget extends Composite {

	private static PreviewWidgetUiBinder uiBinder = GWT.create(PreviewWidgetUiBinder.class);

	interface PreviewWidgetUiBinder extends UiBinder<Widget, PreviewWidget> {
	}

	@UiField
	HTMLPanel panel;
	@UiField
	HTMLPanel contents;
	private IFrameElement frame;
	private String previewURL;
	private String layoutId;

	public PreviewWidget() {
		initWidget(uiBinder.createAndBindUi(this));

		panel.getElement().getStyle().setDisplay(Display.NONE);
		panel.getElement().setId("previewPage");

		contents.getElement().setId("previewPage-contents");
	}

	public native void handleStaticFooterAndHeader() /*-{
		var $iframe = $wnd.$('#lesson-iframe');
		var iframeWindow = $iframe[0].contentWindow
				|| $iframe[0].contentDocument;

		var id = this.@com.lorepo.iceditor.client.ui.widgets.content.PreviewWidget::layoutId;
		function onMessageReceived(event) {
			if (event.data.indexOf('RESIZE:') === 0
					&& !$wnd.isStretchOrFullScreenMode) {
				var height = parseInt($iframe.css('height'), 10);
				postIFrameMessage(height, $wnd.$("#previewPage-contents")
						.scrollTop());
			} else if (event.data.indexOf('PAGE_LOADED') === 0) {
				$wnd.$("#previewPage-contents").scrollTop(0);
				var height = parseInt($iframe.css('height'), 10);
				postIFrameMessage(height);
			} else if (event.data.indexOf('GET_ACTUAL_ID') === 0) {
				postIFrameMessageSelectID(id);
			}

		}

		function postIFrameMessageSelectID(layoutId) {
			var jsonObject = {
				id : layoutId,
			};
			iframeWindow.postMessage('SET_ACTUAL_ID:'
					+ JSON.stringify(jsonObject), '*');
		}

		function postIFrameMessage(height, scroll) {
			var scroll = scroll ? scroll
					: ($wnd.pageYOffset || $doc.documentElement.scrollTop);

			var postObject = {
				offsetTop : scroll,
				height : height,
				frameOffset : 119,
				notScaledOffset : 119,
				windowInnerHeight : $wnd.innerHeight || 0,
				isEditorPreview : true
			};

			iframeWindow.postMessage('I_FRAME_SIZES:'
					+ JSON.stringify(postObject), '*');
		}
		$wnd.addEventListener('message', onMessageReceived, false);

		$wnd.addEventListener('scroll', function(event) {
			var height = parseInt($iframe.css('height'), 10);
			postIFrameMessage(height);
		});

		$wnd.onresize = function() {
			var height = parseInt($iframe.css('height'), 10);
			postIFrameMessage(height);
		};

		$wnd.$("#previewPage-contents").on('scroll', function() {
			var height = parseInt($iframe.css('height'), 10);
			postIFrameMessage(height, $wnd.$(this).scrollTop());
		});

		$wnd.$("#previewPage-contents").scrollTop(0);
	}-*/;

	public void setIdLayout(String id) {
		layoutId = id;
	}

	public void show() {
		MainPageUtils.show(panel);

		frame = Document.get().createIFrameElement();
		frame.getStyle().setOverflow(Overflow.HIDDEN);
		frame.setAttribute("scrolling", "no");
		frame.setSrc(previewURL);
		frame.setId("lesson-iframe");

		contents.getElement().appendChild(frame);
		this.handleStaticFooterAndHeader();
	}

	public void hide() {
		panel.getElement().getStyle().setDisplay(Display.NONE);
		WidgetLockerController.hide();

		contents.getElement().removeChild(frame);
		frame = null;

	}

	public void setURL(String previewURL) {
		this.previewURL = previewURL;
	}
}
