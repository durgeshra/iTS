/*#include <stdio.h>
#include <stdlib.h>
#define s(n) scanf("%d",&n)
int l, b;
int arr[100][100];

void print()
{
    int i, j;
    for(i=0; i<=l; i++)
    {
        for(j=0; j<=b; j++)
        {
            printf("%8d ", arr[i][j]);
        }
        printf("\n");
    }
    printf("\n");
}

int fibo(int a, int b)
{
    if(b > a/2)
        return fibo(a, a-b);
    if(a<0 || b<0 || a<b)
        return 0;
    if(a == b || b == 0)
        return 1;
    if(arr[a][b] != -1)
    {
        return arr[a][b];
    }
    int k = fibo(a-1, b) + fibo(a-1, b-1);
    arr[a][b] = k;
    print();
    return k;
}

int main()
{
    s(l);
    s(b);
    int i, j;
    for(i=0; i<=50; i++)
    {
        for(j=0; j<=50; j++)
        {
            arr[i][j] = -1;
        }
    }
    printf("%d\n", fibo(l,b));
}*/
/*#include <stdio.h>
#include <stdlib.h>
#define s(n) scanf("%d",&n)

int main(){    int a =0, b=1;   int c=5;printf("csdc;dfvd[]{}");if(a==0 || (b=4)){printf("%d\n", b);}    return 0;}
//*/
///*
long long* fmt(int *k){ printf("Hello{World}to you, mr sir \' \" "); return func(-132+'\''); } int main() { if(k==4) for(i=0;i<10;) while(!helpArrives) scream(); else { do printf("This will cause definite trouble\")"); while(hello!=goodBye); for(i:arr;;) printf("Support this format even though im not sure if c supports it"); printf("Here;are;some:colons;and semicolons';';';'''''''"); } return 0 - enemyPrize; }
/*
#include <stdio.h>

int main() {
int
a=5;
if
(a
==5
)
printf
("14");
int i;
for
(i=0;
i<2;
i++){
if(a + 4
	== 
	9
	)
printf("1!");
else if (a==0)
	adcc;
else
	ssvsc;}
do {dfadf;} while(2524);
while(sda) {}
for (int i = 0; i < count; ++i)
{
	/* code */
//}
	// your code goes here
//	return 0;
//}
