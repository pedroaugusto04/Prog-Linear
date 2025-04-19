import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Calculation } from '../../models/Calculation';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { ResultsModalService } from './services/results-modal.service';

@Component({
  selector: 'app-results-modal',
  imports: [CommonModule, MatIconModule],
  templateUrl: './results-modal.component.html',
  styleUrl: './results-modal.component.scss'
})
export class ResultsModalComponent {

  constructor(
    @Inject(MAT_DIALOG_DATA) public modal: { valuesTested: Calculation[] },
    private resultsModalService: ResultsModalService
  ) {}

  closeDialog() {
    this.resultsModalService.closeDialog();
  }
}
