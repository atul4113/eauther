import { Directive, AfterContentInit, ElementRef, Input, AfterViewChecked } from '@angular/core';

declare var componentHandler: any;

@Directive({
    selector: '[mdlup]'
})
export class MDLUP implements AfterViewChecked {
    constructor (private _element: ElementRef) { }

    @Input('mdlup') last: any;
    @Input('mdlup-always') always = false;

    /* FIXME
     * hard work-around, checks if it is last element
     */

    ngAfterViewChecked() {
        if (this.last) {
            componentHandler.upgradeAllRegistered();
            if (!this.always) {
                this.last = false;
            }
        }
    }
}
