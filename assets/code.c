#include <stdio.h>

int main()
{
    int a;
    scanf("%d", &a);
    long long t;
    float m;
    scanf("%lld %f", &t, &m);
    a += 3;
    t += 30000;
    m += a;
    printf("%d\t%lld\n%f\n", a, t, m);
    return 0;
}
