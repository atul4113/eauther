import { Referrers } from "../../common/model/referrers";

export interface IGlobalSettingsRaw {
    referrers: Referrers;
}

export class GlobalSettings {
    referrers: Referrers;

    constructor (globalSettingsRaw: IGlobalSettingsRaw) {
        this.referrers = globalSettingsRaw.referrers;
    }
}
