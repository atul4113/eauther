package com.lorepo.iceditor.client.semi.responsive;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Set;

public final class SemiResponsiveModificationsHistory {
	
	private SemiResponsiveModificationsHistory() {}
	
	public static HashMap<String, String> lastSeen = new HashMap<String, String>();
	public static HashMap<String, WasLayoutVisitedOnPage> wasVisited = new HashMap<String, WasLayoutVisitedOnPage>();
	public static Set<String> layoutAdded = new HashSet<String>();
	public static Set<String> pageAdded = new HashSet<String>();
	
	public static void setLastSeen(String pageID, String semiResponsiveID) {
		lastSeen.put(pageID, semiResponsiveID);
	}
	
	public static void addNewSemiResponsiveLayout(String pageID, String semiResponsiveID) {
		ensureKey(pageID);
		setWasVisited(pageID, semiResponsiveID, false);
		layoutAdded.add(semiResponsiveID);
	}
	
	public static void addNewPage(String pageID) {
		ensureKey(pageID);
		pageAdded.add(pageID);
	}
	
	private static void setWasVisited(String pageID, String semiResponsiveID, boolean value) {
		setBooleanValue(wasVisited, pageID, semiResponsiveID, value);
	}
	
	private static void setBooleanValue(HashMap<String, WasLayoutVisitedOnPage> map, String pageID, String semiResponsiveID, boolean value) {
		WasLayoutVisitedOnPage data = map.get(pageID);
		data.setValue(semiResponsiveID, value);
		map.put(pageID, data);
	}

	private static void ensureKey(String pageID) {
		if (!wasVisited.containsKey(pageID)) {
			SemiResponsiveModificationsHistory.wasVisited.put(pageID, new WasLayoutVisitedOnPage());
		}
	}

	public static void removeSemiResponsiveLayout(String layoutID) {
		deleteLastSeen(layoutID);
		deleteLayoutWasVisitedOnPage(wasVisited, layoutID);
		layoutAdded.remove(layoutID);
	}

	private static void deleteLayoutWasVisitedOnPage(HashMap<String, WasLayoutVisitedOnPage> map, String semiResponsiveLayoutID) {
		for(String key : map.keySet()) {
			WasLayoutVisitedOnPage data = map.get(key);
			data.removeKey(semiResponsiveLayoutID);
		}
	}

	private static void deleteLastSeen(String semiResponsiveID) {
		for (String key : lastSeen.keySet()) {
			String data = lastSeen.get(key);
			if (data.compareTo(semiResponsiveID) == 0) {
				lastSeen.remove(key);
			}
		}
	}

	public static boolean wasAdded(String actualSemiResponsiveID) {
		return layoutAdded.contains(actualSemiResponsiveID);
	}

	public static boolean layoutWasVisited(String pageID, String actualSemiResponsiveID) {
		if (wasVisited.containsKey(pageID)) {
			WasLayoutVisitedOnPage data = wasVisited.get(pageID);
			return data.getValue(actualSemiResponsiveID, false);
		}
		
		return false;
	}

	public static String getLastSeen(String pageID) {
		return lastSeen.get(pageID);
	}

	public static void markAsVisited(String pageID, String semiResponsiveLayoutID) {
		ensureKey(pageID);
		WasLayoutVisitedOnPage map = wasVisited.get(pageID);
		map.setValue(semiResponsiveLayoutID, true);
		
		wasVisited.put(pageID, map);
	}

	public static boolean wasPageAdded(String pageID) {
		return pageAdded.contains(pageID);
	}

	public static void removePage(String pageID) {
		pageAdded.remove(pageID);
	}

	public static void duplicatePage(String oldPageID, String duplicatedPageID) {
		if (pageAdded.contains(oldPageID)) {
			pageAdded.add(duplicatedPageID);
		}
		
		if (lastSeen.containsKey(oldPageID)) {
			String lastSeenLayout = lastSeen.get(oldPageID);
			lastSeen.put(duplicatedPageID, lastSeenLayout);
		}
		
		if (wasVisited.containsKey(oldPageID)) {
			WasLayoutVisitedOnPage dataObj = wasVisited.get(oldPageID);
			wasVisited.put(duplicatedPageID, WasLayoutVisitedOnPage.copy(dataObj));
		}
	}
}
