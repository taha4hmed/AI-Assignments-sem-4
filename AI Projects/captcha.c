#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main() {
    int a, b, ans;
    srand(time(0));
    a = rand() % 10 + 1;
    b = rand() % 10 + 1;
    printf("Solve: %d + %d = ", a, b);
    scanf("%d", &ans);
    if(ans == a + b)
        printf("Human Verified\n");
    else
        printf("Verification Failed\n");
    return 0;
}