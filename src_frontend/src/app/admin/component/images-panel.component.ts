import { Component, OnInit } from '@angular/core';
import { InfoMessageService } from "../../common/service/info-message.service";

@Component({
    templateUrl: '../templates/images-panel.component.html'
})
export class ImagesPanelComponent implements OnInit {
    constructor(
        //private _translations: TranslationsService,
        private _infoMessage: InfoMessageService
    ) {}

    ngOnInit(): void {
        // TODO: Implement image panel functionality
    }
}
