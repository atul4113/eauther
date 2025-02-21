package com.lorepo.iceditor.server;

import java.io.IOException;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.lorepo.iceditor.server.model.FileRecord;

/**
 * Utworzenie przykładowego contentu w bazie danych
 */
@SuppressWarnings("serial")
public class InitContentServlet extends HttpServlet{

	private String simpleContent = 
			"<?xml version='1.0' encoding='UTF-8' ?>" + 
			"<interactiveContent>" + 
				"<pages>" + 
					"<page name='page 1' href='2'/>" + 
				"</pages>" + 
			"</interactiveContent>";

	private String simplePage = 
			"<?xml version='1.0' encoding='UTF-8' ?>" + 
			"<page layout='pixels'>" + 
				"<modules>" + 
					"<shapeModule left='10' top='10' width='100' height='100' style='background-color:red'>" +
					"</shapeModule>" + 
				"</modules>" + 
			"</page>";

	/**
	 * Wstawienie przykładowej zawartości do bazy danych
	 */
	@Override
	protected void doGet(HttpServletRequest request, HttpServletResponse response)
			throws ServletException, IOException {
		

		FileRecord contentRecord = new FileRecord(new Long(1), "text/xml", simpleContent);
		contentRecord.save();
		
		FileRecord pageRecord = new FileRecord(new Long(2), "text/xml", simplePage);
		pageRecord.save();
		
	}
	
	
}
