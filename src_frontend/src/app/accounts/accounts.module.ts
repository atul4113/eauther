import { AccountsRegisterFinishComponent } from "./component/accounts-register-finish/accounts-register-finish.component";
import { NgModule } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { RouterModule } from "@angular/router";
import { HttpClientModule } from "@angular/common/http";
import { CommonModule } from "@angular/common";

import { AppCommonModule } from "../common/app.common.module";
import { AccountsRoutes } from "./accounts.routes";
import { AccountsRegisterComponent } from "./component/accounts-register/accounts-register.component";

@NgModule({
    imports: [
        CommonModule,
        FormsModule,
        RouterModule,
        HttpClientModule,
        AppCommonModule,
        RouterModule.forChild(AccountsRoutes),
    ],
    declarations: [AccountsRegisterComponent, AccountsRegisterFinishComponent],
})
export class AccountsModule {}
