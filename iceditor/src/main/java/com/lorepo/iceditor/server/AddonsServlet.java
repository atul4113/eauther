package com.lorepo.iceditor.server;


import java.io.FileReader;
import java.io.IOException;

import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;



@SuppressWarnings("serial")
public class AddonsServlet extends HttpServlet {


    public void doGet(HttpServletRequest req, HttpServletResponse res)
    	    throws IOException {

    	FileReader reader = new FileReader("content/addons/index.json");

    	char[]	buf = new char[1024];
    	
    	String text = "";
    	int count;
    	while((count = reader.read(buf)) > 0){
    		text += new String(buf, 0, count);
    	}
		res.getWriter().write(text);
		reader.close();
    }
}
