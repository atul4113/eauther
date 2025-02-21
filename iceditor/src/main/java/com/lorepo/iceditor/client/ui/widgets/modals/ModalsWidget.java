package com.lorepo.iceditor.client.ui.widgets.modals;

import static com.google.gwt.query.client.GQuery.$;

import java.util.Collection;
import java.util.List;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.DivElement;
import com.google.gwt.dom.client.Style.Display;
import com.google.gwt.event.dom.client.KeyCodes;
import com.google.gwt.event.dom.client.KeyDownEvent;
import com.google.gwt.event.dom.client.KeyDownHandler;
import com.google.gwt.event.shared.HandlerRegistration;
import com.google.gwt.query.client.Function;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.RootPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.ui.widgets.modals.semi.responsive.AddNewSemiResponsiveLayout;
import com.lorepo.iceditor.client.ui.widgets.modals.semi.responsive.AddNewStyle;
import com.lorepo.iceditor.client.ui.widgets.modals.semi.responsive.AddNewStyleWidget;
import com.lorepo.iceditor.client.ui.widgets.modals.semi.responsive.AddSemiResponsiveLayoutWidget;
import com.lorepo.iceditor.client.ui.widgets.modals.semi.responsive.PageLayoutData;
import com.lorepo.iceditor.client.ui.widgets.modals.semi.responsive.SetSemiResponsiveLayoutCSSStyle;
import com.lorepo.iceditor.client.ui.widgets.modals.semi.responsive.SetSemiResponsiveLayoutCSSStyleWidget;
import com.lorepo.iceditor.client.ui.widgets.utils.MainPageUtils;
import com.lorepo.icplayer.client.model.CssStyle;

public class ModalsWidget extends Composite {

	private static ModalsWidgetUiBinder uiBinder = GWT
			.create(ModalsWidgetUiBinder.class);

	interface ModalsWidgetUiBinder extends UiBinder<Widget, ModalsWidget> {
	}
	
	@UiField HTMLPanel wrapper;
	@UiField HTMLPanel container;
	@UiField DivElement closeBtn;
	
	private String promptValue;
	private SingleGapWidget singleGapWidget;
	private SingleFilledGapWidget singleFilledGapWidget;
	private DropDownGapWidget dropDownGapWidget;
	private PromptWidget questionBox;
	private HandlerRegistration handler;
	private AddNewStyleWidget addNewStyleWidget;
	private AddSemiResponsiveLayoutWidget addSemiResponsiveLayoutWidget;
	private SetSemiResponsiveLayoutCSSStyleWidget setSemiResponsiveLayoutCSSStyleWidget;
	private ImageAltTextWidget imageAltTextWidget;
	private AltTextWidget altTextWidget;

	public ModalsWidget() {
		this.initWidget(uiBinder.createAndBindUi(this));
		
		this.wrapper.getElement().setId("modalWrapper");
		this.hide();
	}
	
	private void hide() {
		this.wrapper.getElement().getStyle().setDisplay(Display.NONE);
		if (this.handler != null) {
			this.removeHandlers();
		}
	}
	
	public void addModal(String message, final QuestionModalListener listener) {
		final ModalQuestionBoxWidget questionBox = new ModalQuestionBoxWidget();
		questionBox.setMessage(message);
		questionBox.setListener(new QuestionModalListener() {
			@Override
			public void onDecline() {
				hide();
				listener.onDecline();
				container.remove(questionBox);
				ModalsWidget.this.container.remove(questionBox);
				ModalsWidget.this.hide();
			}
			
			@Override
			public void onAccept() {
				hide();
				ModalsWidget.this.container.remove(questionBox);
				ModalsWidget.this.hide();
				listener.onAccept();
			}
		});

		this.container.add(questionBox);

		this.wrapper.getElement().getStyle().setDisplay(Display.BLOCK);
		this.addHandlers(questionBox, listener, false);
	}
	
	
	public void addModalSingleButton(String message, final SingleButtonModalListener listener) {
		final SingleButtonWidget questionBox = new SingleButtonWidget();
		questionBox.setMessage(message);
		questionBox.setListener(new SingleButtonModalListener() {
		
			public void onAccept() {
				hide();
				listener.onAccept();
				ModalsWidget.this.container.remove(questionBox);
				ModalsWidget.this.hide();
			}
		});

		this.container.add(questionBox);

		this.wrapper.getElement().getStyle().setDisplay(Display.BLOCK);
		this.addHandlersSingleButton(questionBox, listener);
	}

