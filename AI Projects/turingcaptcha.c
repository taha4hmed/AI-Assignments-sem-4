#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>

int main() {
    int captcha, input;
    char question[100];

    srand(time(0));
    captcha = rand() % 9000 + 1000;  

    printf("==== Human Verification Test ====\n");
    printf("Enter the CAPTCHA to continue: %d\n", captcha);
    scanf("%d", &input);

    if(input != captcha) {
        printf("Verification Failed. You might be a bot.\n");
        return 0;
    }

    printf("\nVerification Successful.\n");
    printf("Starting simple Turing-style interaction...\n\n");

    getchar();

    printf("Bot: Hello! How are you today?\nYou: ");
    fgets(question, sizeof(question), stdin);

    if(strstr(question,"good") || strstr(question,"fine"))
        printf("Bot: Glad to hear that!\n");
    else
        printf("Bot: I hope your day gets better!\n");

    printf("\nBot: What is your favorite programming language?\nYou: ");
    fgets(question, sizeof(question), stdin);

    if(strstr(question,"C") || strstr(question,"c"))
        printf("Bot: Nice! C is powerful and fast.\n");
    else
        printf("Bot: Interesting choice!\n");

    printf("\nBot: Thanks for chatting. Test complete.\n");

    return 0;
}
