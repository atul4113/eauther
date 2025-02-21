package com.lorepo.iceditor.client.module.properties;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dev.jjs.JavaScriptCompiler;
import com.google.gwt.xml.client.CDATASection;
import com.google.gwt.xml.client.Document;
import com.google.gwt.xml.client.NamedNodeMap;
import com.google.gwt.xml.client.Node;
import com.google.gwt.xml.client.NodeList;
import com.google.gwt.http.client.Request;
import com.google.gwt.http.client.RequestBuilder;
import com.google.gwt.http.client.RequestCallback;
import com.google.gwt.http.client.RequestException;
import com.google.gwt.http.client.Response;
import com.google.gwt.xml.client.XMLParser;
import com.lorepo.icf.properties.IAudioProperty;
import com.lorepo.icf.properties.IBooleanProperty;
import com.lorepo.icf.properties.IEditableSelectProperty;
import com.lorepo.icf.properties.IEnumSetProperty;
import com.lorepo.icf.properties.IEventProperty;
import com.lorepo.icf.properties.IFileProperty;
import com.lorepo.icf.properties.IHtmlProperty;
import com.lorepo.icf.properties.IImageProperty;
import com.lorepo.icf.properties.IListProperty;
import com.lorepo.icf.properties.IProperty;
import com.lorepo.icf.properties.IPropertyProvider;
import com.lorepo.icf.properties.ITextProperty;
import com.lorepo.icf.properties.IVideoProperty;
import com.lorepo.icplayer.client.module.api.IModuleModel;

public class ModuleDefaultPropertiesService {
	private static Map<String, Node> MODULES = new HashMap<String, Node>();
	private static Map<String, Map<String, ModuleDefaultProperty>> PROPERTIES = new HashMap<String, Map<String, ModuleDefaultProperty>>();
	
	private static final String fileNamePrefix = "default_properties_";
	private static final String defaultFileUrl = "modules/en/default_properties_en.xml";
	
	public static void init (String lang) {
		MODULES.clear();
		PROPERTIES.clear();
		if (lang.compareToIgnoreCase("mx") == 0) {
			lang = "es";
		}
		
		loadXML(GWT.getModuleBaseURL() + "modules/" + lang + "/" + fileNamePrefix + lang + ".xml");
	}
	
	private static void loadXML(final String url) {
		RequestBuilder request = new RequestBuilder(RequestBuilder.GET, url);
		
		try {
			request.sendRequest(null, new RequestCallback() {
				
				@Override
				public void onResponseReceived(Request request, Response response) {
					if (response.getStatusCode() == 200) {
						onXMLLoaded(response.getText());
					} else {
						loadDefaultXML(url);
					}
				}
				
				@Override
				public void onError(Request request, Throwable exception) {
					loadDefaultXML(url);
				}
			});
		} catch (RequestException e) {
			loadDefaultXML(url);
		}
	}
	
	private static void loadDefaultXML(String oldUrl) {
		String defaultUrl = GWT.getModuleBaseURL() + defaultFileUrl;
		if (defaultUrl.compareToIgnoreCase(oldUrl) != 0) {
			loadXML(defaultUrl);
		}
	}
	
	private static void onXMLLoaded (String xml) {
		Document DefaultPropertiesXML = XMLParser.parse(xml);
		NodeList addons = DefaultPropertiesXML.getElementsByTagName("addon");
		for (int i = 0; i < addons.getLength(); i += 1) {
			Node addon = addons.item(i);
			String name = addon.getAttributes().getNamedItem("id").getNodeValue();
			MODULES.put(name, addon);
		}
	}
	
	public static Map<String, ModuleDefaultProperty> getDefaultProperties (String name) {
		if (PROPERTIES.containsKey(name)) {
			return PROPERTIES.get(name);
		} else {
			Map<String, ModuleDefaultProperty> defaultProperites = readModuleProperties(name);
			if (defaultProperites != null) {
				PROPERTIES.put(name, defaultProperites);
				return defaultProperites;
			}
		}
		return null;
	}
	
