# ============================================================
# EEL670 - Trabalho Final
# Autores: Miguel Cerne & João Costa
#
# Alvos principais:
# - make
# - make run
# - make test-py
# - make test-cpp
# - make test-deps
# - make dist
# - make clean
#
# Dependências (Debian/Ubuntu):
# - sudo apt install g++ make python3-dev python3-pybind11 zip
# - (ou: pip install pybind11)
# ============================================================

CXX ?= g++
PYTHON ?= python3
PY_CONFIG ?= python3-config

TARGET := simulador_mercado
SRC_DIR := src
INCLUDE_DIR := include
PYTHON_DIR := python
BUILD_DIR := build
TEST_CPP_DIR := tests/cpp
TEST_PY_DIR := tests/python
TEST_TARGET := $(BUILD_DIR)/run_tests

DIST_NAME := EEL670_TrabalhoFinal_Joao_Miguel
DIST_FILES := Makefile README.md $(INCLUDE_DIR) $(SRC_DIR) $(PYTHON_DIR) tests data

# ------------------------------------------------------------
# Python embarcado (pybind11/embed.h)
# ------------------------------------------------------------
# `python3 -m pybind11 --includes` ja inclui os headers do proprio Python.
PYBIND11_INCLUDES := $(shell $(PYTHON) -m pybind11 --includes 2>/dev/null)
 
# A partir do Python 3.8, `--ldflags` sozinho NAO inclui -lpython3.x;
# para embarcar o interpretador e preciso `--embed`. O fallback cobre 3.7-.
PYTHON_LDLIBS := $(shell $(PY_CONFIG) --ldflags --embed 2>/dev/null || $(PY_CONFIG) --ldflags 2>/dev/null)
 
# Caminho absoluto de python/, resolvido na maquina que compila. O PythonBridge
# insere esse diretorio no sys.path antes de importar agents_py.
AGENTS_PY_DIR := $(abspath $(PYTHON_DIR))
 
# ------------------------------------------------------------
# Flags
# ------------------------------------------------------------
CPPFLAGS := -I$(INCLUDE_DIR) $(PYBIND11_INCLUDES) -DAGENTS_PY_DIR=\"$(AGENTS_PY_DIR)\"
 
# -fvisibility=hidden evita os avisos do GCC sobre classes que guardam
# py::object como membro ("declared with greater visibility...").
# -MMD -MP geram dependencias de headers automaticamente (arquivos .d).
CXXFLAGS ?= -O2
CXXFLAGS += -std=c++17 -Wall -Wextra -Wpedantic -fvisibility=hidden -MMD -MP
 
LDLIBS := $(PYTHON_LDLIBS)
 
# ------------------------------------------------------------
# Fontes e objetos
# ------------------------------------------------------------
SRCS      := $(wildcard $(SRC_DIR)/*.cpp)
OBJS      := $(SRCS:$(SRC_DIR)/%.cpp=$(BUILD_DIR)/%.o)
MAIN_OBJ  := $(BUILD_DIR)/main.o
# Tudo menos o main: reaproveitado pelo binario de testes.
CORE_OBJS := $(filter-out $(MAIN_OBJ),$(OBJS))
 
TEST_SRCS := $(wildcard $(TEST_CPP_DIR)/*.cpp)
TEST_OBJS := $(TEST_SRCS:$(TEST_CPP_DIR)/%.cpp=$(BUILD_DIR)/tests/%.o)
 
DEPS := $(OBJS:.o=.d) $(TEST_OBJS:.o=.d)
 
.PHONY: all run test test-py test-cpp check-deps dist clean
 
all: $(TARGET)
 
$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) $^ -o $@ $(LDLIBS)
 
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.cpp | check-deps $(BUILD_DIR)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@
 
$(BUILD_DIR)/tests/%.o: $(TEST_CPP_DIR)/%.cpp | check-deps $(BUILD_DIR)/tests
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@
 
$(BUILD_DIR) $(BUILD_DIR)/tests:
	mkdir -p $@
 
run: $(TARGET)
	./$(TARGET)
 
# ------------------------------------------------------------
# Testes
# ------------------------------------------------------------
test: test-py test-cpp
 
test-py:
	$(PYTHON) -m unittest discover -s $(TEST_PY_DIR) -v
 
ifeq ($(strip $(TEST_SRCS)),)
test-cpp:
	@echo "Nenhum teste C++ em $(TEST_CPP_DIR)/ ainda; pulando."
else
test-cpp: $(TEST_TARGET)
	./$(TEST_TARGET)
 
$(TEST_TARGET): $(CORE_OBJS) $(TEST_OBJS)
	$(CXX) $(CXXFLAGS) $^ -o $@ $(LDLIBS)
endif
 
# ------------------------------------------------------------
# Utilitarios
# ------------------------------------------------------------
check-deps:
	@if [ -z "$(strip $(PYBIND11_INCLUDES))" ]; then \
		echo "Erro: pybind11 nao encontrado para '$(PYTHON)'."; \
		echo "Instale com 'sudo apt install python3-pybind11' ou 'pip install pybind11'."; \
		exit 1; \
	fi
	@if [ -z "$(strip $(PYTHON_LDLIBS))" ]; then \
		echo "Erro: '$(PY_CONFIG)' nao encontrado. Instale 'python3-dev'."; \
		exit 1; \
	fi
 
dist: clean
	rm -f $(DIST_NAME).zip
	zip -r $(DIST_NAME).zip $(wildcard $(DIST_FILES)) \
		-x '*/__pycache__/*' '*.pyc' '*.tmp'
	@echo "Pacote gerado: $(DIST_NAME).zip"
 
clean:
	rm -rf $(BUILD_DIR) $(TARGET)
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
 
-include $(DEPS)