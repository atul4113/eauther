import {
    Component, Input, Output, AfterViewInit, OnDestroy, EventEmitter, NgZone, OnInit, OnChanges
} from "@angular/core";


declare let tinymce: any;
declare function getDoc(): any;
declare let document: Document;

@Component({
    selector: 'tiny-mce',
    template: '<textarea id="tiny-mce-{{ id }}"></textarea>'
})
export class TinyMCEComponent implements OnInit, AfterViewInit, OnDestroy, OnChanges {
    @Input() id: string;
    @Input() value: string;
    @Input() submitOptions: any;
    @Input() formatSelect: boolean = true;

    @Output() valueChange = new EventEmitter<string>();

    private editor: any;
    private _value: string;

    constructor (private _zone: NgZone) {}

    ngOnInit () {
        this.id = this.id + '_' + (new Date()).getTime();
    }

    ngAfterViewInit () {
        const intervalId = setInterval( () => {
            const textAreaElement = document.getElementById(`tiny-mce-${this.id}`);
            if (textAreaElement) {
                clearInterval(intervalId);
                this.init();
            }
        }, 100);
    }

    doOnChange () {
        if (this.editor) {
            this._value = this.editor.getContent();
            this.value = this._value;
            this.valueChange.emit(this.value);
        }
    }

    ngOnChanges (changes: any) {
        if (this.editor && this.value !== this._value) {
            this.editor.setContent(this.value || '');
        }
    }

    ngOnDestroy () { // FIXME error on browser back button on edit collection details view
        // this.editor.destroy();
        // tinymce.remove();
        this.editor = null;
    }

    private init () {
        tinymce.init({
            selector: '#tiny-mce-' + this.id,
            height: 250,
            menubar: 'insert table tools',
            resize: false,
            skin: 'lightgray',
            statusbar: false,
            plugins: 'emoticons',
            toolbar: 'undo redo | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist' + (this.formatSelect ? ' | formatselect' : '')  + ' | fontsizeselect | emoticons | submit',
            fontsize_formats: '8pt 10pt 12pt 14pt 18pt 24pt 30pt 36pt',
            setup: (editor) => {
                editor.on('keyup change', () => {
                    this._zone.run(() => {
                        this.doOnChange();
                    });
                });
                editor.on('init', () => {
                    editor.getDoc().body.style.fontSize = '16px';
                });
                if (this.submitOptions) {
                    editor.addButton('submit', {
                        text: this.submitOptions.text,
                        icon: false,
                        onclick: () => {
                            this.submitOptions.callback();
                        }
                    });
                }
            }
        }).then((editors => {
            this.editor = editors[0];
            if (this.editor) {
                this.editor.setContent(this.value || '');
            }
        }));
    }
}
