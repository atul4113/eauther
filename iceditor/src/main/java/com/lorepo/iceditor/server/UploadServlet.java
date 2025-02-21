package com.lorepo.iceditor.server;


import java.io.IOException;
import java.util.List;
import java.util.Map;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.google.appengine.api.blobstore.BlobKey;
import com.google.appengine.api.blobstore.BlobstoreService;
import com.google.appengine.api.blobstore.BlobstoreServiceFactory;



@SuppressWarnings("serial")
public class UploadServlet extends HttpServlet {


    private BlobstoreService blobstoreService = BlobstoreServiceFactory.getBlobstoreService();

    public void doPost(HttpServletRequest req, HttpServletResponse res)
        throws ServletException, IOException {

		// Lista zuplodowanych plików
        Map<String, List<BlobKey>> blobs = blobstoreService.getUploads(req);
        // Pobranie uploadu z konkretna nazwa
        List<BlobKey> blobKeys = blobs.get("file");
        BlobKey blobKey = null;
        
        if(blobKeys.size() > 0){
        	blobKey = blobKeys.get(0);
        }

        if (blobKey == null) {
            res.getWriter().write("Can't find file in upload");
        } else {
        	res.sendRedirect("/upload?blobKey=" + blobKey.getKeyString());
        }
    }

    public void doGet(HttpServletRequest req, HttpServletResponse res)
            throws ServletException, IOException {

    	String key = req.getParameter("blobKey");
    	String url = "/file/serve/" + key;
    	String json = "{\"href\" : \"" + url + "\"," +
    					"\"contentType\" : \"image/png\"," +
    					"\"fileName\" : \"screen1.png\"}";
    	res.setHeader("Content-Type", "text/html");      
    	res.setHeader("Content-Length", Integer.toString(json.length()));      
		res.getWriter().write(json);
		res.getWriter().close();
    }

}