	private void addHandlersSingleButton(final Widget widget, final SingleButtonModalListener listener) {
		setVisible(this.closeBtn, false);

		this.handler = RootPanel.get().addDomHandler(new KeyDownHandler() {
			@Override
	        public void onKeyDown(KeyDownEvent event) {
				if (ModalsWidget.this.wrapper.isVisible()) {
					
					if (event.getNativeKeyCode() == KeyCodes.KEY_ENTER) {
						listener.onAccept();
						ModalsWidget.this.container.remove(widget);
						ModalsWidget.this.hide();
						
					}
				}
			}
		}, KeyDownEvent.getType());
	}

	public void addNewStyle(final AddNewStyle listener) {
		this.addNewStyleWidget = new AddNewStyleWidget();

		final AddNewStyle modalListener = new AddNewStyle() {
			@Override
			public void onDecline() {
				listener.onDecline();
				container.remove(addNewStyleWidget);
				hide();
			}

			@Override
			public void onAddStyle(CssStyle addedStyle) {
				listener.onAddStyle(addedStyle);
				container.remove(addNewStyleWidget);
				hide();
			}
		};
		
		this.addNewStyleWidget.setListener(modalListener);
		this.container.add(this.addNewStyleWidget);
		this.wrapper.getElement().getStyle().setDisplay(Display.BLOCK);

		QuestionModalListener listenerWrapper = new QuestionModalListener() {
			@Override
			public void onDecline() {
				modalListener.onDecline();
			}

			@Override
			public void onAccept() {
				String cssStyleName = addNewStyleWidget.getStyleName();
				CssStyle justCreatedStyle = CssStyle.createNewStyle(cssStyleName);
				listener.onAddStyle(justCreatedStyle);
			}
		};

		this.addHandlers(this.addNewStyleWidget, listenerWrapper, true);
	}
	

	public void addNewSemiResponsiveLayout( final AddNewSemiResponsiveLayout listener) {
		this.addSemiResponsiveLayoutWidget = new AddSemiResponsiveLayoutWidget();

		final AddNewSemiResponsiveLayout modalListener = new AddNewSemiResponsiveLayout() {
			@Override
			public void onDecline() {
				listener.onDecline();
				container.remove(addSemiResponsiveLayoutWidget);
				hide();
			}

			@Override
			public void onAddNewSemiResponsiveLayout(PageLayoutData pageLayoutData) {
				listener.onAddNewSemiResponsiveLayout(pageLayoutData);
				container.remove(addSemiResponsiveLayoutWidget);
				hide();
			}
		};

		this.addSemiResponsiveLayoutWidget.setListener(modalListener);
		this.container.add(this.addSemiResponsiveLayoutWidget);
		this.wrapper.getElement().getStyle().setDisplay(Display.BLOCK);

		QuestionModalListener listenerWrapper = new QuestionModalListener() {
			@Override
			public void onDecline() {
				modalListener.onDecline();
			}

			@Override
			public void onAccept() {
				PageLayoutData data = addSemiResponsiveLayoutWidget.getLayoutData();
				listener.onAddNewSemiResponsiveLayout(data);
			}
		};

		this.addHandlers(this.addSemiResponsiveLayoutWidget, listenerWrapper, true);
	}


	public void setCSSStyleForSemiResponsive(Collection<CssStyle> styles, final SetSemiResponsiveLayoutCSSStyle listener) {
		this.setSemiResponsiveLayoutCSSStyleWidget = new SetSemiResponsiveLayoutCSSStyleWidget();
		this.setSemiResponsiveLayoutCSSStyleWidget.setCssStyles(styles);

		final SetSemiResponsiveLayoutCSSStyle modalListener = new SetSemiResponsiveLayoutCSSStyle() {
			@Override
			public void onDecline() {
				listener.onDecline();
				container.remove(setSemiResponsiveLayoutCSSStyleWidget);
				hide();
			}

			@Override
			public void onSetSemiResponsiveLayoutCSSStyle(String styleID) {
				listener.onSetSemiResponsiveLayoutCSSStyle(styleID);
				container.remove(setSemiResponsiveLayoutCSSStyleWidget);
				hide();
			}
		};

		this.setSemiResponsiveLayoutCSSStyleWidget.setListener(modalListener);
		this.container.add(this.setSemiResponsiveLayoutCSSStyleWidget);
		this.wrapper.getElement().getStyle().setDisplay(Display.BLOCK);

		QuestionModalListener listenerWrapper = new QuestionModalListener() {
			@Override
			public void onDecline() {
				modalListener.onDecline();
			}

			@Override
			public void onAccept() {
				String data = setSemiResponsiveLayoutCSSStyleWidget.getStyleID();
				listener.onSetSemiResponsiveLayoutCSSStyle(data);
			}
		};

		this.addHandlers(this.setSemiResponsiveLayoutCSSStyleWidget, listenerWrapper, true);
	}

