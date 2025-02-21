package com.lorepo.iceditor.server;

import java.io.BufferedReader;
import java.io.IOException;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.google.appengine.api.blobstore.BlobstoreService;
import com.google.appengine.api.blobstore.BlobstoreServiceFactory;
import com.lorepo.iceditor.server.model.FileRecord;

/**
 * Servlet do pokazywania i zapisywania zawartości plików w datastore
 */
@SuppressWarnings("serial")
public class FileServlet extends HttpServlet{

	
	/**
	 * Pobranie zawartości pliku
	 */
	@Override
	protected void doGet(HttpServletRequest request, HttpServletResponse response)
			throws ServletException, IOException {

		String temp = request.getPathInfo();
		
		String stringId = request.getRequestURI();

		stringId = stringId.substring(stringId.lastIndexOf("/")+1);
		if(stringId.compareTo("blobUploadDir") == 0){
			BlobstoreService blobstoreService = BlobstoreServiceFactory.getBlobstoreService();
			String uploadDir = blobstoreService.createUploadUrl("/upload");
			// BUG in GWT
			uploadDir = uploadDir.replace("krzysztof-home", "127.0.0.1");
			response.getWriter().write(uploadDir);	
		}
		else{
			
			temp = temp.substring(temp.lastIndexOf("/")+1);
			try{
				Long id = Long.parseLong(temp);
				FileRecord cr = FileRecord.findById(id);
				
				response.getWriter().write(cr.getContents());
			}
			catch(NumberFormatException e){
				
			}
			
			response.setHeader("Cache-Control", "no-cache");
		}
		
	}
	
	
	/**
	 * Zapisanie zawartości pliku
	 */
	@Override
	protected void doPost(HttpServletRequest request, HttpServletResponse response)
			throws ServletException, IOException {

		String contents = "";
		
		BufferedReader reader = request.getReader();
		String line = null;
		while((line = reader.readLine()) != null){
			contents += line;
		}
		
		String stringId = request.getPathInfo();
		
		stringId = stringId.substring(stringId.lastIndexOf("/")+1);
		FileRecord pageRecord;
		
		Long id = Long.parseLong(stringId);
		pageRecord = FileRecord.findById(id);
		
		pageRecord.setContents(contents);
		pageRecord.save();
		
		response.getWriter().write(pageRecord.getId().toString());
	}


}
