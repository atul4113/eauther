package com.lorepo.iceditor.client.semi.responsive;

import java.util.HashMap;

public class WasLayoutVisitedOnPage {
	HashMap<String, Boolean> values = new HashMap<String, Boolean> ();

	public void setValue(String semiResponsiveID, boolean b) {
		this.values.put(semiResponsiveID, b);
	} 
	
	public void removeKey(String semiResponsiveID) {
		this.values.remove(semiResponsiveID);
	}
	
	public boolean getValue(String key, boolean defaultValue) {
		if (values.containsKey(key)) {
			return values.get(key);
		}
		
		return defaultValue;
	}
	
	public static WasLayoutVisitedOnPage copy(WasLayoutVisitedOnPage toCopy) {
		WasLayoutVisitedOnPage copied = new WasLayoutVisitedOnPage();
		
		for(String key : toCopy.values.keySet()) {
			copied.values.put(key, toCopy.values.get(key));
		}
		
		return copied;
	}
}