	public void addPrompt(String value, String[] textContent, final QuestionModalListener listener) {
		this.questionBox = new PromptWidget();
		this.questionBox.setTextContent(textContent);
		this.questionBox.setMessage(textContent[2]);
		this.questionBox.setPromptValue(value);
		this.questionBox.setListener(new QuestionModalListener() {
			@Override
			public void onDecline() {
				listener.onDecline();
				ModalsWidget.this.container.remove(ModalsWidget.this.questionBox);
				ModalsWidget.this.hide();
			}

			@Override
			public void onAccept() {
				String promptValue = ModalsWidget.this.questionBox.getPromptValue();
				ModalsWidget.this.setPromptValue(promptValue);
				listener.onAccept();
				ModalsWidget.this.container.remove(ModalsWidget.this.questionBox);
				ModalsWidget.this.hide();
			}
		});
		
		this.container.add(this.questionBox);
		this.wrapper.getElement().getStyle().setDisplay(Display.BLOCK);
		this.questionBox.heightValue.focus();
		

		QuestionModalListener listenerDecorator = new QuestionModalListener() {

			@Override
			public void onAccept() {
				String promptValue = ModalsWidget.this.questionBox.getPromptValue();
				ModalsWidget.this.setPromptValue(promptValue);
				listener.onAccept();
			}

			@Override
			public void onDecline() {
				listener.onDecline();
			}
		};
		this.addHandlers(this.questionBox, listenerDecorator, true);
	}
	
	public void addSingleGapWidget(String mode, List<String> values, final QuestionModalListener listener) {
		this.singleGapWidget = new SingleGapWidget(mode, values);
		this.singleGapWidget.setListener(new QuestionModalListener() {
			@Override
			public void onDecline() {
				listener.onDecline();
				ModalsWidget.this.container.remove(ModalsWidget.this.singleGapWidget);
				ModalsWidget.this.hide();
			}
			
			@Override
			public void onAccept() {
				listener.onAccept();
				ModalsWidget.this.container.remove(ModalsWidget.this.singleGapWidget);
				ModalsWidget.this.hide();
			}
		});
		
		this.container.add(this.singleGapWidget);
		this.wrapper.getElement().getStyle().setDisplay(Display.BLOCK);
		this.addHandlers(this.singleGapWidget, listener, true);
		this.singleGapWidget.setFocus();
		this.singleGapWidget.addSortableItems();
		MainPageUtils.addScrollBar(".gapItemsList");
	}
	
	public void addSingleFilledGapWidget(String mode, List<String> values, final QuestionModalListener listener) {
		this.singleFilledGapWidget = new SingleFilledGapWidget(mode, values);
		this.singleFilledGapWidget.setListener(new QuestionModalListener() {
			@Override
			public void onDecline() {
				listener.onDecline();
				ModalsWidget.this.container.remove(ModalsWidget.this.singleFilledGapWidget);
				ModalsWidget.this.hide();
			}
			
			@Override
			public void onAccept() {
				listener.onAccept();
				ModalsWidget.this.container.remove(ModalsWidget.this.singleFilledGapWidget);
				ModalsWidget.this.hide();
			}
		});
		
		this.container.add(this.singleFilledGapWidget);
		this.wrapper.getElement().getStyle().setDisplay(Display.BLOCK);
		this.addHandlers(this.singleFilledGapWidget, listener, true);
		this.singleFilledGapWidget.setFocus();
		MainPageUtils.addScrollBar(".gapItemsList");
	}
	
	public void addAltTextWidget(String mode, List<String> values, final QuestionModalListener listener) {
		this.altTextWidget = new AltTextWidget(values);
		this.altTextWidget.setListener(new QuestionModalListener() {
			@Override
			public void onDecline() {
				listener.onDecline();
				ModalsWidget.this.container.remove(ModalsWidget.this.altTextWidget);
				ModalsWidget.this.hide();
			}
			
			@Override
			public void onAccept() {
				listener.onAccept();
				ModalsWidget.this.container.remove(ModalsWidget.this.altTextWidget);
				ModalsWidget.this.hide();
			}
		});
		
		this.container.add(this.altTextWidget);
		this.wrapper.getElement().getStyle().setDisplay(Display.BLOCK);
		this.addHandlers(this.altTextWidget, listener, true);
		this.altTextWidget.setFocus();
	}
	
