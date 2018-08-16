#include <stdio.h>

int main() {
    int x,y,z; char ch;
    x=1;
    ch='5';
    y=2;
    z=4;

    printf("%c ", x*=y+ch ); 
    printf("%d ", y+++-x );
    printf("%d ", y+++--x );
    printf("%f ", (!z, z) );
    printf("%d ", z>y>x );

    return 0;
}
