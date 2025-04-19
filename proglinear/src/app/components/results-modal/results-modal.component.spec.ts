import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ResultsModalComponent } from './results-modal.component';

describe('ResultsModalComponent', () => {
  let component: ResultsModalComponent;
  let fixture: ComponentFixture<ResultsModalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ResultsModalComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ResultsModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
