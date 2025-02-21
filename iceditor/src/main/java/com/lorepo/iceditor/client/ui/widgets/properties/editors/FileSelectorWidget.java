package com.lorepo.iceditor.client.ui.widgets.properties.editors;

import static com.google.gwt.query.client.GQuery.$;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.AnchorElement;
import com.google.gwt.dom.client.DivElement;
import com.google.gwt.dom.client.InputElement;
import com.google.gwt.dom.client.OptionElement;
import com.google.gwt.dom.client.SelectElement;
import com.google.gwt.dom.client.SpanElement;
import com.google.gwt.dom.client.Style.Display;
import com.google.gwt.dom.client.Style.Unit;
import com.google.gwt.http.client.Request;
import com.google.gwt.http.client.RequestBuilder;
import com.google.gwt.http.client.RequestCallback;
import com.google.gwt.http.client.RequestException;
import com.google.gwt.http.client.Response;
import com.google.gwt.http.client.URL;
import com.google.gwt.query.client.GQuery;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.AbsolutePanel;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FileUpload;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteHandler;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.controller.IMediaProvider;
import com.lorepo.iceditor.client.ui.widgets.content.WidgetLockerController;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icf.widgets.mediabrowser.UploadInfo;
import com.lorepo.icf.widgets.mediabrowser.IMediaProvider.MediaType;
import com.lorepo.iceditor.client.controller.IMediaProvider.OrderType;


public class FileSelectorWidget extends Composite {

	private static FileSelectorWidgetUiBinder uiBinder = GWT
			.create(FileSelectorWidgetUiBinder.class);

	interface FileSelectorWidgetUiBinder extends
			UiBinder<Widget, FileSelectorWidget> {
	}
	
	@UiField HTMLPanel panel;
	@UiField HTMLPanel allTab;
	@UiField HTMLPanel imagesTab;
	@UiField HTMLPanel audiosTab;
	@UiField HTMLPanel videosTab;
	@UiField DivElement tabs;
	@UiField DivElement contentsTabs;
	
	
	@UiField SelectElement sort;
	@UiField OptionElement date;
	@UiField OptionElement name;
	@UiField AnchorElement sortMode;
	@UiField SpanElement sortBySpan;
	
	@UiField AnchorElement empty;
	@UiField AnchorElement selectLoad;
	@UiField AnchorElement selectOnlineResource;
	@UiField HTMLPanel load;
	@UiField DivElement onlineResourceTab;
	@UiField DivElement schemelessURLWarning;
	@UiField InputElement onlineResource;
	@UiField AnchorElement save;
	@UiField AnchorElement upload;
	@UiField SpanElement url;
	@UiField AnchorElement closeButton;
	
	FormPanel uploadForm;
	FileUpload fileUpload;
	
	private final static String MAIN_PAGE_ID = "filesPage";
	private final static String NO_SCHEMELESS_WARNING_STYLE = "file-select-schemeless-urls-no-warning";
	
	private IMediaProvider mediaProvider;
	private FileSelectorEventListener listener;
	private static final String BLOB_UPLOAD_DIR_API = "/editor/api/blobUploadDir";
	private String blobUploadURL = null;
	private MediaType mediaType;
	private boolean shouldCloseWidgetLocker;
	private OrderType orderType = OrderType.ASCENDING;
	
	public FileSelectorWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		panel.getElement().setId(MAIN_PAGE_ID);
		empty.setId("fileSelectTab-empty");
		selectOnlineResource.setId("fileSelectTab-online");
		selectLoad.setId("fileSelectTab-load");
		onlineResourceTab.getStyle().setDisplay(Display.NONE);
		
		allTab.getElement().setAttribute("type-name", "all");
		contentsTabs.setId("filesPage-contents");
		imagesTab.getElement().getStyle().setDisplay(Display.NONE);
		imagesTab.getElement().setAttribute("type-name", "image");
		audiosTab.getElement().getStyle().setDisplay(Display.NONE);
		audiosTab.getElement().setAttribute("type-name", "audio");
		videosTab.getElement().getStyle().setDisplay(Display.NONE);
		videosTab.getElement().setAttribute("type-name", "video");
		
		setShouldCloseWidgetLocker(true);
		
