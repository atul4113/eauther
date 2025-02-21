package com.lorepo.iceditor.client.actions;

import java.util.ArrayList;
import java.util.List;

import com.google.gwt.dom.client.Element;
import com.google.gwt.user.client.DOM;
import com.google.gwt.user.client.Timer;
import com.lorepo.iceditor.client.actions.ActionFactory.ActionType;
import com.lorepo.iceditor.client.actions.api.IServerService.IRequestListener;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.widgets.modals.SingleButtonModalListener;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationType;
import com.lorepo.icf.utils.ILoadListener;
import com.lorepo.icf.utils.URLUtils;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.addonsLoader.AddonLoaderFactory;
import com.lorepo.icplayer.client.addonsLoader.IAddonLoader;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.addon.AddonDescriptor;
import com.lorepo.icplayer.client.model.addon.AddonDescriptorFactory;
import com.lorepo.icplayer.client.model.addon.AddonEntry;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.api.player.IAddonDescriptor;
import com.lorepo.icplayer.client.xml.IProducingLoadingListener;
import com.lorepo.icplayer.client.xml.page.PageFactory;

public class AddTTSToPresentationAction extends AbstractAction{

	AppFrame appFrame = null;
	AppController appController = null;
	AddAllTextToSpeechAction autofillAction = null;
	List<String> modifiedPageNames = null;
	
	int correctPageParsedCounter = 0;
	int errorPageParsedCounter = 0;
	
	public AddTTSToPresentationAction(AppController controller) {
		super(controller);
	}

	
	@Override
	public void execute() {
		appFrame = getAppFrame();
		appController = getAppController();
		
		AbstractAction action = getActionFactory().getAction(ActionType.addAllTextToSpeech);
		if (action instanceof AddAllTextToSpeechAction) autofillAction = (AddAllTextToSpeechAction)action;
		
	    showAsyncNotification(DictionaryWrapper.get("Editor_begin_adding_tts"), NotificationType.notice);
	    
		correctPageParsedCounter = 0;
		errorPageParsedCounter = 0;
		List<Page> pages = getServices().getModel().getAllPages();
		modifiedPageNames = new ArrayList<String>();
		for (int i = 0; i < pages.size(); i++) {
			Page page = pages.get(i);
			loadAndParsePage(page);	
		}
	}
	
	private void parsePage(Page page) {
		List<String> modules = page.getModulesList();
		boolean hasTextToSpeech = false;
		for (String id: modules) {
			if (id.equals("Text_To_Speech1")){
				hasTextToSpeech = true;
				break;
			}
		}
		if (!hasTextToSpeech){ 
			addTextToSpeech(page);
		} else {
			incrementPageParseCounter(true);
		}
	}
	
	public void addTextToSpeech(final Page page) {
		Content content = getModel();
		if (content.addonIsLoaded("Text_To_Speech")) {
			IAddonDescriptor ittsDescriptor = content.getAddonDescriptor("Text_To_Speech");
			if (ittsDescriptor instanceof AddonDescriptor) {
				AddonDescriptor ttsDescriptor = (AddonDescriptor)ittsDescriptor;
				onDescriptorLoaded(ttsDescriptor, page);
			} else {
				incrementPageParseCounter(false);
			}
		} else {
			AddonEntry entry = AddonDescriptorFactory.getInstance().getEntry("Text_To_Speech");
			final AddonDescriptor descriptor = new AddonDescriptor(entry.getId(), entry.getDescriptorURL());
			AddonLoaderFactory addonLoader = new AddonLoaderFactory(this.getServices().getModel().getBaseUrl());
			IAddonLoader loader = addonLoader.getAddonLoader(descriptor);
			loader.load(new ILoadListener() {
				@Override
				public void onFinishedLoading(Object obj) {
					onDescriptorLoaded(descriptor, page);
				}

				@Override
				public void onError(String error) {
					incrementPageParseCounter(false);
				}
			});
		}
	}
	
	private void onDescriptorLoaded(AddonDescriptor ttsDescriptor, final Page page) {
		insertAddonIntoContent(ttsDescriptor);
		InsertAddonAction.insertAddonIntoPage(page, ttsDescriptor, appController, appFrame);
		autofillAction.execute(page);
		getAppController().savePage(page, new IRequestListener() {

			@Override
			public void onFinished(String responseText) {	
				modifiedPageNames.add(page.getName());
				incrementPageParseCounter(true);
			}

			@Override
			public void onError(int reason_code) {
				incrementPageParseCounter(false);
			}
			
		});
	}
	
	private void insertAddonIntoContent(AddonDescriptor descriptor) {
		getAppController().addAddon(descriptor);

		Content content = getServices().getModel();
		content.getAddonDescriptors().put(descriptor.getAddonId(), descriptor);
	}
	
	private void loadAndParsePage(final Page page){
		if(!page.isLoaded()){	
			Content model = getServices().getModel();

			// Load new page
			String baseUrl = model.getBaseUrl();

			String url = URLUtils.resolveURL(baseUrl, page.getHref());

			PageFactory factory = new PageFactory((Page) page);
			factory.load(url, new IProducingLoadingListener() {
				@Override
				public void onFinishedLoading(Object producedItem) {
					parsePage(page);
				}

				@Override
				public void onError(String error) {
					incrementPageParseCounter(false);
				}
			});
		} else {
			parsePage(page);
		}
	}
	
	public void incrementPageParseCounter(boolean correct){
		if(correct) {
			this.correctPageParsedCounter++;
		} else {
			this.errorPageParsedCounter++;
		}
		if(this.getServices().getModel().getAllPages().size() <= correctPageParsedCounter + errorPageParsedCounter) {
			if (errorPageParsedCounter == 0){
				showAsyncNotification(DictionaryWrapper.get("Editor_finish_adding_tts"), NotificationType.success);
			} else {
				showAsyncNotification(DictionaryWrapper.get("Editor_finish_adding_tts_with_errors"), NotificationType.error);
			}
			String message = "";
			if (modifiedPageNames.size() > 0){
				message = generateModifiedPagesList();
			} else {
				message = DictionaryWrapper.get("Editor_tts_no_modified_pages");
			}
			appFrame.getModals().addModalSingleButton(message, new SingleButtonModalListener() {

                public void onAccept() {
                }
            });  
			
			getAppController().saveContent();
		}
	}
	
	private String generateModifiedPagesList() {
		if (modifiedPageNames.size() == 0)
		    return "";
		Element wrapper = DOM.createElement("div");
		
		Element title = DOM.createElement("div");
		title.setInnerText(DictionaryWrapper.get("Editor_tts_modified_pages_list"));
		wrapper.appendChild(title);
		
		Element list = DOM.createElement("div");
		String listText = "";
		for (String name: modifiedPageNames) listText += name+", ";
		listText = listText.substring(0,listText.length() - 2);
		list.setInnerText(listText);
		wrapper.appendChild(list);
		
		return wrapper.getInnerHTML();
	}
	
	private void showAsyncNotification(final String message, final NotificationType type) {
		Timer t = new Timer() {
			// Without the timer, notification will only appear once parser finished working
	      @Override
	      public void run() {
	    	  getAppFrame().getNotifications().addMessage(message, type, false);
	      }
	    };
	    t.schedule(50);
	}
	
	
	
}
