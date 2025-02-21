package com.lorepo.iceditor.server;


import javax.servlet.ServletContextEvent;
import javax.servlet.ServletContextListener;

import com.googlecode.objectify.ObjectifyService;
import com.lorepo.iceditor.server.model.FileRecord;


/**
 * Register domain objects
 * @author Krzysztof Langner
 *
 */
public class ContextInitializer implements ServletContextListener {

	public void contextDestroyed(ServletContextEvent arg) {}

	public void contextInitialized(ServletContextEvent arg) {
		
		ObjectifyService.register(FileRecord.class);
	}
}