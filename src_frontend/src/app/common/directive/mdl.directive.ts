import { Directive, AfterContentInit } from "@angular/core";

interface ComponentHandler {
    upgradeAllRegistered(): void;
}

declare const componentHandler: ComponentHandler;

@Directive({
    selector: "[mdl]",
})
export class MDL implements AfterContentInit {
    ngAfterContentInit(): void {
        componentHandler.upgradeAllRegistered();
    }
}
