import os
import sys

from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from sympy import symbols, Eq, solve, Matrix,Le,Ge,Lt,Gt,oo
from dotenv import load_dotenv
from pathlib import Path
from scipy.optimize import linprog


if os.getenv("ENV") != "production":
    load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / '.env')

@api_view(['GET'])
def ping(request):
    return Response("API Online")

@api_view(['POST'])
def findPoints(request):

    MAX_LEN_TO_BE_2D = 5

    is2D = True

    equacoes_str = request.data.get("equacoes", [])

    num_colunas = len(equacoes_str[0][0])

    # associa cada indice aos valores da eq correspondente
    equacoes_map = {i: [] for i in range(num_colunas)}

    for linha in equacoes_str[0]:
        for i, valor in enumerate(linha):
            equacoes_map[i].append(valor)

    for linha in equacoes_str[1]:
        for i,valor in enumerate(linha):
            equacoes_map[i].append(valor)

    for index,linha in enumerate(equacoes_str[2]):
        for i,valor in enumerate(linha):
            equacoes_map[index].insert(-1,valor)

    max_len = max(len(valores) for valores in equacoes_map.values())

    if max_len > MAX_LEN_TO_BE_2D:
        is2D = False

    # aplica o sinal da operacao
    for i in equacoes_map.keys():
        lista = equacoes_map[i]
        indexStart = 0
        indexOpStart = int((len(lista)/2)-1)
        indexOpEnd = len(lista) - 2

        if lista[indexOpEnd] == '-':
            lista[indexOpEnd+1] = -lista[indexOpEnd+1]
        while indexOpStart < indexOpEnd and isinstance(lista[indexStart], (int, float)):
            valorOp = lista[indexOpStart]
            if valorOp == '-':
                lista[indexStart] = -lista[indexStart]
            indexStart += 1
            indexOpStart += 1

    points = []
    intersections = []
    equations = []
    inequations = []
    valuesTested = []
    index_equal_simplex = set()

    # monta o sistema de  inequacoes para verificacao das intersecoes
    for i in equacoes_map.keys():
        if i == 0: continue # nao processa a primeira ( a primeira eh o que queremos maximizar )

        lista = equacoes_map[i]

        if lista[len(lista)-2] == '<':
            lista[len(lista)-2] = '<='
        elif lista[len(lista)-2] == '>=' or lista[len(lista)-2] == '>':
            for index,value in enumerate(lista):
                if not isinstance(value, (int, float)): continue
                lista[index] = -value

        if lista[len(lista)-2] != "=":
            lista[len(lista) - 2] = '<='
        else:
            index_equal_simplex.add(i)

        if max_len <= MAX_LEN_TO_BE_2D:
            vars = symbols(f'x1:{int((max_len)/2)+1}')

            lhs = 0

            for index,var in enumerate(vars):
                lhs += float(lista[index]) * var

            rhs = lista[len(lista)-1]

            op2 = lista[len(lista) -2]

            if op2 == '=':
                inequations.append(Eq(lhs, rhs))
            elif op2 == '<=':
                inequations.append(Le(lhs, rhs))
            elif op2 == '>=':
                inequations.append(Ge(lhs, rhs))
            elif op2 == '<':
                inequations.append(Lt(lhs, rhs))
            elif op2 == '>':
                inequations.append(Gt(lhs, rhs))

    # busca as equacoes (ate 2d)
    if max_len <= MAX_LEN_TO_BE_2D:
        for i in equacoes_map.keys():
            lista = equacoes_map[i]

            vars = symbols(f'x1:{int((max_len)/2)+1}')

            A = Matrix([lista[:len(vars)]])
            b = Matrix([lista[len(lista) -1]])

            solution = solve(A * Matrix(vars) - b, vars)

            if i != 0:
                for var in solution:
                    equations.append(Eq(var, solution[var]))

            # verifica 2 pontos para formar o grafico ( no caso de ate 2 variaveis )
            if lista[0] != 0: # x != 0
                if not solution: continue

                x1,x2 = symbols('x1 x2')

                x_expr = solution[x1]
                y1v = float(os.getenv("MIN_VAR", "-100")) # first point
                y2v = float(os.getenv("MAX_VAR", "100")) # second point

                x1v = float(x_expr.subs(x2, y1v))
                x2v = float(x_expr.subs(x2,y2v))
                points.append([x1v, y1v, x2v, y2v])
            else:
                if not solution: continue

                y_expr = solution[x2]
                x1v = float(os.getenv("MIN_VAR", "-100")) # first point
                x2v = float(os.getenv("MAX_VAR", "100")) # second point

                y1v = float(y_expr.subs(x1,x1v))
                y2v = float(y_expr.subs(x1, x2v))
                points.append([x1v, y1v, x2v, y2v])



    # resolve as inequacoes ( ate 2d)
    if max_len <= MAX_LEN_TO_BE_2D:
        for i in range(len(equations)):
            for j in range(i + 1, len(equations)):
                if equations[i] == equations[j]: continue
                sol = solve((equations[i], equations[j]), vars)
                if sol:
                    intersections.append([float(sol[v]) for v in vars] + [True])


    # verifica quais intersecoes sao validas ( respeitam as inequacoes e quais nao - ate 2d )
    if max_len <= MAX_LEN_TO_BE_2D:
        for inequation in inequations:
            for intersection in intersections:
                value = {x1: intersection[0],x2: intersection[1]}

                valid = inequation.subs(value)

                if not valid:
                    intersection[2] = False


    # recupera funcao que o usuario deseja otimizar
    if max_len <= MAX_LEN_TO_BE_2D:
        listaFuncaoOtimiza = equacoes_map[0]

        vars = symbols(f'x1:{int((max_len)/2)+1}')

        funcaoOtimiza = 0

        for index,var in enumerate(vars):
            funcaoOtimiza += listaFuncaoOtimiza[index] * var

    maxResult = -sys.maxsize
    maxResultX = -sys.maxsize
    maxResultY = -sys.maxsize

    minResult = sys.maxsize
    minResultX = -sys.maxsize
    minResultY = -sys.maxsize

    minAxisX = sys.maxsize
    maxAxisX = -sys.maxsize

    minAxisY = sys.maxsize
    maxAxisY = -sys.maxsize


    maxXSimplex = []
    minXSimplex = []

    if max_len > MAX_LEN_TO_BE_2D:
        A_simplex = []
        B_simplex = []
        C_simplex = []
        A_Eq_Simplex = []
        B_Eq_Simplex = []

        for index,value in enumerate(equacoes_map[0]):
            if not isinstance(value, (int, float)): continue
            if index == len(equacoes_map[0]) -1: break
            C_simplex.append(value)

        i_ub = 0
        i_eq = 0
        for i in equacoes_map.keys():
            if i == 0: continue  # Não processa a primeira (a primeira é o que queremos maximizar)

            lista = equacoes_map[i]
            coef = []

            for index, value in enumerate(lista):
                if isinstance(value, (int, float)):
                    if index == len(lista) - 1:
                        b = value
                    else:
                        coef.append(value)

            if i in index_equal_simplex:
                A_Eq_Simplex.append(coef)
                B_Eq_Simplex.append(b)
                i_eq += 1
            else:
                A_simplex.append(coef)
                B_simplex.append(b)
                i_ub += 1


        resultSimplexMinimization = linprog(C_simplex,A_ub=A_simplex, b_ub = B_simplex, A_eq=A_Eq_Simplex,b_eq=B_Eq_Simplex,method='simplex')

        for index,value in enumerate(C_simplex):
            C_simplex[index] = -value

        resultSimplexMaximization = linprog(C_simplex,A_ub=A_simplex, b_ub = B_simplex, A_eq=A_Eq_Simplex,b_eq=B_Eq_Simplex,method='simplex')

        if resultSimplexMaximization.status == 0:
            maxResult  = -resultSimplexMaximization.fun
            for x in resultSimplexMaximization.x:
                maxXSimplex.append(round(float(x),3))

        if resultSimplexMinimization.status == 0:
            minResult  = resultSimplexMinimization.fun
            for x in resultSimplexMinimization.x:
                minXSimplex.append(round(float(x),3))

    # percorre as intersecoes ( metodo grafico )
    for intersection in intersections:
        result = funcaoOtimiza.subs({x1: intersection[0], x2: intersection[1]})

        if not intersection[2]:
            valuesTested.append({'x': float(intersection[0]), 'y': float(intersection[1]), 'result': float(result), 'isValid': False})
            continue

        minAxisX = min(minAxisX,float(intersection[0]))
        maxAxisX = max(maxAxisX, float(intersection[0]))

        minAxisY = min(minAxisY, float(intersection[1]))
        maxAxisY = max(maxAxisY, float(intersection[1]))


        if result > maxResult:
            maxResult = result
            maxResultX = intersection[0]
            maxResultY = intersection[1]
        if result < minResult:
            minResult = result
            minResultX = intersection[0]
            minResultY = intersection[1]

        valuesTested.append({'x': float(intersection[0]), 'y': float(intersection[1]), 'result': float(result), 'isValid': True})

    axisRange = {
        'minX': float(os.getenv("DEFAULT_MIN_RANGE", "-100")) if minAxisX == sys.maxsize or minAxisX == -sys.maxsize else minAxisX,
        'maxX': float(os.getenv("DEFAULT_MAX_RANGE", "100")) if maxAxisX == sys.maxsize or maxAxisX == -sys.maxsize else maxAxisX,
        'minY': float(os.getenv("DEFAULT_MIN_RANGE", "-100")) if minAxisY == sys.maxsize or minAxisY == -sys.maxsize else minAxisY,
        'maxY': float(os.getenv("DEFAULT_MAX_RANGE", "100")) if maxAxisY == sys.maxsize or maxAxisY == -sys.maxsize else maxAxisY,
    }

    response_data = {
        'points': points,
        'intersections': intersections,
        'valuesTested': valuesTested,
        'maxResult': float(maxResult) if maxResult != -sys.maxsize else None,
        'maxResultX': float(maxResultX)  if maxResultX != -sys.maxsize else None,
        'maxResultY': float(maxResultY) if maxResultY != -sys.maxsize else None,
        'minResult': float(minResult) if minResult != sys.maxsize and minResult != -sys.maxsize else None,
        'minResultX': float(minResultX) if minResultX != sys.maxsize and minResultX != -sys.maxsize else None,
        'minResultY': float(minResultY) if minResultY != sys.maxsize and minResultY != -sys.maxsize else None,
        'maxXSimplex': maxXSimplex,
        'minXSimplex':minXSimplex,
        'axisRange': axisRange,
        'is2D': is2D
    }

    return JsonResponse(response_data, safe=False)