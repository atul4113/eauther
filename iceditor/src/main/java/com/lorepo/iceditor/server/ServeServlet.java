package com.lorepo.iceditor.server;


import java.io.IOException;

import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.google.appengine.api.blobstore.BlobKey;
import com.google.appengine.api.blobstore.BlobstoreService;
import com.google.appengine.api.blobstore.BlobstoreServiceFactory;



@SuppressWarnings("serial")
public class ServeServlet extends HttpServlet {


    private BlobstoreService blobstoreService = BlobstoreServiceFactory.getBlobstoreService();

    public void doGet(HttpServletRequest req, HttpServletResponse res)
    	    throws IOException {
    	        
		String stringId = req.getPathInfo();
		stringId = stringId.substring(stringId.lastIndexOf("/")+1);
    	BlobKey blobKey = new BlobKey(stringId);
    	blobstoreService.serve(blobKey, res);
    }
}
