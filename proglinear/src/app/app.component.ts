import { Component } from '@angular/core';
import { PlotlyComponent } from './components/plotly/plotly.component';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatInputModule} from '@angular/material/input';
import {MatIconModule} from '@angular/material/icon';
import * as math from 'mathjs';

@Component({
  selector: 'app-root',
  imports: [PlotlyComponent,ReactiveFormsModule,MatFormFieldModule, MatInputModule, MatIconModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'proglinear';

  restritionsForm: FormGroup;
  restritions: any[] = [{ id: 1 }]; 

  constructor(private fb: FormBuilder) {
    this.restritionsForm = this.fb.group({
      restrition_0: ""
    });
  }

  addRestrition() {
    const newEqIndex = this.restritions.length;
    this.restritions.push({ id: newEqIndex });

    this.restritionsForm.addControl(`restrition_${newEqIndex}`, this.fb.control(''));
  }

  removeRestrition(index: number) {
    this.restritions.splice(index, 1);
  
    this.restritionsForm.removeControl(`restrition_${index}`);
  
    this.restritions.forEach((eq, i) => {
      const oldKey = `restrition_${eq.id}`;
      const newKey = `restrition_${i}`;
  
      if (oldKey !== newKey) {
        const control = this.restritionsForm.get(oldKey);
        if (control) {
          this.restritionsForm.removeControl(oldKey);
          this.restritionsForm.addControl(newKey, control);
        }
      }
  
      eq.id = i;
    });
  }

  onSubmit() {
    let equations: any[] = [];

    Object.keys(this.restritionsForm.controls).forEach((key) => {
      const control = this.restritionsForm.get(key);  
      if (control && control.value) {
        const equation = control.value;

        const f = math.parse(equation);  
        const simp = math.simplify(f);   
        equations.push(simp);
      }
    });

  }
}
