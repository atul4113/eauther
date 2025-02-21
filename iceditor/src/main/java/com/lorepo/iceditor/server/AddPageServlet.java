package com.lorepo.iceditor.server;

import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.lorepo.iceditor.server.model.FileRecord;

/**
 * Servlet do pokazywania i zapisywania zawartości plików w datastore
 */
@SuppressWarnings("serial")
public class AddPageServlet extends HttpServlet{

	
	private static final String SIMPLE_PAGE = 
			"<?xml version='1.0' encoding='UTF-8' ?>" + 
			"<page layout='pixels'>" + 
				"<modules>" + 
					"<shapeModule left='10' top='10' width='100' height='100' style='background-color:red'>" +
					"</shapeModule>" + 
				"</modules>" + 
			"</page>";
	
	/**
	 * Pobranie zawartości pliku
	 */
	@Override
	protected void doGet(HttpServletRequest request, HttpServletResponse response)
			throws ServletException, IOException {

	}
	
	
	/**
	 * Zapisanie zawartości pliku
	 */
	@Override
	protected void doPost(HttpServletRequest request, HttpServletResponse response)
			throws ServletException, IOException {

		FileRecord pageRecord;
		
		String pageXml = SIMPLE_PAGE;
		if(request.getParameter("page") != null){
			String pageUrl = request.getParameter("page");
			pageXml = getPageXml(pageUrl);
		}
		
		pageRecord = new FileRecord();
		pageRecord.setContents(pageXml);
		pageRecord.setContentType("text/xml");
		pageRecord.save();
		
		response.getWriter().write(pageRecord.getId().toString());
	}


	/**
	 * Pobranie zawartości strony z url-a
	 * @param pageUrl
	 * @return
	 */
	private static String getPageXml(String pageUrl) {

		String xml = SIMPLE_PAGE; 
		try {
			FileReader reader = new FileReader("." + pageUrl);
	    	char[]	buf = new char[1024];
	    	
	    	String text = "";
	    	int count;
	    	while((count = reader.read(buf)) > 0){
	    		text += new String(buf, 0, count);
	    	}
	    	
	    	xml = text;
	    	reader.close();
			
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
		
		return xml;
	}
	
	
}
