#include <stdio.h>

int main()
{
    char *c;
    c = "Hello World";
    char *d = "Hip Hip Hurray!";
    printf("%c\n", c[4]);
    int i=0;
    for(i=0; d[i] != '\0'; i++)
    {
        printf("%c", d[i]);
    }
    printf("\n");
    return 0;
}
