import { Component, EventEmitter, Input, OnInit, Output, OnChanges } from '@angular/core';

import { Category, ITranslations } from "../../../common/model";
import { TranslationsService } from "../../../common/service";

@Component({
  selector: 'app-categories-list',
  templateUrl: './categories-list.component.html'
})
export class CategoriesListComponent implements OnInit {

  @Input() categories: Category[];
  @Input() shouldShowAddons: boolean;
  @Input() shouldShowTrash: boolean;
  @Input() currentSpaceId: number;
  @Output() displayLessons = new EventEmitter<any>();

  public translations: ITranslations;
  public mainCategory: Category = null;
  public categoriesToDisplay: Category[];

  constructor(
      private _translations: TranslationsService
  ) {}

  ngOnInit() {
      this._translations.getTranslations().subscribe(t => this.translations = t);
  }

  ngOnChanges() {
      if(this.categories) {
          this.mainCategory = this.categories.filter(cat => cat.isTopLevel)[0];
          this.categoriesToDisplay = this.categories.filter(cat => !cat.isTopLevel);
      }
  }

  get mainCategoryId() {
      return this.mainCategory ? this.mainCategory.id : '';
  }

  public showLessons() {
      this.displayLessons.emit();
  }

}
