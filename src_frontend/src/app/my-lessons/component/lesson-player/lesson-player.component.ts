import {Component, ElementRef, EventEmitter, Input, OnInit, Output, ViewChild} from '@angular/core';
import {DomSanitizer, SafeResourceUrl} from '@angular/platform-browser'

const CORPORATE_EMBED = '/embed/corporate_embed/'

declare const window:any;

@Component({
    selector: 'app-lesson-player',
    templateUrl: './lesson-player.component.html',
})
export class PlayerComponent implements OnInit {
    @Input() lessonId!: number;
    @Output() close = new EventEmitter<any>();
    @ViewChild('contentIframe') contentIframe!: ElementRef;
    @Input() main!: HTMLElement;

    public iframeUrl!: SafeResourceUrl;

    private MAX_WIDTH: number = 1100;
    private DELTA_WIDTH: number = 800;
    private iframe:any;
    private userAgent:any;
    private iframeWindow:any;
    private viewPort:any;

    constructor(private _sanitizer: DomSanitizer) {
    }

    public closeLesson() {
        this.close.emit();
    }

    handleResize(data:any) {
        let dimensions = data.split(';');
        let width = dimensions[0];
        let height = dimensions[1];
        if (window.mAuthor.ScreenUtils.isMobileUserAgent(this.userAgent)) {
            let screenSizes = window.mAuthor.ScreenUtils.getScreenSizesDependingOnOrientation(this.userAgent);
            this.viewPort.setAttribute('content', 'width=' + screenSizes.width);
            this.iframe.style.width = screenSizes.width;
            this.iframe.style.height = screenSizes.height;
        } else {
            this.viewPort.setAttribute('content', 'width=' + width);
            this.iframe.style.width = width;
            this.iframe.style.height = height;
        }
        let player_width = parseInt(this.iframe.style.width, 10);
        if (player_width > this.MAX_WIDTH) {
            this.main.style.width = (player_width + this.DELTA_WIDTH) + "px";
        }
    }

    getOffsetTopSum(elem:any) {
        let top = 0;
        while (elem) {
            top = top + parseFloat(elem.offsetTop);
            elem = elem.offsetParent;
        }
        return top;
    }

    onMessageReceived(event:any) {
        if (event.data.indexOf('RESIZE:') === 0 && !window.isStretchOrFullScreenMode) {
            this.handleResize(event.data.substring('RESIZE:'.length));
            this.postIFrameMessage(this.iframe.style.height);
        } else if (event.data.indexOf('PAGE_LOADED') === 0) {
            document.body.scrollTop = 0;
            this.postIFrameMessage(this.iframe.style.height);
            clearTimeout(window.resizedFinished);
            window.resizedFinished = setTimeout(() => {
                this.postIFrameMessage(this.iframe.style.height,);
            }, 250);
        }
    }

    postIFrameMessage(height:any) {
        let offset, scroll, windowInnerHeight, frameOffsetTop;
        offset = (window.pageYOffset || document.documentElement.scrollTop);
        frameOffsetTop = this.getOffsetTopSum(this.iframe);
        scroll = this.getOffsetTopSum(this.iframe) - 64;
        windowInnerHeight = window.innerHeight;
        let postObject = {
            offsetTop: offset,
            height: height,
            frameOffset: scroll,
            notScaledOffset: frameOffsetTop,
            windowInnerHeight: windowInnerHeight || 0
        };

        this.iframeWindow.postMessage('I_FRAME_SCROLL:' + offset, '*');
        this.iframeWindow.postMessage('I_FRAME_SIZES:' + JSON.stringify(postObject), '*');
    }

    postWindowWidth(data:any) {
        this.iframeWindow.postMessage("WINDOW_WIDTH:" + JSON.stringify(data), '*');
    }

    ngOnInit() {
        let url = window.location.origin + CORPORATE_EMBED + this.lessonId;
        this.iframeUrl = this._sanitizer.bypassSecurityTrustResourceUrl(url);
        this.iframe = this.contentIframe.nativeElement;

        this.viewPort = document.querySelector("meta[name=viewport]");
        this.iframeWindow = this.iframe.contentWindow || this.iframe.contentDocument;
        this.userAgent = window.navigator.userAgent;
        let screenSizes = window.mAuthor.ScreenUtils.getScreenSizesDependingOnOrientation(this.userAgent);
        this.iframe.style.width = screenSizes.width;
        this.iframe.style.height = screenSizes.height;

        window.addEventListener('message',
            (event:any) => {
                this.onMessageReceived(event)
            },
            false);

        window.addEventListener('scroll', () => {
            this.postIFrameMessage(this.iframe.style.height);
        });

        window.onresize = () => {
            let screenSizes = window.mAuthor.ScreenUtils.getScreenSizesDependingOnOrientation(this.userAgent);
            this.postWindowWidth(screenSizes.width);
            this.postIFrameMessage(screenSizes.height);
        };
    }
}
