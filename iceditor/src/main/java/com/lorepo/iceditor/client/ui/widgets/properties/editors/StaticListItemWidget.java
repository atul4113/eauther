package com.lorepo.iceditor.client.ui.widgets.properties.editors;

import java.util.ArrayList;
import java.util.List;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.ui.widgets.properties.ButtonPropertyClickListener;
import com.lorepo.icf.properties.IAudioProperty;
import com.lorepo.icf.properties.IBooleanProperty;
import com.lorepo.icf.properties.IEventProperty;
import com.lorepo.icf.properties.IFileProperty;
import com.lorepo.icf.properties.IHtmlProperty;
import com.lorepo.icf.properties.IImageProperty;
import com.lorepo.icf.properties.IProperty;
import com.lorepo.icf.properties.IPropertyProvider;
import com.lorepo.icf.properties.IStaticRowProperty;
import com.lorepo.icf.properties.ITextProperty;
import com.lorepo.icf.properties.IVideoProperty;
import com.lorepo.icf.widgets.mediabrowser.IMediaProvider.MediaType;

public class StaticListItemWidget extends Composite {

	private static StaticListItemWidgetUiBinder uiBinder = GWT
			.create(StaticListItemWidgetUiBinder.class);

	interface StaticListItemWidgetUiBinder extends UiBinder<Widget, StaticListItemWidget> {
	}
	
	@UiField HTMLPanel panel;
	private StaticListItemTitleWidget title;
	private ListItemContentsWidget contents;
	private List<IListItemWidget> widgets = new ArrayList<IListItemWidget>();
	private RichTextToolbar toolbar;
	private FileSelectorWidget fileSelector;
	private HTMLListItemWidget htmlItem;

	public StaticListItemWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		
		title = new StaticListItemTitleWidget();
		contents = new ListItemContentsWidget();
		
		panel.add(title);
		panel.add(contents);
	}
	
	protected HTMLListItemWidget getListHTMLItem() {
		return htmlItem;
	}
	
	public void setPropertyProvider(IPropertyProvider provider, int index) {
		
		IProperty property = provider.getProperty(index);
		String displayName = property.getDisplayName();
		if (displayName.equals("")) {
			displayName = property.getName();
		}
		IListItemWidget propertyWidget = null;

		if (property instanceof IHtmlProperty) {
			propertyWidget = new HTMLListItemWidget();
			propertyWidget.setName(displayName);
			propertyWidget.setProperty(property);
			
			((HTMLListItemWidget) propertyWidget).setToolbar(toolbar);
			htmlItem = (HTMLListItemWidget) propertyWidget;
		} else if(property instanceof IBooleanProperty) {
			propertyWidget = new BooleanListItemWidget();
			propertyWidget.setName(displayName);
			propertyWidget.setProperty(property);
		} else if(property instanceof IImageProperty) {
			propertyWidget = createFileItem(displayName, property, MediaType.IMAGE);
		} else if(property instanceof IAudioProperty) {
			propertyWidget = createFileItem(displayName, property, MediaType.AUDIO);
		} else if(property instanceof IVideoProperty) {
			propertyWidget = createFileItem(displayName, property, MediaType.VIDEO);
		} else if(property instanceof IFileProperty) {
			propertyWidget = createFileItem(displayName, property, MediaType.FILE);
		} else if(property instanceof ITextProperty || property instanceof IEventProperty) {
			propertyWidget = new TextListItemWidget();
			propertyWidget.setName(displayName);
			propertyWidget.setProperty(property);
		} else if(property instanceof IStaticRowProperty) {
			IStaticRowProperty cast = (IStaticRowProperty) property;
			for (int i = 0; i < cast.getChildrenCount(); i++) {
				for (int j = 0; j < cast.getChild(i).getPropertyCount(); j++) {
					this.setPropertyProvider(cast.getChild(i), j);
				}
			}
		} else {
			propertyWidget = new StringListItemWidget();
			propertyWidget.setName(displayName);
			propertyWidget.setProperty(property);
		}
		
		if (propertyWidget != null) {
			widgets.add(propertyWidget);
			contents.add((Composite) propertyWidget);
		}
	
	}
	
	private IListItemWidget createFileItem(String name, IProperty property, final MediaType mediaType) {
		final IListItemWidget propertyWidget = new FileListItemWidget();

		propertyWidget.setName(name);
		propertyWidget.setProperty(property);
		((FileListItemWidget) propertyWidget).setListener(new ButtonPropertyClickListener() {
			@Override
			public void onSelected() {
				fileSelector.setMediaType(mediaType);
				fileSelector.setShouldCloseWidgetLocker(false);
				fileSelector.setListener(new FileSelectorEventListener() {
					@Override
					public void onSelected(String filePath) {						
						((FileListItemWidget) propertyWidget).setValue(filePath);
						fileSelector.hide();
					}
				});
				fileSelector.show();
			}
		});
		
		return propertyWidget;
	}

	public void setName(String name) {
		title.setName(name);
	}
	
	public void save() {
		for (IListItemWidget widget : widgets) {
			widget.save();
		}
	}

	public void setListener(final ListItemEventListener listener) {
		com.google.gwt.dom.client.Element arrowUpElement = title.getArrowUpElement();
		Event.sinkEvents(arrowUpElement, Event.ONCLICK);
		Event.setEventListener(arrowUpElement, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				event.preventDefault();
				event.stopPropagation();

				if (listener != null) {
					listener.onMoveUp();
				}
			}
		});
		
		com.google.gwt.dom.client.Element arrowDownElement = title.getArrowDownElement();
		Event.sinkEvents(arrowDownElement, Event.ONCLICK);
		Event.setEventListener(arrowDownElement, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				event.preventDefault();
				event.stopPropagation();

				if (listener != null) {
					listener.onMoveDown();
				}
			}
		});
		
	}
	
	public void setArrowUpDisabled() {
		title.getArrowUpElement().getStyle().setOpacity(0.5);
	}

	public void setArrowDownDisabled() {
		title.getArrowDownElement().getStyle().setOpacity(0.5);
	}
	

	public void setToolbar(RichTextToolbar toolbar) {
		this.toolbar = toolbar;
	}

	public void setFileSelector(FileSelectorWidget fileSelector) {
		this.fileSelector = fileSelector;
	}
	
	public boolean isModified() {
		for (IListItemWidget item : widgets) {
			if (item.isModified()) return true;
		}
		
		return false;
	}
	
	public void resetAllItems() {
		for(IListItemWidget widget : widgets) {
			widget.reset();
		}
	}
}