	public static void setProperties (IModuleModel module) {
		String name = module.getModuleTypeName();
		
		if (name.equalsIgnoreCase("button")) {
			name = module.getClassNamePrefix() + name;
		}

		if (PROPERTIES.containsKey(name)) {
			setProperties(module, PROPERTIES.get(name), name);
		} else {
			Map<String, ModuleDefaultProperty> defaultProperites = readModuleProperties(name);
			if (defaultProperites != null) {
				PROPERTIES.put(name, defaultProperites);
				setProperties(module, defaultProperites, name);
			}
		}
	}
	
	private static void setProperties (IProperty property, String moduleName, ModuleDefaultProperty propertyValue, String name) {
		//Youtube addon has two ID properties.
		if (!propertyValue.isForbidden()
		|| (moduleName.compareTo("list") == 0)
		|| (moduleName.compareTo("editableselect") == 0)
		|| (moduleName.compareTo("YouTube_Addon") == 0
		&& name.compareTo("ID") == 0)) {
			if (propertyValue.isProtectedInteger()) {
				setIntegerProperty(property, propertyValue);
			} else if (propertyValue.isList()) {
				setListProperty(property, propertyValue.listValue);
			} else if (propertyValue.isSimple()){
				setProperty(property, propertyValue.value);
			}
		}
	}

	private static void setProperties (IPropertyProvider module, Map<String, ModuleDefaultProperty> map, String moduleName) {
		for (int i = 0; i < module.getPropertyCount(); i += 1) {
			IProperty property = module.getProperty(i);
			String name = property.getName();

			if (map.containsKey(name)) {
				ModuleDefaultProperty propertyValue = map.get(name);
				setProperties (property, moduleName, propertyValue, name);
			}
		}
	}

	private static void setIntegerProperty(IProperty property, ModuleDefaultProperty propertyValue) {
		if (propertyValue.isSimple()) {
			try {
				Integer value = Integer.parseInt(propertyValue.value);
				property.setValue(value.toString());
			} catch (NumberFormatException e) {}
		}
	}

	private static void setListProperty(IProperty property, List<Map<String, ModuleDefaultProperty>> listValue) {
		if (listValue.size() == 0) {
			return;
		}
		
		if (property instanceof IListProperty) {
			IListProperty listProperty = (IListProperty) property;
			
			// If listProperty does not have enough children we need to create them.
			if (listValue.size() > listProperty.getChildrenCount()) {
				int difference = listValue.size() - listProperty.getChildrenCount();
				listProperty.addChildren(difference);
			}
			
			for(int i = 0; i < listProperty.getChildrenCount(); i += 1) {
				IPropertyProvider child = listProperty.getChild(i);
				setProperties(child, listValue.get(i), "list");
			}
		} else if (property instanceof IEditableSelectProperty) {
			IEditableSelectProperty editableProperty = (IEditableSelectProperty) property;
			if (listValue.size() > 0) {
				for (int i = 0; i < editableProperty.getChildrenCount(); i++) {
					IProperty childProperty = editableProperty.getChild(i);
					String childName = childProperty.getName();
					if (listValue.get(0).containsKey(childName)) {
						ModuleDefaultProperty propertyValue = listValue.get(0).get(childName);
						setProperties(childProperty, "editableselect", propertyValue, childName);
					}
				}
			}
		}
	}

	private static void setProperty(IProperty property, String value) {
		String parsedValue = preparePropertyValue(property, value);

		if (parsedValue != null) {
			property.setValue(parsedValue);
		}
	}

	private static String preparePropertyValue (IProperty property, String value) {
		value = value.replaceAll("\\r\\n", "\n").replaceAll("\\r", "\n");
		
		if (property instanceof IBooleanProperty) {
			if (value.compareToIgnoreCase("true") == 0) {
				return "True";
			} else {
				return "False";
			}
		} else if (property instanceof IAudioProperty || property instanceof IVideoProperty ||
				property instanceof IFileProperty || property instanceof IImageProperty ||
				property instanceof ITextProperty || property instanceof IHtmlProperty ||
				property instanceof IEventProperty) {
			return value;
		} else if (property instanceof IEnumSetProperty) {
			IEnumSetProperty enumProperty = (IEnumSetProperty) property;
			for (int i = 0; i < enumProperty.getAllowedValueCount(); i += 1) {
				if(enumProperty.getAllowedValue(i).compareTo(value) == 0) {
					return value;
				}
			}
		} else if (property instanceof IProperty) {
			return value;
		} 
		return null;
	}
	
