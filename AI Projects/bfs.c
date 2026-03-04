#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int m, c, b;
} State;

int valid(int m, int c) {
    if(m < 0 || c < 0 || m > 3 || c > 3) return 0;
    if(m > 0 && m < c) return 0;
    if((3 - m) > 0 && (3 - m) < (3 - c)) return 0;
    return 1;
}

int main() {
    State queue[100];
    int front = 0, rear = 0;
    int visited[4][4][2] = {0};

    State start = {3,3,1};
    queue[rear++] = start;
    visited[3][3][1] = 1;

    while(front < rear) {
        State curr = queue[front++];
        printf("(%d,%d,%d)\n", curr.m, curr.c, curr.b);

        if(curr.m == 0 && curr.c == 0 && curr.b == 0)
            break;

        int moves[5][2] = {{1,0},{2,0},{0,1},{0,2},{1,1}};

        for(int i=0;i<5;i++) {
            int nm, nc, nb;

            if(curr.b == 1) {
                nm = curr.m - moves[i][0];
                nc = curr.c - moves[i][1];
                nb = 0;
            } else {
                nm = curr.m + moves[i][0];
                nc = curr.c + moves[i][1];
                nb = 1;
            }

            if(valid(nm,nc) && !visited[nm][nc][nb]) {
                visited[nm][nc][nb] = 1;
                State next = {nm,nc,nb};
                queue[rear++] = next;
            }
        }
    }
    return 0;
}