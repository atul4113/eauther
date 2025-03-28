import { Component, EventEmitter, Input, OnInit, Output, OnChanges, SimpleChanges } from '@angular/core';

import { Category, ITranslations } from "../../../common/model";
import { TranslationsService } from "../../../common/service";

@Component({
  selector: 'app-categories-list',
  templateUrl: './categories-list.component.html'
})
export class CategoriesListComponent implements OnInit, OnChanges {
  @Input() categories: Category[] = [];
  @Input() shouldShowAddons: boolean = false;
  @Input() shouldShowTrash: boolean = false;
  @Input() currentSpaceId: number = 0;
  @Output() displayLessons = new EventEmitter<void>();

  public translations: ITranslations | null = null;
  public mainCategory: Category | null = null;
  public categoriesToDisplay: Category[] = [];

  constructor(
      private _translations: TranslationsService
  ) {}

  ngOnInit(): void {
      this._translations.getTranslations().subscribe((translations: ITranslations | null) => {
          if (translations) {
              this.translations = translations;
          }
      });
  }

  ngOnChanges(changes: SimpleChanges): void {
      if (this.categories) {
          this.mainCategory = this.categories.find(cat => cat.isTopLevel) || null;
          this.categoriesToDisplay = this.categories.filter(cat => !cat.isTopLevel);
      }
  }

  get mainCategoryId(): string {
      return this.mainCategory ? this.mainCategory.id.toString() : '';
  }

  public showLessons(): void {
      this.displayLessons.emit();
  }
}
