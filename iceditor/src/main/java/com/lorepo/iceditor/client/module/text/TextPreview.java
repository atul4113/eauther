package com.lorepo.iceditor.client.module.text;

import com.google.gwt.event.logical.shared.AttachEvent;
import com.google.gwt.event.logical.shared.AttachEvent.Handler;
import com.google.gwt.regexp.shared.MatchResult;
import com.google.gwt.regexp.shared.RegExp;
import com.google.gwt.user.client.DOM;
import com.google.gwt.dom.client.Element;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.icplayer.client.module.text.GapInfo;
import com.lorepo.icplayer.client.module.text.InlineChoiceInfo;
import com.lorepo.icplayer.client.module.text.TextModel;
import com.lorepo.icplayer.client.module.text.TextView;

public class TextPreview extends Composite{

	private TextModel module;
	

	public TextPreview(TextModel module) {
		this.module = module;
		initWidget(getView());
	}
	
	
	private Widget getView() {
	
		TextView view = new TextView(module, true);
		String parsedText = module.getParsedText();
		if (module.hasMathGaps()) {
			String gapId = module.getGapUniqueId();
			String stringPattern = "\\{" + gapId + "-([\\d+])\\|";
			RegExp pattern = RegExp.compile(stringPattern, "g");
			
			MatchResult match = pattern.exec(parsedText);
			while(match instanceof MatchResult) {
				String counter = match.getGroup(1);
				parsedText = parsedText.replaceAll("\\{" + gapId + "-" + counter + "\\|", "{editor-" + gapId + "-" + counter + "|");
				match = pattern.exec(parsedText);
			}
		}
		parsedText = parsedText.replaceAll("id=\"", "id=\"editor-");
		
		view.setHTML(parsedText);
		
		if(module.getGapWidth() > 0){
		
			view.addAttachHandler(new Handler() {
				
				@Override
				public void onAttachOrDetach(AttachEvent event) {
					if(event.isAttached()){
						resizeGaps();
					}
				}
			});
			
		}
		
		return view;
	}


	protected void resizeGaps() {

		Element gapElement;
		String width = module.getGapWidth() + "px";

		if (!module.hasMathGaps()) {
			for(GapInfo gap : module.gapInfos){
				gapElement = DOM.getElementById("editor-"+gap.getId());
				gapElement.getStyle().setProperty("width", width);
			}
		}

		for(InlineChoiceInfo choice : module.choiceInfos){
			gapElement = DOM.getElementById("editor-"+choice.getId());
			gapElement.getStyle().setProperty("width", width);
		}

	}
}
