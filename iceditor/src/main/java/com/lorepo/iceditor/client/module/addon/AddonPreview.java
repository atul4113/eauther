package com.lorepo.iceditor.client.module.addon;

import java.util.Iterator;
import java.util.List;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.event.logical.shared.AttachEvent;
import com.google.gwt.event.logical.shared.AttachEvent.Handler;
import com.google.gwt.dom.client.Element;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.module.api.IEditorServices;
import com.lorepo.icf.properties.IEditableSelectProperty;
import com.lorepo.icf.properties.IHtmlProperty;
import com.lorepo.icf.properties.IListProperty;
import com.lorepo.icf.properties.IProperty;
import com.lorepo.icf.properties.IPropertyProvider;
import com.lorepo.icf.properties.IStaticListProperty;
import com.lorepo.icf.properties.IStaticRowProperty;
import com.lorepo.icf.utils.JavaScriptUtils;
import com.lorepo.icplayer.client.framework.module.StyleUtils;
import com.lorepo.icplayer.client.module.addon.AddonModel;
import com.lorepo.icplayer.client.module.api.player.IAddonDescriptor;
import com.lorepo.icplayer.client.module.text.GapInfo;
import com.lorepo.icplayer.client.module.text.InlineChoiceInfo;
import com.lorepo.icplayer.client.module.text.TextParser;
import com.lorepo.icplayer.client.module.text.TextParser.ParserResult;

public class AddonPreview extends Composite{

	protected static AddonPreview addonPreview = null;
	private AddonModel module;
	private IAddonDescriptor addonDescriptor;
	private String previewHTML;
	private JavaScriptObject presenterObject;
	private JavaScriptObject jsModel;

	public AddonPreview(AddonModel module, IEditorServices services) {
		this.module = module;
		this.addonDescriptor = services.getContent().getAddonDescriptor(module.getAddonId());
		initJavaScriptObjects();
		initWidget(getView());
		addonPreview = this;
	}


	private void initJavaScriptObjects() {
		if(addonDescriptor != null){
			previewHTML = addonDescriptor.getPreviewHTML();
			presenterObject = initJavaScript("Addon" + module.getAddonId() + "_create");
			jsModel = createModel(module);
		}
		else{
			previewHTML = "Error loading module: " + module.getAddonId();
		}
	}


	private JavaScriptObject createModel(IPropertyProvider provider) {

		TextParser parser = new TextParser();

		JavaScriptObject propertyModel = JavaScriptObject.createArray();
		for(int i=0; i < provider.getPropertyCount(); i++){
			IProperty property = provider.getProperty(i);
			if(property instanceof IListProperty){
				IListProperty listProperty = (IListProperty) property;
				JavaScriptObject listModel = JavaScriptObject.createArray();
				for(int j = 0; j < listProperty.getChildrenCount(); j++){
					JavaScriptObject providerModel = createModel(listProperty.getChild(j));
					addToJSArray(listModel, providerModel);
				}
				addPropertyToJSObject(propertyModel, property.getName(), listModel);
			} else if (property instanceof IStaticListProperty) {
				IStaticListProperty listProperty = (IStaticListProperty) property;
				JavaScriptObject listModel = JavaScriptObject.createObject();
				for(int j = 0; j < listProperty.getChildrenCount(); j++){
					IPropertyProvider child = listProperty.getChild(j);
					JavaScriptObject childModel = createModel(child);
					String name = this.getStringFromJSObject(childModel, "name");
					JavaScriptObject object = this.getObjectFromJSObject(childModel, "value");
					this.addPropertyToJSObject(listModel, name, object);
				}
				addPropertyToJSObject(propertyModel, property.getName(), listModel);
			} else if (property instanceof IStaticRowProperty) {
				propertyModel = JavaScriptObject.createObject();
				IStaticRowProperty listProperty = (IStaticRowProperty) property;
				JavaScriptObject listModel = JavaScriptObject.createObject();
				for(int j = 0; j < listProperty.getChildrenCount(); j++){
					if (listProperty.getChild(j).getPropertyCount() > 0) {
						String value = listProperty.getChild(j).getProperty(0).getValue();
						addPropertyToJSObject(listModel, listProperty.getChild(j).getProperty(0).getName(), value);
					}
				}
				addPropertyToJSObject(propertyModel, "value", listModel);
				addPropertyToJSObject(propertyModel, "name", property.getName());
			} else if (property instanceof IEditableSelectProperty) {
				IEditableSelectProperty castedProperty = (IEditableSelectProperty)property;
				JavaScriptObject editableSelectModel = JavaScriptObject.createObject();
				addPropertyToJSObject(editableSelectModel, "value", castedProperty.getChild(castedProperty.getSelectedIndex()).getValue());
				addPropertyToJSObject(editableSelectModel, "name", castedProperty.getChild(castedProperty.getSelectedIndex()).getName());
				addPropertyToJSObject(propertyModel, property.getName(), editableSelectModel);
			} else{
				String value = property.getValue();
				addPropertyToJSObject(propertyModel, property.getName(), value);
			}
		}

		return propertyModel;
	}


	private native JavaScriptObject initJavaScript(String name) /*-{
		if($wnd.window[name] == null){
			return function(){}
		}
		return $wnd.window[name]();
	}-*/;


	private native void addPropertyToJSObject(JavaScriptObject model, String name, String value)  /*-{
		model[name] = value;
	}-*/;


	private native void addPropertyToJSObject(JavaScriptObject model, String name, JavaScriptObject obj)  /*-{
		model[name] = obj;
	}-*/;

	private native void addToJSArray(JavaScriptObject arrayModel, JavaScriptObject obj)  /*-{
		arrayModel.push(obj);
	}-*/;
	