		updateElementsTexts();
		connectHandlers();
		hide();
	}

	private MediaType getMediaType(String contentType) {
		MediaType type = MediaType.FILE;
		
		if (contentType.startsWith("audio")) {
			type = MediaType.AUDIO;
		} else if (contentType.startsWith("image")){
			type = MediaType.IMAGE;
		} else if (contentType.startsWith("video")){
			type = MediaType.VIDEO;
		}
		
		return type;
	}
	
	private void createUploadForm() {
		if (uploadForm != null) {
			load.remove(uploadForm);
		}
		
		fileUpload = new FileUpload();
		fileUpload.setName("file");
		
		uploadForm = new FormPanel();
		uploadForm.setEncoding(FormPanel.ENCODING_MULTIPART);
		uploadForm.setMethod(FormPanel.METHOD_POST);
		
		AbsolutePanel formPanel = new AbsolutePanel();
		uploadForm.setWidget(formPanel);
		formPanel.add(fileUpload);

		load.add(uploadForm);
		
		uploadForm.addSubmitCompleteHandler(new SubmitCompleteHandler() {
            @Override
            public void onSubmitComplete(SubmitCompleteEvent event) {
            	String result = event.getResults().trim();
            	UploadInfo uploadInfo = UploadInfo.create(result);
            	
            	MediaType type = getMediaType(uploadInfo.getContentType());
            	mediaProvider.addMediaUrl(type, uploadInfo.getHref(), uploadInfo.getFileName(), uploadInfo.getContentType());
            	FileSelectorWidget.this.listener.onSelected(uploadInfo.getHref());
            }
        });
	}

	private void connectHandlers() {
		Event.sinkEvents(empty, Event.ONCLICK);
		Event.setEventListener(empty, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if (Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				hideSchemelessWarning();
				FileSelectorWidget.this.listener.onSelected("");
				
			}
		});
		
		Event.sinkEvents(selectLoad, Event.ONCLICK);
		Event.setEventListener(selectLoad, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if (Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				hideSchemelessWarning();
				selectLoadTab();
			}
		});
		
		Event.sinkEvents(selectOnlineResource, Event.ONCLICK);
		Event.setEventListener(selectOnlineResource, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if (Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				onlineResourceChangeHandler();
				selectResourceTab();
			}
		});

		Event.sinkEvents(save, Event.ONCLICK);
		Event.setEventListener(save, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if (Event.ONCLICK != event.getTypeInt() && Event.ONTOUCHEND != event.getTypeInt()) {
					return;
				}
				
				String resourceHref = onlineResource.getValue();
				if (resourceHref.isEmpty()) {
					return;
				}
				
				mediaProvider.addMediaUrl(mediaType, onlineResource.getValue(), "", "image/png");
				FileSelectorWidget.this.listener.onSelected(onlineResource.getValue());
			}
		});
		
		Event.sinkEvents(upload, Event.ONCLICK);
		Event.setEventListener(upload, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if (Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				if (fileUpload.getFilename().isEmpty()) {
					return;
				}
				
				uploadForm.submit();
			}
		});
		
		Event.sinkEvents(sort, Event.ONCHANGE);
		Event.setEventListener(sort, new EventListener(){
			@Override
			public void onBrowserEvent(Event event) {
		
				if(Event.ONCHANGE != event.getTypeInt()){
					return;
				}
				sort();
				updateTabs();
			}
			
		});
		
		Event.sinkEvents(sortMode, Event.ONCLICK);
		Event.setEventListener(sortMode, new EventListener(){
			@Override
			public void onBrowserEvent(Event event) {
		
				if(Event.ONCLICK != event.getTypeInt()){
					return;
				}

				changeSortingOrder();
				
				sort();
				updateTabs();
			}
			
		});
		
		Event.sinkEvents(this.onlineResource, Event.ONCHANGE | Event.ONKEYUP);
		Event.setEventListener(this.onlineResource, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if (event.getTypeInt() == Event.ONCHANGE  || event.getTypeInt() == Event.ONKEYUP) {
					onlineResourceChangeHandler();
				}
				return;
			}
		});
	}
	private boolean theSameStart(String first, String second) {
		for (int i = 0; i< Math.min(first.length(),second.length()); i++) {
			if (first.charAt(i) != second.charAt(i))
					return false;
		}
		return true;
	}
	
	private void onlineResourceChangeHandler() {
		String value = onlineResource.getValue();
		
		if (!value.isEmpty() && !value.startsWith("//") && !theSameStart("/file/serve/", value)) {
			
			showSchemelessWarning();
		} else {
			hideSchemelessWarning();
		}
	}
	
	private void hideSchemelessWarning() {
		schemelessURLWarning.addClassName(NO_SCHEMELESS_WARNING_STYLE);
		contentsTabs.getStyle().setTop(80, Unit.PX);
	}

	private void showSchemelessWarning() {
		schemelessURLWarning.removeClassName(NO_SCHEMELESS_WARNING_STYLE);
		contentsTabs.getStyle().setTop(140, Unit.PX);
	}
	
	private void selectLoadTab() {
		selectLoad.addClassName("selected");
		load.getElement().getStyle().setDisplay(Display.BLOCK);
		
		selectOnlineResource.removeClassName("selected");
		onlineResourceTab.getStyle().setDisplay(Display.NONE);
	}
	
	private void selectResourceTab() {
		selectLoad.removeClassName("selected");
		load.getElement().getStyle().setDisplay(Display.NONE);

		selectOnlineResource.addClassName("selected");
		onlineResourceTab.getStyle().setDisplay(Display.BLOCK);
	}

	public void hide() {
		if (shouldCloseWidgetLocker) {
			WidgetLockerController.hide();
		}

		panel.getElement().getStyle().setDisplay(Display.NONE);
	}

	public void show() {
		if (shouldCloseWidgetLocker) {
			WidgetLockerController.show();
		}
		
		this.sort();

		selectLoadTab();
		onlineResource.setValue("");
		this.hideSchemelessWarning();
		
		upload.setAttribute("disabled", "disabled");
		
		allTab.clear();
		imagesTab.clear();
		audiosTab.clear();
		videosTab.clear();

		fillTabs();
		createUploadForm();
		initBlobUploadUrl();

		panel.getElement().getStyle().setDisplay(Display.BLOCK);
	}
	
	public void updateTabs(){		
		this.allTab.clear();
		this.imagesTab.clear();
		this.audiosTab.clear();
		this.videosTab.clear();

		this.fillTabsWithMedia();
	}
	
	private void setActiveTab() {
		$(tabs).find("a").removeClass("selected");

		if (MediaType.AUDIO == mediaType) {
			audiosTab.getElement().getStyle().setDisplay(Display.BLOCK);
			imagesTab.getElement().getStyle().setDisplay(Display.NONE);
			videosTab.getElement().getStyle().setDisplay(Display.NONE);
			allTab.getElement().getStyle().setDisplay(Display.NONE);
			$(tabs).find("a").get(2).addClassName("selected");
		} else if (MediaType.IMAGE == mediaType) {
			imagesTab.getElement().getStyle().setDisplay(Display.BLOCK);
			audiosTab.getElement().getStyle().setDisplay(Display.NONE);
			videosTab.getElement().getStyle().setDisplay(Display.NONE);
			allTab.getElement().getStyle().setDisplay(Display.NONE);
			$(tabs).find("a").get(1).addClassName("selected");
		} else if (MediaType.VIDEO == mediaType) {
			videosTab.getElement().getStyle().setDisplay(Display.BLOCK);
			imagesTab.getElement().getStyle().setDisplay(Display.NONE);
			audiosTab.getElement().getStyle().setDisplay(Display.NONE);
			allTab.getElement().getStyle().setDisplay(Display.NONE);
			$(tabs).find("a").get(3).addClassName("selected");
		} else {
			audiosTab.getElement().getStyle().setDisplay(Display.NONE);
			imagesTab.getElement().getStyle().setDisplay(Display.NONE);
			videosTab.getElement().getStyle().setDisplay(Display.NONE);
			allTab.getElement().getStyle().setDisplay(Display.BLOCK);
			$(tabs).find("a").get(0).addClassName("selected");
		}
	}
	
	private void fillTabsWithMedia(){
		int mediaCount = mediaProvider.getMediaCount();	
		
		for (int i = mediaCount - 1; i >= 0; i--) {
			FileWidget fileWidget = new FileWidget();

			String name = mediaProvider.getMediaName(i);
			final String url = mediaProvider.getMediaUrl(i);
			String contentType = mediaProvider.getContentType(i);
			
			FileEventListener fileEventListener = new FileEventListener() {
				@Override
				public void onSelected() {
					FileSelectorWidget.this.listener.onSelected(url);
				}
			};
			
			fileWidget.setInfo(name, url, contentType);
			fileWidget.setListener(fileEventListener);
			
			allTab.add(fileWidget);
			
			MediaType type = mediaProvider.getMediaType(i);
			FileWidget mediaWidget = new FileWidget();
			mediaWidget.setInfo(name, url, contentType);
			mediaWidget.setListener(fileEventListener);
			
			if (MediaType.FILE == type) {
				if(contentType.startsWith("video")){
					videosTab.add(mediaWidget);
				}else if (contentType.startsWith("audio")){
					audiosTab.add(mediaWidget);
				}else if(contentType.startsWith("image")){
					imagesTab.add(mediaWidget);
				}else{
					continue;
				}
			}

			if (MediaType.AUDIO == type) {
				audiosTab.add(mediaWidget);
			} else if (MediaType.IMAGE == type) {
				imagesTab.add(mediaWidget);
			} else if (MediaType.VIDEO == type) {
				videosTab.add(mediaWidget);
			}
		}
		
		tabs.getStyle().setDisplay(Display.BLOCK);
		contentsTabs.removeClassName("no-tabs");
	}

	private void fillTabs() {
		this.fillTabsWithMedia();

		setActiveTab();
	}
	
	public void changeSortingOrder(){
		if (this.orderType == OrderType.ASCENDING){
			this.orderType = OrderType.DESCENDING;

			this.sortMode.removeClassName("ascending");
			this.sortMode.addClassName("descending");
		}
		else {
			this.orderType = OrderType.ASCENDING;
			
			this.sortMode.removeClassName("descending");
			this.sortMode.addClassName("ascending");
		}
	}
	
	private void initBlobUploadUrl() {
			RequestBuilder builder = new RequestBuilder(
				RequestBuilder.GET, URL.encode(BLOB_UPLOAD_DIR_API));
		builder.setHeader("Content-Type", "text/xml");

		try {
			builder.sendRequest("", new RequestCallback() {
				@Override
				public void onResponseReceived(Request request, Response response) {
					if (response.getStatusCode() == 200) {
						upload.removeAttribute("disabled");
						blobUploadURL = response.getText();
						uploadForm.setAction(blobUploadURL);
					}
				}
				
				@Override
				public void onError(Request request, Throwable exception) {
				}
			});
		} catch (RequestException e) {
		}		
	}
	
	public void setMediaProvider(IMediaProvider mediaProvider) {
		this.mediaProvider = mediaProvider;
	}

	public void setListener(FileSelectorEventListener listener) {
		this.listener = listener;
	}

	public void setMediaType(MediaType mediaType) {
		this.mediaType = mediaType;
	}

	public void updateElementsTexts() {
		$(panel.getElement()).find(".mainPageHeader h3").text(DictionaryWrapper.get("select_file"));

		GQuery tabButton = $(tabs).find(".tabButton");
		tabButton.eq(0).text(DictionaryWrapper.get("all"));
		tabButton.eq(1).text(DictionaryWrapper.get("image"));
		tabButton.eq(2).text(DictionaryWrapper.get("audio"));
		tabButton.eq(3).text(DictionaryWrapper.get("video"));

		url.setInnerText(DictionaryWrapper.get("url"));
		selectLoad.setInnerText(DictionaryWrapper.get("load_from_hard_drive"));
		selectOnlineResource.setInnerText(DictionaryWrapper.get("online_resource"));
		upload.setInnerText(DictionaryWrapper.get("upload"));
		save.setInnerText(DictionaryWrapper.get("save"));
		empty.setInnerText(DictionaryWrapper.get("empty"));
		
		date.setInnerText(DictionaryWrapper.get("date"));
		name.setInnerText(DictionaryWrapper.get("name"));	
		sortBySpan.setInnerText(DictionaryWrapper.get("sort_by"));
		
		schemelessURLWarning.setInnerHTML(DictionaryWrapper.get("schemeless_url_warning"));
	}
	
	public void setShouldCloseWidgetLocker(boolean shouldCloseWidgetLocker) {
		this.shouldCloseWidgetLocker = shouldCloseWidgetLocker;

		if (shouldCloseWidgetLocker) {
			closeButton.addClassName("closeWidgetLocker");
		} else {
			closeButton.removeClassName("closeWidgetLocker");
		}
	}
	
	public void sort(){
		if (this.sort.getSelectedIndex() == 0){
			this.mediaProvider.sortByName(this.orderType);
		}
		if (this.sort.getSelectedIndex() == 1){
			this.mediaProvider.sortByDate(this.orderType);
		}
	}	
	
	public OrderType getOrderType(){
		return this.orderType;
	}
	
	public IMediaProvider getMediaProvider() {
		return this.mediaProvider;
	}
}
