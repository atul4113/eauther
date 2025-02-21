package com.lorepo.iceditor.client.controller.addons;

import java.util.ArrayList;
import java.util.List;

import com.google.gwt.core.client.JavaScriptObject;
import com.lorepo.icplayer.client.model.addon.AddonEntry;


/**
 * Parser for addon json data return from server
 * @author Krzysztof Langner
 */
public class AddonsJsonParser extends JavaScriptObject{

	protected AddonsJsonParser(){
	}
	
	public final List<AddonEntry> toArray(){
	
		AddonEntry entry;
		ArrayList<AddonEntry>	addons = new ArrayList<AddonEntry>();
		
		for(int i = 0; i < getAddonCount(); i++){
			entry = new AddonEntry(
					getAddonId(i),
					getAddonName(i),
					getAddonDescriptor(i),
					getAddonCategory(i));
			addons.add(entry);
		}
		
		return addons;
	}
	
	
	public static final native AddonsJsonParser parse(String json) /*-{
		return eval('(' + json + ')');
	}-*/;
	
	
	public final native String getVersion() /*-{ 
   		return this.version;
	}-*/;
	
	
	public final native int getAddonCount() /*-{ 
		return this.addons.length;
	}-*/;


	public final native String getAddonId(int index) /*-{ 
		return this.addons[index].id;
	}-*/;

	public final native String getAddonName(int index) /*-{ 
		return this.addons[index].name;
	}-*/;

	public final native String getAddonAbout(int index) /*-{ 
		return this.addons[index].about;
	}-*/;

	public final native String getAddonIcon(int index) /*-{ 
		return this.addons[index].icon_url;
	}-*/;

	public final native String getAddonDescriptor(int index) /*-{ 
		return this.addons[index].descriptor_url;
	}-*/;

	public final native String getAddonCategory(int index) /*-{ 
		return this.addons[index].category;
	}-*/;
}