	private native String getStringFromJSObject (JavaScriptObject model, String name)  /*-{
		return model[name];
	}-*/; 
	
	private native JavaScriptObject getObjectFromJSObject (JavaScriptObject model, String name)  /*-{
		return model[name];
	}-*/; 


	private Widget getView() {
		final HTML view = new HTML(previewHTML);
		view.setStyleName("addon_" + module.getAddonId());
		view.getElement().setId(module.getId());
		StyleUtils.applyInlineStyle(view, module);

		view.addAttachHandler(new Handler() {
			@Override
			public void onAttachOrDetach(AttachEvent event) {
				if(event.isAttached()){
					createPreview(presenterObject, view.getElement(), jsModel, module.getAddonId(), addonPreview);
				}
			}
		});

		return view;
	}

	private static JavaScriptObject inLineChoiceToJs(List<InlineChoiceInfo> choiceInfos) {
		JavaScriptObject model = JavaScriptObject.createArray();

		for (int i = 0; i < choiceInfos.size(); i++) {
			JavaScriptObject gap = JavaScriptObject.createArray();
			JavaScriptUtils.addPropertyToJSArray(gap, "id", choiceInfos.get(i).getId());
			JavaScriptUtils.addPropertyToJSArray(gap, "answer", choiceInfos.get(i).getAnswer());
			JavaScriptUtils.addPropertyToJSArray(gap, "value", choiceInfos.get(i).getValue());

			JavaScriptObject distractors = JavaScriptObject.createArray();
			Iterator<String> gapDistractors = choiceInfos.get(i).getDistractors();

			while (gapDistractors.hasNext()) {
				String dist = gapDistractors.next();
				JavaScriptUtils.addElementToJSArray(distractors, dist);
			}

			JavaScriptUtils.addObjectAsPropertyToJSArray(gap, "distractors", distractors);
			JavaScriptUtils.addObjectToJSArray(model, gap);
		}
		return model;
	}

	private static JavaScriptObject gapsToJs(List<GapInfo> gapInfos) {
		JavaScriptObject model = JavaScriptObject.createArray();

		for (int i = 0; i < gapInfos.size(); i++) {
			JavaScriptObject gap = JavaScriptObject.createArray();
			JavaScriptUtils.addPropertyToJSArray(gap, "id", gapInfos.get(i).getId());
			JavaScriptUtils.addPropertyToJSArray(gap, "value", gapInfos.get(i).getValue());

			JavaScriptObject answersArray = JavaScriptObject.createArray();
			Iterator<String> answers = gapInfos.get(i).getAnswers();

			while (answers.hasNext()) {
				String dist = answers.next();
				JavaScriptUtils.addElementToJSArray(answersArray, dist);
			}

			JavaScriptUtils.addObjectAsPropertyToJSArray(gap, "answers", answersArray);
			JavaScriptUtils.addObjectToJSArray(model, gap);
		}
		return model;
	}

	private String parseText(String text){
		TextParser parser = new TextParser();
		parser.skipGaps();
		ParserResult result = parser.parse(text);
		return result.parsedText;
	}

	private JavaScriptObject parseGaps(String text, JavaScriptObject options) {
		TextParser parser = new TextParser();
		Boolean isCaseSensitive = Boolean.valueOf(JavaScriptUtils.getArrayItemByKey(options, "isCaseSensitive"));
		parser.setCaseSensitiveGaps(isCaseSensitive);
		ParserResult result = parser.parse(text);

		JavaScriptObject inlineGaps = inLineChoiceToJs(result.choiceInfos);
		JavaScriptObject gaps = gapsToJs(result.gapInfos);

		JavaScriptObject model = JavaScriptObject.createArray();
		JavaScriptUtils.addObjectAsPropertyToJSArray(model, "inLineGaps", inlineGaps);
		JavaScriptUtils.addObjectAsPropertyToJSArray(model, "gaps", gaps);
		JavaScriptUtils.addPropertyToJSArray(model, "parsedText", result.parsedText);

		return model;
	}

	private native void createPreview(JavaScriptObject obj, Element view,
			JavaScriptObject model, String addonId, AddonPreview x)
	/*-{

		var getTextParser = function() {
			var commands = function() {
			};

			commands.parse = function(text) {
				return x.@com.lorepo.iceditor.client.module.addon.AddonPreview::parseText(Ljava/lang/String;)(text);
			};

			commands.parseGaps = function(text, options) {
				if (typeof options == 'undefined') {
					options = {
						isCaseSensitive: false
					};
				}

				if (!('isCaseSensitive' in options)) {
					options.isCaseSensitive = false;
				}

				return x.@com.lorepo.iceditor.client.module.addon.AddonPreview::parseGaps(Ljava/lang/String;Lcom/google/gwt/core/client/JavaScriptObject;)(text, options);
			};


			return commands;
		};

		try{
			if(obj.createPreview != undefined){;
				try {
					if(obj.setTextParser != undefined){
						obj.setTextParser(getTextParser);
					}
				}
				catch(err){
				}
				obj.createPreview(view, model);
			}
		}
		catch(err){
	  		alert("Can't load addon: " + addonId + "\n" + err);
	  	}
	}-*/;

    public int getMaxScore() {
		try {
			return this.getMaxScore(presenterObject);
		} catch(Exception e) {
			JavaScriptUtils.log("Can't get max score of addon: " + module.getAddonId() + "error: " + e.toString());
		}

		return 0;
	}

	private native int getMaxScore(JavaScriptObject obj) /*-{
		if(obj.getMaxScore){
			if(obj.getMaxScore != undefined){
				return obj.getMaxScore();
			}
		}

		return 0;
	}-*/;
	
	public JavaScriptObject getPresenterObject () {
		return this.presenterObject;
	}

}
