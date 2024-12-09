# Matriz
 Auto Market Analizer Tool


# Propostas Funcionais:
* __Agente Risk Manager__
Media de racios obtidos como benshmark
Ajudará na decisão de tamanho de lote, alavancagem e posição do stoploss 
Aplicação de testes englobando taxas cambiais, comissões, spreads e swaps aplicados.
Excluir Tailling stoploss, só aplicado quando superar o take profit esperado como acrescento de ganho 

* __Optimização__
Janela para medição de performance
Em vez de aplicar valores às variaveis face a todo o historico, aplicar a varias janelas e fazer uma média ponderada à ultimas janelas. Acompanhando o mercado

* __Deteção de Velas__
Talib.py -> Deteção de velas


# Propostas Front End:
Adicionar os resultados no GUI
colocar totais do bot no GUI, ganho até à data


# Analisador de Stocks

* __Volume__
float - Numero de ações disponiveis para investidores publicos comprarem (Poucos M - Penny Stocks) 
_Yahoo Finance -> Statistics -> Share Statistics_

ALVO: High Volume + Low Supply (Low float better target 20M low)

* __News__
Stock Screener (Follow the walles)
_Trading View -> Stock Screener_ (7:00 am - 9:00 am) Qualquer stock nova aqui sugere um bom movimento diario. 
Destas stocks novas puxar noticias associadas do yahoo p.e.

* __Relative Volume__
Compara o volume corrente em relação à quantidade de volume que é negociado normalmente. 60 = 60x mais volume.

__News screener__
* NEXT IMPLEMENTATION