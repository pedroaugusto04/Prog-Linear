import { TestBed } from '@angular/core/testing';

import { ResultsModalService } from './results-modal.service';

describe('ResultsModalService', () => {
  let service: ResultsModalService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ResultsModalService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
