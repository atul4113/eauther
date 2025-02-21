package com.lorepo.iceditor.client.ui.widgets.properties.editors;

import static com.google.gwt.query.client.GQuery.$;

import java.util.HashMap;
import java.util.Map;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.Document;
import com.google.gwt.dom.client.OptionElement;
import com.google.gwt.query.client.GQuery;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.ui.widgets.properties.ButtonPropertyClickListener;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.BooleanListItemWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.FileListItemWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.FileSelectorEventListener;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.FileSelectorWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.HTMLListItemWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.IListItemWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.RichTextToolbar;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.SelectListItemWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.StringListItemWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.TextListItemWidget;
import com.lorepo.icf.properties.IAudioProperty;
import com.lorepo.icf.properties.IBooleanProperty;
import com.lorepo.icf.properties.IEditableSelectProperty;
import com.lorepo.icf.properties.IEnumSetProperty;
import com.lorepo.icf.properties.IEventProperty;
import com.lorepo.icf.properties.IFileProperty;
import com.lorepo.icf.properties.IHtmlProperty;
import com.lorepo.icf.properties.IImageProperty;
import com.lorepo.icf.properties.IProperty;
import com.lorepo.icf.properties.ITextProperty;
import com.lorepo.icf.properties.IVideoProperty;
import com.lorepo.icf.widgets.mediabrowser.IMediaProvider.MediaType;

public class EditableSelectListItemWidget extends Composite  implements IListItemWidget{
	private HashMap<String, IListItemWidget> components = new HashMap<String, IListItemWidget>();
	private FileSelectorWidget fileSelector;
	private HTMLListItemWidget htmlItem;
	private RichTextToolbar toolbar;
	private IEditableSelectProperty property;
	private String oldValue = "";
	private static EditableSelectListItemWidgetUiBinder uiBinder = GWT
			.create(EditableSelectListItemWidgetUiBinder.class);

	interface EditableSelectListItemWidgetUiBinder extends
			UiBinder<Widget, EditableSelectListItemWidget> {
	}
	
	@UiField HTMLPanel panel;
	@UiField HTMLPanel editableValue;

	public EditableSelectListItemWidget() {
		initWidget(uiBinder.createAndBindUi(this));
	}
	
	public void setName(String name) {
		$(getRootElement()).find(".propertiesItem-Label").html(name);		
	}
	
	public void setValue(String[] options, String selectedOption) {
		boolean wasSelected = false;
		Element selectElement = getSelectElement();
		for (String key : options) {
			OptionElement option = Document.get().createOptionElement();
			option.setValue(key);
			option.setText(key);
			option.setSelected(selectedOption.equals(key));
			if (selectedOption.equals(key)) {
				wasSelected = true;
			}
			selectElement.appendChild(option);
		}
		
		if(!wasSelected) {
			if (options.length > 0) {
				this.property.setValue(options[0]);
				this.getSelectQueryElement().find(":first").attr("selected", "selected");
			}
		}
	}
	
	@Override
	public void setProperty (IProperty property) {
		this.property = ((IEditableSelectProperty)property);
		String[] options = new String[this.property.getChildrenCount()];
		for (int i = 0; i < this.property.getChildrenCount(); i++) {
			this.addWidgetElement(this.property.getChild(i).getDisplayName(), this.property.getChild(i));
			options[i] = this.property.getChild(i).getDisplayName();
		}
		
		if (this.property.getChildrenCount() > 0) {
			setValue(options, property.getValue());
			if (this.components.get(property.getValue()) != null) {
				this.editableValue.add((Composite)this.components.get(property.getValue()));
			} else {
				this.editableValue.add((Composite)this.components.get(options[0]));
			}
		}		
		this.setListener();
	}
	
	public void addWidgetElement (String key, final IProperty property) {
		IListItemWidget propertyWidget = null;
		
		String displayName = property.getDisplayName();
		if (displayName.equals("")) {
			displayName = property.getName();
		}
		
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
		} else if(property instanceof IEnumSetProperty) {
			propertyWidget = new SelectListItemWidget();
			propertyWidget.setName(displayName);
			propertyWidget.setProperty(property);
		}else {
			propertyWidget = new StringListItemWidget();
			propertyWidget.setName(displayName);
			propertyWidget.setProperty(property);
		}
		
		this.components.put(key, propertyWidget);
		
	}
	
	private GQuery getSelectQueryElement() {
		return $(getRootElement()).find(".propertiesItem-Value select");
	}
	
	private Element getSelectElement() {
		return (Element) getSelectQueryElement().get(0);
	}

	private Element getRootElement() {
		return panel.getElement();
	}
	
	public void setListener() {
		Element selectElement = getSelectElement();
		Event.sinkEvents(selectElement, Event.ONCHANGE);
		Event.setEventListener(selectElement, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCHANGE != event.getTypeInt()) {
					return;
				}
				if (components.containsKey(oldValue)) {
					components.get(oldValue).save();
				}
				editableValue.remove(0);
				editableValue.add((Composite)components.get(getSelectQueryElement().val()));
				
			}
		});
	}
	
	public void setFileEditor (FileSelectorWidget fileEditor) {
		this.fileSelector = fileEditor;
	}
	
	public void setHTMLEditor (HTMLListItemWidget htmlEditor) {
		this.htmlItem = htmlEditor;
	}
	
	public void setToolbar (RichTextToolbar toolbar) {
		this.toolbar = toolbar;
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

	@Override
	public void save() {
		this.property.setValue(this.getSelectQueryElement().val());
		for (Map.Entry<String,IListItemWidget> component : components.entrySet()) {
		    component.getValue().save();
		}
	}

	@Override
	public void reset() {
		this.getSelectQueryElement().val(this.property.getValue());		
	}

	@Override
	public boolean isModified() {
		if (this.property.getValue() != this.getSelectQueryElement().val()) {
			return true;
		}
		return components.get(getSelectQueryElement().val()).isModified();
	}
}
