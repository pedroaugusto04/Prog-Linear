import sys

from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
import sympy as sp


@api_view(['POST'])
def solveLinearEquation(request):
    equacoes_str = request.data.get("equacoes", [])

    if not equacoes_str:
        return Response({"erro": "Nenhuma equação fornecida."}, status=400)

    try:
        respostas = []

        for eq_str in equacoes_str:
            lhs, rhs = eq_str.split('=')
            lhs_expr = sp.sympify(lhs)
            rhs_expr = sp.sympify(rhs)

            equacao = sp.Eq(lhs_expr, rhs_expr)

            variaveis = list(lhs_expr.free_symbols.union(rhs_expr.free_symbols))

            pontos = []

            if len(variaveis) >= 2:
                x, y = variaveis[:2]

                for y_val in [0, 5]:
                    eq_substituida = equacao.subs(y, y_val)
                    x_val = sp.solve(eq_substituida, x)
                    if x_val:
                        pontos.append({str(x): x_val[0], str(y): y_val})
            else:
                var = variaveis[0]
                val = sp.solve(equacao, var)
                if val:
                    pontos.append({str(var): val[0], 'r': sys.maxsize})
                    pontos.append({str(var): val[0], 'r': -sys.maxsize})

            respostas.append(f"Pontos: {pontos}")

        return Response({"respostas": respostas})

    except Exception as e:
        return Response({"erro": f"Erro ao processar equações: {str(e)}"}, status=500)
