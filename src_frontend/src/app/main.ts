import { enableProdMode } from "@angular/core";
import { platformBrowserDynamic  } from '@angular/platform-browser-dynamic';
import 'rxjs/Rx';

import { AppModule } from './app.module';


enableProdMode();
platformBrowserDynamic().bootstrapModule(AppModule);

/// <reference path="./declarations.d.ts" />
