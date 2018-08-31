import { NgModule } from '@angular/core';

import { SafeUrlPipe } from './pipes/safe-url/safe-url.pipe';

@NgModule({
    declarations: [SafeUrlPipe],
    exports: [SafeUrlPipe],
})
export class SharedModule {}
