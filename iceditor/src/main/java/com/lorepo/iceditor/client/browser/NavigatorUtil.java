package com.lorepo.iceditor.client.browser;

public class NavigatorUtil {
	
	public static native String getBrowserName() /*-{
	    return navigator.userAgent.toLowerCase();
	}-*/;
	
	public static boolean isChromeBrowser() {
	    return getBrowserName().toLowerCase().contains("chrome");
	}

	public static boolean isFirefoxBrowser() {
	    return getBrowserName().toLowerCase().contains("firefox");
	}

	public static boolean isIEBrowser() {
		String[] names = new String[] {"msie", "trident", "edge"}; // different browser versions have different names
		String browserName = getBrowserName().toLowerCase();
		
		for (String name : names) {
			if (browserName.contains(name)) return true;
		}
		
	    return false;
	}
}
