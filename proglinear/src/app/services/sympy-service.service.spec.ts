import { TestBed } from '@angular/core/testing';

import { SympyServiceService } from './sympy-service.service';

describe('SympyServiceService', () => {
  let service: SympyServiceService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(SympyServiceService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
