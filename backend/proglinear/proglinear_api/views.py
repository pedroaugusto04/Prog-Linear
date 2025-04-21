import os
import sys

from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from sympy import symbols, Eq, solve, Matrix,Le,Ge,Lt,Gt,oo
from dotenv import load_dotenv
from pathlib import Path


if os.getenv("ENV") != "production":
    load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / '.env')

@api_view(['GET'])
def ping(request):
    return Response("API Online")

@api_view(['POST'])
def findPoints(request):
    INFINITE_RESULT = -2
    equacoes_str = request.data.get("equacoes", [])

    num_colunas = len(equacoes_str[0])

    # associa cada indice aos valores da eq correspondente
    equacoes_map = {i: [] for i in range(num_colunas)}

    for linha in equacoes_str:
        for i, valor in enumerate(linha):
            equacoes_map[i].append(valor)


    # aplica o sinal da operacao

    for i in equacoes_map.keys():
        lista = equacoes_map[i]
        for index,valor in enumerate(lista[1:]):
            indexOp = index + int((len(lista)) / 2) + 1
            if indexOp >= len(lista):  break
            valorOp = lista[indexOp]
            if valorOp == '-':
                lista[index+1] = -valor


    points = []
    intersections = []
    equations = []
    inequations = []
    valuesTested = []

    # monta o sistema de  inequacoes para verificacao das intersecoes
    for i in equacoes_map.keys():
        if i == 0: continue # nao processa a primeira ( a primeira eh o que queremos maximizar )

        lista = equacoes_map[i]

        x,y = symbols('x y')

        resultX = lista[0] * x
        resultY = lista[1] * y

        lhs = resultX + resultY
        rhs = lista[2]

        op2 = lista[4]

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

    # verifica 2 pontos para cada equacao

    for i in equacoes_map.keys():
        lista = equacoes_map[i]

        x, y = symbols('x y')

        A = Matrix([[lista[0],lista[1]]])
        b = Matrix([lista[2]])

        solution = solve(A * Matrix([x, y]) - b, (x, y))


        if i != 0:
            for var in solution:
                equations.append(Eq(var, solution[var]))

        if lista[0] != 0: # x != 0
            if not solution: continue

            x_expr = solution[x]
            y1 = float(os.getenv("MIN_VAR", "-100")) # first point
            y2 = float(os.getenv("MAX_VAR", "100")) # second point

            x1 = float(x_expr.subs(y, y1))
            x2 = float(x_expr.subs(y,y2))
            points.append([x1, y1, x2, y2])
        else:
            if not solution: continue

            y_expr = solution[y]
            x1 = float(os.getenv("MIN_VAR", "-100")) # first point
            x2 = float(os.getenv("MAX_VAR", "100")) # second point

            y1 = float(y_expr.subs(x,x1))
            y2 = float(y_expr.subs(x, x2))
            points.append([x1, y1, x2, y2])

    for i in range(len(equations)):
        for j in range(i + 1, len(equations)):
            if equations[i] == equations[j]: continue
            sol = solve((equations[i], equations[j]), (x, y))
            if sol:
                intersections.append([float(sol[x]), float(sol[y]),True])


    # verifica quais intersecoes sao validas ( respeitam as inequacoes e quais nao )
    for inequation in inequations:
        for intersection in intersections:
            value = {x: intersection[0],y: intersection[1]}

            valid = inequation.subs(value)

            if not valid:
                intersection[2] = False

    # verifica o limite inferior e superior de cada variavel ( verificar casos de borda - 0 ou infinito )
    limInfX = 0
    limSupX = sys.maxsize
    limInfY = 0
    limSupY = sys.maxsize
    isPossible = True # verifica se nao tem contradicao, do tipo, x = 5 e x = 4
    for inequation in inequations:

        valueX = {y: 0}

        resultX = inequation.subs(valueX)

        valueY = {x: 0}

        resultY = inequation.subs(valueY)

        if resultX != True and resultX != False:
            y = symbols('y')

            solX = solve(resultX,y)

            if solX == []:
                if (limInfX != limInfY) or (limInfX == resultX.rhs):
                    limSupX = int(resultX.rhs)
                    limInfX = int(resultX.rhs)
                else:
                    isPossible = False
            else:
                for i,cond in enumerate(solX.args):
                    op = cond.rel_op

                    x = symbols('x')

                    if cond.rhs == x:
                        valor = cond.lhs

                        if valor in (oo, -oo): continue

                        valor = valor.evalf()
                        if op == "<":
                            limInfX = max(limInfX, int(valor + 1))
                        elif op == "<=":
                            limInfX = max(limInfX, int(valor))
                    elif cond.lhs == x:
                        valor = cond.rhs
                        if valor in (oo, -oo): continue

                        valor = valor.evalf()
                        if op == "<":
                            limSupX = min(limSupX, int(valor - 1))
                        elif op == "<=":
                            limSupX = min(limSupX, int(valor))

        if resultY != True and resultY != False:
            x = symbols('x')

            solY = solve(resultY,x)

            if solY == []:
                if (limInfY != limSupY) or (limInfY == resultY.rhs):
                    limInfY = int(resultY.rhs)
                    limSupY = int(resultY.rhs)
                else:
                    isPossible = False

            else:
                for i, cond in enumerate(solY.args):
                    op = cond.rel_op

                    if cond.rhs == y:
                        valor = cond.lhs
                        if valor in (oo, -oo): continue

                        valor = valor.evalf()
                        if op == "<":
                            limInfY = max(limInfY, int(valor + 1))
                        elif op == "<=":
                            limInfY = max(limInfY, int(valor))
                    elif cond.lhs == y:
                        valor = cond.rhs
                        if valor in (oo, -oo): continue

                        valor = valor.evalf()
                        if op == "<":
                            limSupY = min(limSupY, int(valor - 1))
                        elif op == "<=":
                            limSupY = min(limSupY, int(valor))


    # recupera funcao que o usuario deseja otimizar
    listaFuncaoOtimiza = equacoes_map[0]
    x, y = symbols("x y")

    resultX = listaFuncaoOtimiza[0] * x
    resultY = listaFuncaoOtimiza[1] * y
    resultZ = listaFuncaoOtimiza[2]

    funcaoOtimiza = resultX + resultY + resultZ

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

    # verfiica se nao tem restricao superior ( resultado maximo infinito )
    if (limSupX == sys.maxsize or limSupY == sys.maxsize) and isPossible:
        #max
        maxResult = INFINITE_RESULT # indica que o maior valor pode ser infinito
        maxResultX = INFINITE_RESULT if limSupX == sys.maxsize else float(limSupX)
        maxResultY = INFINITE_RESULT if limSupY == sys.maxsize else float(limSupY)

        valuesTested.append({'x': float(INFINITE_RESULT if limSupX == sys.maxsize else float(limSupX)),
                                         'y': float(INFINITE_RESULT if limSupY == sys.maxsize else float(limSupY)), 'result': float(INFINITE_RESULT), 'isValid': isPossible})

    # verfiica se nao tem restricao inferior
    if (limInfX == 0  or limInfY == 0) and isPossible:
        # min
        minResult = funcaoOtimiza.subs({x: limInfX,y: limInfY})
        minResultX = limInfX
        minResultY = limInfY

        maxResult = funcaoOtimiza.subs({x: limInfX, y: limInfY})
        maxResultX = limInfX
        maxResultY = limInfY

        valuesTested.append({'x': float(limInfX),'y': float(limInfY),'result': float(minResult), 'isValid': isPossible})

    # percorre as intersecoes ( metodo grafico )
    for intersection in intersections:
        result = funcaoOtimiza.subs({x: intersection[0], y: intersection[1]})

        if not intersection[2]:
            valuesTested.append({'x': float(intersection[0]), 'y': float(intersection[1]), 'result': float(result), 'isValid': False})
            continue

        if isPossible:
            minAxisX = min(minAxisX,float(intersection[0]))
            maxAxisX = max(maxAxisX, float(intersection[0]))

            minAxisY = min(minAxisY, float(intersection[1]))
            maxAxisY = max(maxAxisY, float(intersection[1]))


        if result > maxResult and maxResult != INFINITE_RESULT:
            maxResult = result
            maxResultX = intersection[0]
            maxResultY = intersection[1]
        if result < minResult:
            minResult = result
            minResultX = intersection[0]
            minResultY = intersection[1]

        valuesTested.append({'x': float(intersection[0]), 'y': float(intersection[1]), 'result': float(result), 'isValid': isPossible})

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
        'axisRange': axisRange
    }

    return JsonResponse(response_data, safe=False)