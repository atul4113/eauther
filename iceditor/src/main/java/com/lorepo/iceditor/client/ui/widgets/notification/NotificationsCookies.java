package com.lorepo.iceditor.client.ui.widgets.notification;

import java.util.Date;

import com.google.gwt.user.client.Cookies;
import com.google.gwt.user.client.Window;

public class NotificationsCookies {
	
	private final static String notificationsCookiesPrefix = "icEditor_notifications_";
	private final static String notificationCookieValue = "closed";
	
	public static String get (String id) {
		return Cookies.getCookie(notificationsCookiesPrefix + id);
	}
	
	public static void setForPortal (String id) {
		Cookies.setCookie(notificationsCookiesPrefix + id, notificationCookieValue, getExpirationDate(), null, "/", false);
	}

	public static void setForLesson (String id) {
		String path = Window.Location.getPath();
		Cookies.setCookie(notificationsCookiesPrefix + id, notificationCookieValue, getExpirationDate(), null, path, false);
	}
	
	public static void update (String id) {
		if (get(id) != null) {
			setForPortal(id);
		}
	}
	
	private static Date getExpirationDate () {
		Date expiration = new Date();
		
		Long expTime = expiration.getTime();
		Long oneDay = (long) (1000 * 60 * 60 * 24);
		expTime += (long) oneDay * 365;
		
		expiration.setTime(expTime);
		
		return expiration;
	}

}
