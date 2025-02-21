package com.lorepo.iceditor.client.ui.widgets.utils;

import com.lorepo.iceditor.client.ui.widgets.properties.BooleanPropertyWidget;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.module.text.TextParser;

import java.util.Arrays;
import java.util.List;

public class GapsParserUtil {	
	public static String render(String srcText) {
		TextParser parser = new TextParser();
		
		if (isKeepOrder()) {
			parser.setKeepOriginalOrder(true);
		}

		return parser.parse(srcText, true).parsedText;
	}
	
	public static String renderItemsEditor(String srcText) {
		return !isRenderedView() ? srcText : render(srcText);
	}
	
	public static List<String> getEditableGaps(String text) {
		String result = "";

		result = text.replace("\\gap{", "");
		result = result.substring(0, result.length() - 1);

		return Arrays.asList(result.split("\\|"));
	}

	public static List<String> getFilledGaps(String text) {
		String result = "";
		
		result = text.replace("\\filledGap{", "");
		result = result.substring(0, result.length() - 1);
		
		return Arrays.asList(result.split("\\|"));
	}
	
	public static List<String> getDropdownGaps(String text) {
		String result = text.substring(2, text.length() - 2);

		result = TextParser.escapeAltText(result);
		String[] resultArray = result.split("\\|");
		for(int i = 0; i<resultArray.length;i++) {
			resultArray[i] = TextParser.unescapeAltText(resultArray[i]);
		}
		return Arrays.asList(resultArray);
	}

	public static boolean isKeepOrder() {
		BooleanPropertyWidget keepOriginalProperty = (BooleanPropertyWidget) MainPageUtils.appFrame.getProperties().getModuleProperties().get(DictionaryWrapper.get("Keep_original_order"));

		if (keepOriginalProperty == null) {
			return false;
		}

		return keepOriginalProperty.getValue();
	}
	
	public static boolean isRenderedView() {
		return MainPageUtils.appFrame.getItemsEditor().isRenderMode();
	}
	
	public static boolean isVisible() {
		return MainPageUtils.appFrame.getItemsEditor().isVisible();
	}
	
	public static native String unwrapGaps(String text) /*-{
		text = "<div>" + text + "</div>";
		
		function replaceWithGapDef(items) {
			$_.each(items, function(i, el) {
				$_(el).replaceWith($_(el).attr("data-gap-value"));
			});	
		}
		
		var html = $wnd.$("<div/>").html(text).contents(),
			syntax = "",
			$_ = $wnd.$,
			items = html.find("input[data-gap]");
			link_items = html.find("a[data-gap]");

		replaceWithGapDef(items);
		replaceWithGapDef(link_items);

		return html.html();
	}-*/;
}