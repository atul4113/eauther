import { Directive, AfterContentInit } from '@angular/core';

declare var componentHandler: any;

@Directive({
    selector: '[mdl]'
})
export class MDL implements AfterContentInit {
    ngAfterContentInit() {
        componentHandler.upgradeAllRegistered();
    }
}
