package com.lorepo.iceditor.client.controller;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.IAsset;
import com.lorepo.icplayer.client.model.asset.AudioAsset;
import com.lorepo.icplayer.client.model.asset.FileAsset;
import com.lorepo.icplayer.client.model.asset.ImageAsset;
import com.lorepo.icplayer.client.model.asset.VideoAsset;

public class MediaProviderImpl implements IMediaProvider {

	private final Content content;
	private final IAppController appController;
	
	private final List<Integer> imagesIndex = new ArrayList<Integer>();
	private final List<Integer> audiosIndex = new ArrayList<Integer>();
	private final List<Integer> videosIndex = new ArrayList<Integer>();
	private final List<Integer> filesIndex = new ArrayList<Integer>();
	
	private final List<IAsset> allMedia = new ArrayList<IAsset>();

	public MediaProviderImpl(Content content, IAppController appController){
		this.appController = appController;
		this.content = content;

		for (int i = 0; i < content.getAssetCount(); i++) {
			IAsset asset = content.getAsset(i);

			if (asset instanceof AudioAsset) {
				audiosIndex.add(Integer.valueOf(i));
			} else if (asset instanceof ImageAsset) {
				imagesIndex.add(Integer.valueOf(i));
			} else if (asset instanceof VideoAsset) {
				videosIndex.add(Integer.valueOf(i));
			} else {
				filesIndex.add(Integer.valueOf(i));
			}
			this.allMedia.add(asset);
		}
	}

	private IAsset getAsset(MediaType type, int index) {
		if (type == MediaType.AUDIO) {
			return this.allMedia.get(audiosIndex.get(index));
		} else if (type == MediaType.IMAGE) {
			return this.allMedia.get(imagesIndex.get(index));
		} else if (type == MediaType.VIDEO) {
			return this.allMedia.get(videosIndex.get(index));
		} else {
			return this.allMedia.get(filesIndex.get(index));
		}
	}

	@Override
	public int getMediaCount(MediaType type) {
		if (type == MediaType.AUDIO) {
			return audiosIndex.size();
		}

		if (type == MediaType.IMAGE) {
			return imagesIndex.size();
		}

		if (type == MediaType.VIDEO) {
			return videosIndex.size();
		}

		if (type == MediaType.FILE) {
			return filesIndex.size();
		}

		return 0;
	}

	@Override
	public String getMediaUrl(MediaType type, int index) {
		return getAsset(type, index).getHref();
	}

	@Override
	public void addMediaUrl(MediaType type, String url, String fileName, String contentType) {
		IAsset asset;

		int index = Integer.valueOf(this.allMedia.size());
		if (type == MediaType.AUDIO) {
			asset = new AudioAsset(url);
			audiosIndex.add(index);
		} else if (type == MediaType.IMAGE) {
			asset = new ImageAsset(url);
			imagesIndex.add(index);
		} else if (type == MediaType.VIDEO) {
			asset = new VideoAsset(url);
			videosIndex.add(index);
		} else {
			asset = new FileAsset(url);
			filesIndex.add(index);
		}

		asset.setOrderNumber(this.allMedia.size());
		this.allMedia.add(asset);
		
		asset.setFileName(fileName.replaceAll("\\p{C}", "")); // remove non-printable characters
		asset.setContentType(contentType);
		
		content.addAsset(asset);
		appController.saveContent();
	}


	@Override
	public String getMediaName(MediaType type, int index) {
		return getAsset(type, index).getFileName();
	}


	@Override
	public int getMediaCount() {
		return audiosIndex.size() + imagesIndex.size() + videosIndex.size() + filesIndex.size();
	}


	@Override
	public String getMediaUrl(int index) {
		return getAssetFromAll(index).getHref();
	}


	@Override
	public String getMediaName(int index) {
		return getAssetFromAll(index).getFileName();
	}

	public IAsset getAssetFromAll(int index) {
		if(index > this.allMedia.size()){
			return null;
		}
		return this.allMedia.get(index);
	}


	@Override
	public String getContentType(int index) {
		return getAssetFromAll(index).getContentType();
	}

	@Override
	public String getContentType(MediaType type, int index) {
		return getAsset(type, index).getContentType();
	}

	@Override
	public MediaType getMediaType(int index) {
		IAsset asset = getAssetFromAll(index);

		if (asset instanceof AudioAsset) {
			return MediaType.AUDIO;
		} else if (asset instanceof ImageAsset) {
			return MediaType.IMAGE;
		} else if (asset instanceof VideoAsset) {
			return MediaType.VIDEO;
		} else {
			return MediaType.FILE;
		}
	}

	@Override
	public void sortByName(OrderType order) {
		Comparator<IAsset> comparator = this.createSortingByNameComparator(order);
		
		if (comparator != null) {
			Collections.sort(this.allMedia, comparator);
		}
	}

	@Override
	public void sortByDate(OrderType order) {
		Comparator<IAsset> comparator = this.createSortingByDateComparator(order);
		
		if (comparator != null) {
			Collections.sort(this.allMedia, comparator);
		}
	};
	
	private Comparator<IAsset> createSortingByDateComparator(OrderType order) {
		Comparator <IAsset> dateComparator = null;
		
		if (order == OrderType.ASCENDING) {
			dateComparator = new Comparator<IAsset>(){
				@Override
				public int compare(IAsset arg0, IAsset arg1) {
					int firstDate = arg0.getOrderNumber();
					int secondDate = arg1.getOrderNumber();
					return compareInts(firstDate, secondDate);
					}
			};
		}
		else if (order == OrderType.DESCENDING) {
			dateComparator = new Comparator<IAsset>() {
				@Override
				public int compare(IAsset arg0, IAsset arg1) {
					int firstDate = arg0.getOrderNumber();
					int secondDate = arg1.getOrderNumber();
					return compareInts(secondDate, firstDate);
				}
			};
		}
		return dateComparator;
	}
	
	private Comparator<IAsset> createSortingByNameComparator(OrderType order) {
		Comparator <IAsset> fileNameComparator = null;
		
		if (order == OrderType.ASCENDING) {
			fileNameComparator = new Comparator<IAsset>(){
				@Override
				public int compare(IAsset arg0, IAsset arg1) {
					String filenameFirst = arg0.getFileName().toUpperCase();
					String filenameSecond = arg1.getFileName().toUpperCase();
					return filenameSecond.compareTo(filenameFirst);
				}
			};
		}
		else if (order == OrderType.DESCENDING) {
			fileNameComparator = new Comparator<IAsset>() {
				@Override
				public int compare(IAsset arg0, IAsset arg1) {
					String filenameFirst = arg0.getFileName().toUpperCase();
					String filenameSecond = arg1.getFileName().toUpperCase();
					return filenameFirst.compareTo(filenameSecond);
				}
			};
		}
		return fileNameComparator;
	}
	
	private int compareInts(int arg0, int arg1) {
		if (arg0 < arg1) {
			return -1;
		}
		else if (arg0 == arg1){
			return 0;
		}
		else {
			return 1;
		}
	}
	
	
}

