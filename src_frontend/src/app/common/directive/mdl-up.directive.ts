import {
    Directive,
    AfterContentInit,
    ElementRef,
    Input,
    AfterViewChecked,
} from "@angular/core";

interface ComponentHandler {
    upgradeAllRegistered(): void;
}

declare const componentHandler: ComponentHandler;

@Directive({
    selector: "[mdlup]",
})
export class MDLUP implements AfterViewChecked {
    constructor(private readonly _element: ElementRef<HTMLElement>) {}

    @Input("mdlup") last: boolean = false;
    @Input("mdlup-always") always: boolean = false;

    /* FIXME
     * hard work-around, checks if it is last element
     */

    ngAfterViewChecked(): void {
        if (this.last) {
            componentHandler.upgradeAllRegistered();
            if (!this.always) {
                this.last = false;
            }
        }
    }
}
