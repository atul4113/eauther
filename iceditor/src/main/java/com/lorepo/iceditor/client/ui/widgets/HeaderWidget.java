package com.lorepo.iceditor.client.ui.widgets;

import static com.google.gwt.query.client.GQuery.$;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.AnchorElement;
import com.google.gwt.dom.client.DivElement;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;

public class HeaderWidget extends Composite {

	private static HeaderWidgetUiBinder uiBinder = GWT
			.create(HeaderWidgetUiBinder.class);

	interface HeaderWidgetUiBinder extends UiBinder<Widget, HeaderWidget> {
	}
	
	@UiField DivElement lessonTitle;
	@UiField DivElement subTitle;
	@UiField DivElement logo;
	@UiField AnchorElement expand;

	public HeaderWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		
		lessonTitle.setId("lessonTitle");
		logo.setId("mAuthorLogo");
		expand.setId("additionalHeaderItemsExpandBtn");
		
		updateElementsText();
	}
	
	public void setTitle(String title) {
		this.lessonTitle.setInnerHTML(title);
	}
	
	public void setSubTitle(String subTitle) {
		if (subTitle.isEmpty()) {
			$(subTitle).hide();
			$(expand).hide();
			
			return;
		}

		this.subTitle.setInnerHTML(subTitle);
	}

	public void setTemplateName(String templateName) {
		$(subTitle).find("#spaceName").text(templateName);
	}
	
	public void updateElementsText() {
		lessonTitle.setInnerText(DictionaryWrapper.get("presentation_title"));
	}
	
	public void setImageLogo(String url) {
		logo.getStyle().setProperty("background", "url("+ url + ")");
		logo.getStyle().setProperty("background-size", "105px 36px");
	}
}
