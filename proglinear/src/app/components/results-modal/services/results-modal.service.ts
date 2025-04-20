import { Injectable } from '@angular/core';
import { MatDialog } from "@angular/material/dialog";
import { ResultsModalComponent } from '../results-modal.component';
import { Calculation } from '../../../models/Calculation';


@Injectable({
  providedIn: 'root'
})
export class ResultsModalService {

  constructor(private dialog: MatDialog) { }

  openDialog(valuesTested: Calculation[], isGraphical: boolean) {
    this.dialog.open(ResultsModalComponent, {
      data: {valuesTested,isGraphical},
      width: "90%",
      height: "95%",
    });
  }

  closeDialog() {
    this.dialog.closeAll();
  }
}
