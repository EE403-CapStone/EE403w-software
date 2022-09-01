from axioms_calc import expression as e
import math as m

def car2pol(cart):
		theta = m.atan(cart.imag/cart.real)*180/m.pi
		return abs(cart), theta



M = [
e('Sab=Vab*Iab\'=(P/3)+(Q/3)*1j^(1-2*leading?)'),
e('|S|^2=(P^2)+(Q^2)'),
e('Vab=Van*e^((pi*1j*30)/180)'),
e('Vba=Van*e^((pi*1j*270)/180)'),
e('Vca=Van*e^((pi*1j*150)/180)'),
e('|S|=P/pf'),]

S = e()
S = S.connect_exps(M)


S.dir ={}
S.map()

for leaf in S.dir.keys():
	text_input = (input(leaf+"= "))
	if len(text_input)>0:
		S.replace(leaf,complex(text_input))


print('################')


sol = S.solve()


m1 = [e('Ia=Iab-Ica'),
e('Ib=Ibc-Iab'),
e('Ic=Ica-Ibc'),
e('Ibc=Iab*e^((pi*1j*240)/180)'),
e('Ica=Iab*e^((pi*1j*120)/180)'),
]


if 'Iab\'' in sol:
	I = e.connect_exps(m1)
	I.replace('Iab',sol['Iab\''].conjugate())
	I.solve()

for leaf in sol.keys():
	S.replace(leaf,sol[leaf])

sol = S.solve()
if 'Iab\'' in sol:
	I = e.connect_exps(m1)
	I.replace('Iab',sol['Iab\''].conjugate())
	I.solve()


	
