import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { PlotlyModule } from 'angular-plotly.js';
import * as PlotlyJS from 'plotly.js-dist-min';

PlotlyModule.plotlyjs = PlotlyJS;


@Component({
  selector: 'app-plotly',
  imports: [PlotlyModule, CommonModule],
  templateUrl: './plotly.component.html',
  styleUrl: './plotly.component.scss'
})
export class PlotlyComponent {

   trace1 = {
    x: [2, 3],
    y: [16, 5],
    mode: 'lines'
  };
  trace2 = {
    x: [3,9],
    y: [1,6],
    mode: 'lines'
  };


  public graph = {
    data: [
        this.trace1,this.trace2,
    ],
    layout: {width: 600, height: 600, title: {text: 'Resultados: Método Gráfico'}}
  };
}
