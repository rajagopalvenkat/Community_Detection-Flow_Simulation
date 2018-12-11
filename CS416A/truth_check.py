import sys
import numpy as np
import matplotlib.pyplot as plt
import random

T={}

f=open(sys.argv[1], 'r')
lines=list(f.readlines())

i=0
for line in lines:
	T[i]=set([int(x) for x in line.split()])
	i+=1

f.close()
f=open(sys.argv[2], 'r')
lines=list(f.readlines())

C = {}

for line in lines:
	cs=[int(x) for x in line.split()]
	if cs[1] in C:
		C[cs[1]].add(cs[0])
	else:
		C[cs[1]]=set([cs[0]])
if -1 in C:
	del C[-1]

count=0

TP=0
FP=0
TN=0
FN=0

while count<=10000:
	count+=1
	if random.uniform(0,1)<=0.5: 				# Choose Positive
		key=random.sample(C.keys(),1)[0]
		u=random.sample(C[key], 1)[0]
		v=random.sample(C[key], 1)[0]
		matched=0
		for key, value in T.items():
			if u in value and v in value:
				matched=1
				break
		if matched:
			TP+=1
		else:
			FP+=1
	else:									# Sample Negative
		key_1=random.sample(C.keys(),1)[0]
		matched=0
		key_2=key_1
		while key_2==key_1:
			key_2=random.sample(C.keys(), 1)[0]
		u=random.sample(C[key_1], 1)[0]
		v=random.sample(C[key_2], 1)[0]

		matched=0
		for key, value in T.items():
			if u in value and v in value:
				matched=1
				break
		if matched:
			FN+=1
		else:
			TN+=1


print("TP : ", TP)
print("FP : ", FP)
print("TN : ", TN)
print("FN : ", FN)