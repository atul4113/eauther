import { Referrers } from "../../common/model/referrers";

export interface IGlobalSettingsRaw {
    referrers: Referrers;
}

export class GlobalSettings {
    readonly referrers: Referrers;

    constructor(globalSettingsRaw: IGlobalSettingsRaw) {
        if (!globalSettingsRaw) {
            throw new Error("Global settings data is required");
        }
        this.referrers = globalSettingsRaw.referrers;
    }
}
