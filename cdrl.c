#include <stdio.h>
#include <string.h>
#include <stdlib.h>

char (*pars(char *x, char delimiter))[256] {
    for (int i = 0; x[i] != '\0'; i++){ // remove newlines
        if (x[i]=='\n') {
            for (int j = i; x[j] != '\0'; j++) {
                x[j] = x[j+1];
            }
            i--;
        } 
    }
    // count delimiters
    int nest = 0;
    int quotes = 0;
    int escaped = 0;
    int count = 0;
    for (int i=0; x[i] != '\0'; i++) {
        if (x[i] == '(' || x[i] == '[' || x[i] == '{') { // nest ++ if left bracket
            nest++;
        }
        if (x[i] == ')' || x[i] == ']' || x[i] == '}') { // nest -- if right bracket
            nest--;
        }
        if (!escaped && x[i] == '"') {quotes = !quotes;} // track quotes
        if (x[i] == delimiter && nest == 0 && !quotes && !escaped) {
            count++;
        }
        if (escaped) {escaped = 0;} // unescape, important location after escape uses and before escape assignment
        if (x[i] == '\\') {escaped = 1;} // escape
    }
    //prepare for parsing
    nest = 0;
    quotes = 0;
    escaped = 0;
    char stack[256];
    int stacklen = 0;
    int idxls = 0;
    char (*ls)[256] = malloc(count*256);
    for (int i=0; x[i] != '\0'; i++) {
        if (x[i] == '(' || x[i] == '[' || x[i] == '{') { // nest ++ if left bracket
            nest++;
        }
        if (x[i] == ')' || x[i] == ']' || x[i] == '}') { // nest -- if right bracket
            nest--;
        }
        if (!escaped && x[i] == '"') {quotes = !quotes;} // track quotes
        if (x[i] == delimiter && nest == 0 && !quotes && !escaped) {
            // hit delimiter, append stack to ls
            strcpy(ls[idxls++], stack);
            stacklen = 0;
            stack[0] = '\0';
        }
        if (x[i] != '\\' || escaped) {
            // append character to stack
            stack[stacklen++] = x[i];
            stack[stacklen] = '\0';
        }
        if (escaped) {escaped = 0;} // unescape, important location after escape uses and before escape assignment
        if (x[i] == '\\') {escaped = 1;} // escape
    }
    return ls;
}

int main() {
    char str[] = "test.helloworld;\nhi im \nsometh\\\";\\\"ing i\";\" think;o\nk;";
    char (*ls)[256] = pars(str,';');
    printf("%s\n", ls[0]);
    free(ls);
    return 0;
}
