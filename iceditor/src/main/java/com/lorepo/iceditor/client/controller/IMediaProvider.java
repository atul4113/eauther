package com.lorepo.iceditor.client.controller;

public interface IMediaProvider extends com.lorepo.icf.widgets.mediabrowser.IMediaProvider {
	
	public enum OrderType {
		ASCENDING,
		DESCENDING
	}
	
	public int getMediaCount(MediaType type);
	public int getMediaCount();

	public String getMediaUrl(MediaType type, int index);
	public String getMediaName(MediaType type, int index);
	public String getContentType(MediaType type, int index);
	
	public void	addMediaUrl(MediaType type, String url, String fileName, String contentType);

	public String getMediaUrl(int index);
	public String getMediaName(int index);
	public String getContentType(int index);
	public MediaType getMediaType(int index);
	
	public void sortByName(OrderType order);
	public void sortByDate(OrderType order);
}