	public void addDropDownGapWidget(String moduleTypeName, String mode, List<String> values, final QuestionModalListener listener) {
		this.dropDownGapWidget = new DropDownGapWidget(mode, values);
		this.dropDownGapWidget.setListener(new QuestionModalListener() {
			@Override
			public void onDecline() {
				listener.onDecline();
				ModalsWidget.this.container.remove(ModalsWidget.this.dropDownGapWidget);
				ModalsWidget.this.hide();
			}
			
			@Override
			public void onAccept() {
				listener.onAccept();
				ModalsWidget.this.container.remove(ModalsWidget.this.dropDownGapWidget);
				ModalsWidget.this.hide();
			}
		});
		
		this.dropDownGapWidget.init();
		this.container.add(this.dropDownGapWidget);
		this.wrapper.getElement().getStyle().setDisplay(Display.BLOCK);
		this.addHandlers(this.dropDownGapWidget, listener, true);
		this.dropDownGapWidget.addSortableItems();
		this.dropDownGapWidget.setFocus();
		
		this.dropDownGapWidget.setModuleTypeName(moduleTypeName);
		MainPageUtils.addScrollBar(".gapItemsList");
	}
	
	private void removeHandlers() {
		this.handler.removeHandler();
		$(this.closeBtn).off("click");
	}
	
	private void addHandlers(final Widget widget, final QuestionModalListener listener, final boolean isCancelBtn) {
		$(this.closeBtn).on("click", new Function() {
			@Override
			public void f() {
				if (isCancelBtn) {
					listener.onDecline();
				}

				ModalsWidget.this.container.remove(widget);
				ModalsWidget.this.hide();
			 }
		});
		
		this.handler = RootPanel.get().addDomHandler(new KeyDownHandler() {
			@Override
	        public void onKeyDown(KeyDownEvent event) {
				if (ModalsWidget.this.wrapper.isVisible()) {
					if (event.getNativeKeyCode() == KeyCodes.KEY_ESCAPE) {
						if (isCancelBtn) {
							listener.onDecline();
						}
						
						ModalsWidget.this.container.remove(widget);
						ModalsWidget.this.hide();
					} else if (event.getNativeKeyCode() == KeyCodes.KEY_ENTER) {
						listener.onAccept();
						ModalsWidget.this.container.remove(widget);
						ModalsWidget.this.hide();
						
					}
				}
			}
		}, KeyDownEvent.getType());
	}
	
	private void setPromptValue(String value) {
		this.promptValue = value;
	}
	
	public String getPromptValue() {
		return this.promptValue;
	}	
	
	public SingleGapWidget getSingleGapWidget() {
		return this.singleGapWidget;
	}
	
	public SingleFilledGapWidget getSingleFilledGapWidget() {
		return this.singleFilledGapWidget;
	}
	
	public DropDownGapWidget getDropDownGapWidget() {
		return this.dropDownGapWidget;
	}
	
	public AltTextWidget getAltTextWidget() {
		return this.altTextWidget;
	}
	
	public void addImageAltTextWidget(String value, final QuestionModalListener listener) {
		this.imageAltTextWidget = new ImageAltTextWidget(value);
		this.imageAltTextWidget.setListener(new QuestionModalListener() {
			@Override
			public void onDecline() {
				listener.onDecline();
				ModalsWidget.this.container.remove(ModalsWidget.this.imageAltTextWidget);
				ModalsWidget.this.hide();
			}
			
			@Override
			public void onAccept() {
				listener.onAccept();
				ModalsWidget.this.container.remove(ModalsWidget.this.imageAltTextWidget);
				ModalsWidget.this.hide();
			}
		});
		
		this.container.add(this.imageAltTextWidget);
		this.wrapper.getElement().getStyle().setDisplay(Display.BLOCK);
		this.addHandlers(this.imageAltTextWidget, listener, true);
		this.imageAltTextWidget.setFocus();
	}
	
	public ImageAltTextWidget getImageAltTextWidget(){
		return this.imageAltTextWidget;
	}
}
