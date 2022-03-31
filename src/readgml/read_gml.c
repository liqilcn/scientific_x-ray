#include "Python.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include <ctype.h>

#define MAX_LEN 10100

void strip_and_spilt_with_max_1(const char *s, char **word1, char **word2) {
    const char *start = s, *end;
    long len;
    *word1 = *word2 = NULL;
    
    while (isspace(*start)) ++start;
    if (!*start) return;  // empty line
    end = start;
    while (*end && !isspace(*end)) ++end;  // [start, end)
    len = end - start;
    *word1 = (char *)malloc(sizeof(char) * (len + 1));
    strncpy(*word1, start, len);
    (*word1)[len] = 0;

    start = end;
    while (isspace(*start)) ++start;
    if (!*start) return;  // not key value
    if (*start == '"') ++start;
    end = start + strlen(start) - 1;
    while (isspace(*end)) --end;
    if (*end != '"') ++end;  // [start, end)
    len = end - start;
    *word2 = (char *)malloc(sizeof(char) * (len + 1));
    strncpy(*word2, start, len);
    (*word2)[len] = 0;
}

static PyObject *py_read_gml(PyObject *self, PyObject *args) {
    const char *file_name;
    if (!PyArg_ParseTuple(args, "s", &file_name)) {
        return NULL;
    }
    
    // Read gml file.
    FILE* f = fopen(file_name, "r");
    if (f == NULL) {
        return NULL;
    }
    
    PyObject *nodes, *edges, *tmp;
    nodes = PyList_New(0);
    edges = PyList_New(0);
    tmp = PyDict_New();
    
    char line[MAX_LEN], *word1, *word2;
    while (true) {
        char *ret = fgets(line, MAX_LEN, f);
        if (ret == NULL) {
            break;
        }
        strip_and_spilt_with_max_1(line, &word1, &word2);
        if (word1 != NULL) {
            if (!strcmp(word1, "node")) {
                Py_DECREF(tmp);
                tmp = PyDict_New();
                PyList_Append(nodes, tmp);
            }
            if (!strcmp(word1, "edge")) {
                Py_DECREF(tmp);
                tmp = PyDict_New();
                PyList_Append(edges, tmp);
            }
            if (word2 != NULL) {
                PyObject *value;
                if (!strcmp(word1, "id") || !strcmp(word1, "source") || !strcmp(word1, "target")) {
                    value = Py_BuildValue("l", atol(word2));
                } else if (!strcmp(word1, "x") || !strcmp(word1, "y") || !strcmp(word1, "z") || !strcmp(word1, "w") || !strcmp(word1, "h") || !strcmp(word1, "d") || !strcmp(word1, "value")) {
                    value = Py_BuildValue("d", atof(word2));
                } else if (!strcmp(word1, "fill") || !strcmp(word1, "fill_dark") || !strcmp(word1, "color") || !strcmp(word1, "color_dark")) {
                    value = Py_BuildValue("s", word2 + 1);
                } else {
                    value = Py_BuildValue("s", word2);
                }
                PyDict_SetItemString(tmp, word1, value);
                Py_DECREF(value);
                free(word2);
            }
            free(word1);
        }
    }
    
    fclose(f);
    
    PyObject *tuple = Py_BuildValue("(OO)", nodes, edges);
    Py_DECREF(nodes);
    Py_DECREF(edges);
    Py_DECREF(tmp);
    return tuple;
}

/* Module method table */
static PyMethodDef SampleMethods[] = {
    { "read_gml", py_read_gml, METH_VARARGS, "Read GML file" },
    { NULL, NULL, 0, NULL }
};

/* Module structure */
static struct PyModuleDef samplemodule = {
    PyModuleDef_HEAD_INIT,
    "readgml",           /* name of module */
    "Read GML file.",  /* Doc string (may be NULL) */
    -1,                 /* Size of per-interpreter state or -1 */
    SampleMethods       /* Method table */
};

/* Module initialization function */
PyMODINIT_FUNC
PyInit_readgml(void) {
    return PyModule_Create(&samplemodule);
}