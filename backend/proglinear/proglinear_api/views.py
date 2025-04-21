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

        op1 = lista[3]

        resultX = lista[0] * x
        resultY = lista[1] * y

        if op1 == "-":
            resultY *= -1

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
            x_expr = solution[x]
            y1 = float(os.getenv("MIN_VAR", "-100")) # first point
            y2 = float(os.getenv("MAX_VAR", "100")) # second point

            x1 = float(x_expr.subs(y, y1))
            x2 = float(x_expr.subs(y,y2))
            points.append([x1, y1, x2, y2])
        else:
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

    # verifica o limite inferior superior de cada variavel ( verificar casos de borda - 0 ou infinito )
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


            for i,cond in enumerate(solX.args):
                op = cond.rel_op

                x = symbols('x')

                if cond.rhs == x:
                    valor = cond.lhs

                    if valor in (oo, -oo): continue

                    valor = valor.evalf()
                    if op == "==":
                        if limInfX <= int(valor) <= limSupX:
                            limSupX = int(valor)
                            limInfX = int(valor)
                        else:
                            isPossible = False

                elif cond.lhs == x:
                    valor = cond.rhs
                    if valor in (oo, -oo): continue

                    valor = valor.evalf()
                    if op == "<":
                        limSupX = min(limSupX, int(valor - 1))
                    elif op == "<=":
                        limSupX = min(limSupX, int(valor))
                    elif op == "==":
                        if limInfX <= int(valor) <= limSupX:
                            limSupX = int(valor)
                            limInfX = int(valor)
                        else:
                            isPossible = False

        if resultY != True and resultY != False:
            x = symbols('x')

            solY = solve(resultY,x)

            for i, cond in enumerate(solY.args):
                op = cond.rel_op
                if cond.rhs == y:
                    valor = cond.lhs
                    if valor in (oo, -oo): continue

                    valor = valor.evalf()
                    if op == "==":
                        if limInfY <= int(valor) <= limSupY:
                            limInfY = int(valor)
                            limSupY = int(valor)
                        else:
                            isPossible = False

                elif cond.lhs == y:
                    valor = cond.rhs
                    if valor in (oo, -oo): continue

                    valor = valor.evalf()
                    if op == "<":
                        limSupY = min(limSupY, int(valor - 1))
                    elif op == "<=":
                        limSupY = min(limSupY, int(valor))
                    elif op == "==":
                        if limInfY <= int(valor) <= limSupY:
                            limInfY = int(valor)
                            limSupY = int(valor)
                        else:
                            isPossible = False


    # recupera funcao que o usuario deseja otimizar
    listaFuncaoOtimiza = equacoes_map[0]
    x, y = symbols("x y")

    resultX = listaFuncaoOtimiza[0] * x
    resultY = listaFuncaoOtimiza[1] * y
    resultZ = listaFuncaoOtimiza[2]
    op1 = listaFuncaoOtimiza[3]
    op2 = listaFuncaoOtimiza[4]

    if op1 == "-":
        resultY *= -1

    if op2 == "-":
        resultZ *= -1

    funcaoOtimiza = resultX + resultY + resultZ
    maxResult = -sys.maxsize
    maxResultX = -sys.maxsize
    maxResultY = -sys.maxsize

    minResult = sys.maxsize
    minResultX = -sys.maxsize
    minResultY = -sys.maxsize


    if limSupX == sys.maxsize or limSupY == sys.maxsize:
        #max
        maxResult = INFINITE_RESULT # indica que o maior valor pode ser infinito
        maxResultX = INFINITE_RESULT if limSupX == sys.maxsize else float(limSupX)
        maxResultY = INFINITE_RESULT if limSupY == sys.maxsize else float(limSupY)

        valuesTested.append({'x': float(INFINITE_RESULT if limSupX == sys.maxsize else float(limSupX)),
                                         'y': float(INFINITE_RESULT if limSupY == sys.maxsize else float(limSupY)), 'result': float(INFINITE_RESULT), 'isValid': isPossible})
        #min
        result = funcaoOtimiza.subs({x: limInfX, y: limInfY})
        minResult = result
        minResultX = limInfX
        minResultY = limInfY
        valuesTested.append({'x': float(limInfX), 'y': float(limInfY), 'result': float(result), 'isValid': isPossible})

    # percorre as intersecoes ( metodo grafico )
    for intersection in intersections:
        result = funcaoOtimiza.subs({x: intersection[0], y: intersection[1]})

        if not intersection[2]:
            valuesTested.append({'x': float(intersection[0]), 'y': float(intersection[1]), 'result': float(result), 'isValid': False})
            continue

        if result > maxResult and maxResult != INFINITE_RESULT:
            maxResult = result
            maxResultX = intersection[0]
            maxResultY = intersection[1]
        if result < minResult:
            minResult = result
            minResultX = intersection[0]
            minResultY = intersection[1]

        valuesTested.append({'x': float(intersection[0]), 'y': float(intersection[1]), 'result': float(result), 'isValid': isPossible})

    response_data = {
        'points': points,
        'intersections': intersections,
        'valuesTested': valuesTested,
        'maxResult': float(maxResult) if maxResult != -sys.maxsize else None,
        'maxResultX': float(maxResultX)  if maxResultX != -sys.maxsize else None,
        'maxResultY': float(maxResultY) if maxResultY != -sys.maxsize else None,
        'minResult': float(minResult) if minResult != sys.maxsize and minResult != -sys.maxsize else None,
        'minResultX': float(minResultX) if minResultX != sys.maxsize and minResultX != -sys.maxsize else None,
        'minResultY': float(minResultY) if minResultY != sys.maxsize and minResultY != -sys.maxsize else None
    }

    return JsonResponse(response_data, safe=False)