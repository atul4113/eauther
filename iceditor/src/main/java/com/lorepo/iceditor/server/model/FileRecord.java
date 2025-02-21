package com.lorepo.iceditor.server.model;

import javax.persistence.Id;

import com.googlecode.objectify.Objectify;
import com.googlecode.objectify.ObjectifyService;

/**
 * Rekord z danymi 
 * @author Krzysztof Langner
 *
 */
public class FileRecord {
	
	@Id
	private Long id;	
	private String contentType = "text/xml";
	private String contents;

	/**
	 * Constructor
	 */
	public FileRecord() {
		super();	
	}

	/**
	 * constructor
	 * @param id
	 * @param contents
	 */
	public FileRecord(Long id, String contentType, String contents) {
	  
		 super();
		 this.id = id;
		 this.contentType = contentType;
		 this.contents = contents;
	 }

	/**
	 * @return contents
	 */
	public String getContents() {
	
		return contents;
	}

	/**
	 * @return contentType
	 */
	public String getContentType() {
	
		return contentType;
	}

	/**
	 * @return id
	 */
	public Long getId() {
	  
		return id;
	}
	

	/**
	 * Get content by id
	 * @param id
	 * @return
	 */
	public static FileRecord findById(Long id){
		Objectify service = getService();
	 	return service.get(FileRecord.class, id);
	}

	 
	/**
	 * save
	 * @param id
	 * @return
	 */
	 public void save(){
	  
		 Objectify service = getService();
		 service.put(this);
	 }
	 
	 
	 /**
	  * Wstawienie zawartości pliku
	  * @param c
	  */
	 public void setContents(String c){
		 contents = c;
	 }

	 
	/**
	 * Get service
	 * @return
	 */
	private static Objectify getService() {
	
		return ObjectifyService.begin();
	}

	public void setContentType(String type) {

		this.contentType = type;
	}

}