	private static Map<String, ModuleDefaultProperty> readModuleProperties (String name) {
		if (MODULES.containsKey(name)) {
			Map<String, ModuleDefaultProperty> defaultPropertiesValues = readProperties(MODULES.get(name));
			return defaultPropertiesValues;
		} else {
			return null;
		}
	}
	
	private static Map<String, ModuleDefaultProperty> readProperties (Node propertiesNode) {
		Map<String, ModuleDefaultProperty> defaultPropertiesValues = new HashMap<String, ModuleDefaultProperty>();

		for(Node defaultProperty : getChildNodes(propertiesNode, "property")) {
			NamedNodeMap propertyAttributes = defaultProperty.getAttributes();
			String propertyName = propertyAttributes.getNamedItem("name").getNodeValue();
			String propertyType = propertyAttributes.getNamedItem("type").getNodeValue();
			
			if (propertyType.compareToIgnoreCase("list") == 0) {
				defaultPropertiesValues.put(propertyName, new ModuleDefaultProperty(propertyName, getPropertyListValue(defaultProperty)));
			} else if (propertyType.compareToIgnoreCase("editableSelect") == 0) {
				defaultPropertiesValues.put(propertyName, new ModuleDefaultProperty(propertyName, getEditableSelectDefaultProperty(defaultProperty)));
			}
			else {
				defaultPropertiesValues.put(propertyName, new ModuleDefaultProperty(propertyName, getPropertyValue(defaultProperty)));
			}
		}
		return defaultPropertiesValues;
	}
	
	private static List<Map<String, ModuleDefaultProperty>> getPropertyListValue (Node property) {
		List<Map<String, ModuleDefaultProperty>> listValue = new ArrayList<Map<String,ModuleDefaultProperty>>();

		try {
			Node items = getChildNodes(property, "items").get(0);
			
			for (Node child : getChildNodes(items, "item")) {
				listValue.add(readProperties(child));
			}
		} catch (IndexOutOfBoundsException e) {}
		return listValue;
	}

	private static List<Map<String, ModuleDefaultProperty>> getEditableSelectDefaultProperty (Node property) {
		List<Map<String, ModuleDefaultProperty>> listValue = new ArrayList<Map<String,ModuleDefaultProperty>>();
		listValue.add(readProperties(property));
		return listValue;
	}

	private static String getPropertyValue (Node property) {
		try {
			return property.getAttributes().getNamedItem("value").getNodeValue();
		} catch (Exception e) {
			return getValueFromCData(property);
		}
	}
	
	private static String getValueFromCData (Node node) {
		String cDataValue = "";
		String textValue = "";
		for(Node child : getChildNodes(node)){
			if (child.getNodeType() == Node.CDATA_SECTION_NODE) {
				cDataValue += ((CDATASection) child).getData();
			} else if (child.getNodeType() == Node.TEXT_NODE) {
				textValue += child.getNodeValue();
			}
		}
		
		if (cDataValue.length() > 0) {
			return cDataValue;
		} else if (textValue.length() > 0){
			return textValue;
		} else {
			return null;
		}
	}
	
	private static List<Node> getChildNodes (Node node) {
		return getChildNodes(node, "");
	}
	
	private static List<Node> getChildNodes (Node node, String tagName) {
		List<Node> nodes = new ArrayList<Node>();
		
		NodeList childNodes = node.getChildNodes();
		
		for(int i = 0; i < childNodes.getLength(); i += 1) {
			Node child = childNodes.item(i);
			if (tagName.length() == 0 || child.getNodeName().compareToIgnoreCase(tagName) == 0) {
				nodes.add(child);
			}
		}
		
		return nodes;
	}
}
