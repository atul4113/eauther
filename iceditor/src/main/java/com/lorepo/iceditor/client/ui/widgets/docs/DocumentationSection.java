package com.lorepo.iceditor.client.ui.widgets.docs;

import java.util.ArrayList;
import java.util.List;

import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONString;
import com.google.gwt.json.client.JSONValue;

public class DocumentationSection {
	public String name;
	public DocumentationPage page;
	public List<DocumentationPage> children = new ArrayList<DocumentationPage>();

	public DocumentationSection (String name, String sectionJSON) {
		this.name = name;
		parseSectionJSON(sectionJSON);
	}
	
	private String getStringValue (JSONValue value) {
		JSONString str = value.isString();
		
		if (str != null) {
			return str.stringValue();
		} else {
			return "";
		}
	}
	
	private void parseSectionJSON (String sectionJSON) {
		JSONValue parsedSection = JSONParser.parseStrict(sectionJSON);
		
		JSONObject section = parsedSection.isObject();
		
		if (section.containsKey("page") && section.containsKey("children")) {
			JSONObject page = section.get("page").isObject();
			JSONArray children = section.get("children").isArray();
			
			if(page != null && children != null) {
				this.page = new DocumentationPage(getStringValue(page.get("name")), getStringValue(page.get("html")));
				
				for (int i = 0; i < children.size(); i += 1) {
					JSONObject child = children.get(i).isObject();
					
					if (child != null) {
						this.children.add(new DocumentationPage(getStringValue(child.get("name")), getStringValue(child.get("html"))));
					}
				}
			}
		}
	}
}
