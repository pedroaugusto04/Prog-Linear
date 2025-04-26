import { CommonModule } from '@angular/common';
import { Component, Input, OnChanges, OnInit, SimpleChanges } from '@angular/core';
import { PlotlyModule } from 'angular-plotly.js';
import { number } from 'mathjs';
import * as PlotlyJS from 'plotly.js-dist-min';
import { BreakpointObserver } from "@angular/cdk/layout";

PlotlyModule.plotlyjs = PlotlyJS;

@Component({
  selector: 'app-plotly',
  standalone: true,
  imports: [PlotlyModule, CommonModule],
  templateUrl: './plotly.component.html',
  styleUrl: './plotly.component.scss'
})
export class PlotlyComponent implements OnChanges, OnInit {
  
  @Input() points: number[][] = [];
  @Input() intersections: number[][] = [];
  @Input() axisRange!: any;

  isMobile: boolean = false;

  constructor(private mobileObserver: BreakpointObserver) {}

  ngOnInit() {
    this.mobileObserver.observe(['(max-width: 1000px)']).subscribe((screenSize) => {
      if (screenSize.matches) {
        this.isMobile = true;
      } else {
        this.isMobile = false;
      }

      this.graph.layout = {
        ...this.graph.layout,
        width: this.isMobile ? 410 : 1000,
        height: this.isMobile ? 410 : 600,
      };
    });
  }

  public graph: { data: { x: number[], y: number[], mode: string }[]; layout: any } = {
    data: [],
    layout: {
      width: 1000,
      height: 600,
      title: { text: 'Resultados: Método Gráfico' },
      xaxis: {
        title: 'x',
        autorange: false,
        autoscale: false
      },
      yaxis: {
        title: 'y',
        autorange: false,
        autoscale: false
      },
    }
  };

  public graphConfig = {
    modeBarButtonsToRemove: ['autoScale2d']
  };

  ngOnChanges(changes: SimpleChanges) {

    this.graph.data = [];

    if (changes['points']) {
      this.gerarTracos();
    }

    if (changes['intersections']) {
      this.gerarIntersecoes();
    }

    if (changes['axisRange']) {
      this.updateRange();
    }
  }

  gerarTracos() {

    // o primeiro conjunto de pontos eh da equacao a ser maximizada, nao deve colocar no grafico 

    for (let i = 1; i < this.points.length; i ++) {

      const [x0, y0, x1, y1] = this.points[i];

      const trace = {
        x: [x0,x1],  
        y: [y0,y1],  
        mode: 'lines',
        name: `Reta ${i}`,
      };

      this.graph.data.push(trace);
    }
  

    this.graph.data = this.graph.data.filter(trace => Object.keys(trace).length > 0);
  }

  gerarIntersecoes() {

    let indexValidIntersection = 1;

    for (let i = 0; i < this.intersections.length; i++) {
        const [x, y, isValid] = this.intersections[i];

        if (!isValid) continue;
        
        const trace = {
            x: [x],  
            y: [y],  
            mode: 'markers',  
            type: 'scatter', 
            name: `Interseção ${indexValidIntersection}`,
            marker: {
                color: 'blue', 
                size: 8       
            }
        };

        indexValidIntersection++;

        this.graph.data.push(trace);
    }

    this.graph.data = this.graph.data.filter(trace => Object.keys(trace).length > 0);
  }

  updateRange() {
    if (!this.axisRange) return;

    this.graph.layout = {
      ...this.graph.layout,
      xaxis: {
        ...this.graph.layout.xaxis,
        range: [this.axisRange.minX - 10,this.axisRange.maxX + 10]
      },
      yaxis: {
        ...this.graph.layout.yaxis,
        range: [this.axisRange.minY - 10,this.axisRange.maxY + 10]
      },
    };
  }
  
}
