# 🧪 GUIA COMPLETO DE TESTES - CHATBOT ACADÊMICO

## 📋 ÍNDICE

1. [Testes Básicos de Conversação](#1-testes-básicos-de-conversação)
2. [Testes de Consultas de Avisos](#2-testes-de-consultas-de-avisos)
3. [Testes de Cronograma e Horários](#3-testes-de-cronograma-e-horários)
4. [Testes de Avaliações](#4-testes-de-avaliações)
5. [Testes de Atividades Acadêmicas](#5-testes-de-atividades-acadêmicas)
6. [Testes de Informações de Docentes](#6-testes-de-informações-de-docentes)
7. [Testes de Atendimento de Docentes](#7-testes-de-atendimento-de-docentes)
8. [Testes de Perguntas com IA](#8-testes-de-perguntas-com-ia)
9. [Testes de Solicitação de Materiais](#9-testes-de-solicitação-de-materiais)
10. [Testes de Dúvidas Frequentes](#10-testes-de-dúvidas-frequentes)
11. [Testes de Formulários](#11-testes-de-formulários)
12. [Testes de Salvamento de Perguntas](#12-testes-de-salvamento-de-perguntas)
13. [Testes de Retorno de URLs](#13-testes-de-retorno-de-urls)
14. [Testes de Integração com API](#14-testes-de-integração-com-api)
15. [Testes de Casos Extremos e Erros](#15-testes-de-casos-extremos-e-erros)
16. [Checklist de Testes](#16-checklist-de-testes)

---

## 1. TESTES BÁSICOS DE CONVERSAÇÃO

### 1.1 Saudação

**Objetivo:** Verificar se o bot responde corretamente a saudações.

**Testes:**
```
Usuário: oi
Esperado: "Ola. Sou o assistente academico. Como posso ajudar voce hoje?"

Usuário: olá
Esperado: "Ola. Sou o assistente academico. Como posso ajudar voce hoje?"

Usuário: bom dia
Esperado: "Ola. Sou o assistente academico. Como posso ajudar voce hoje?"

Usuário: boa tarde
Esperado: "Ola. Sou o assistente academico. Como posso ajudar voce hoje?"

Usuário: boa noite
Esperado: "Ola. Sou o assistente academico. Como posso ajudar voce hoje?"

Usuário: e aí
Esperado: "Ola. Sou o assistente academico. Como posso ajudar voce hoje?"

Usuário: tudo bem
Esperado: "Ola. Sou o assistente academico. Como posso ajudar voce hoje?"
```

**Verificações:**
- ✅ Bot responde com mensagem de saudação
- ✅ Pergunta foi salva no banco (verificar endpoint `/mensagens_aluno/get_lista_msg/`)

---

### 1.2 Despedida

**Objetivo:** Verificar se o bot responde corretamente a despedidas.

**Testes:**
```
Usuário: tchau
Esperado: "Ate mais. Bons estudos."

Usuário: adeus
Esperado: "Ate mais. Bons estudos."

Usuário: até mais
Esperado: "Ate mais. Bons estudos."

Usuário: até logo
Esperado: "Ate mais. Bons estudos."

Usuário: preciso ir
Esperado: "Ate mais. Bons estudos."

Usuário: encerrar
Esperado: "Ate mais. Bons estudos."

Usuário: sair
Esperado: "Ate mais. Bons estudos."
```

**Verificações:**
- ✅ Bot responde com mensagem de despedida

---

### 1.3 Agradecimento

**Objetivo:** Verificar se o bot responde corretamente a agradecimentos.

**Testes:**
```
Usuário: obrigado
Esperado: "De nada! Fico feliz em ajudar."

Usuário: obrigada
Esperado: "De nada! Fico feliz em ajudar."

Usuário: valeu
Esperado: "De nada! Fico feliz em ajudar."

Usuário: grato
Esperado: "De nada! Fico feliz em ajudar."

Usuário: muito obrigado
Esperado: "De nada! Fico feliz em ajudar."

Usuário: ajudou muito
Esperado: "De nada! Fico feliz em ajudar."
```

**Verificações:**
- ✅ Bot responde com mensagem de agradecimento

---

### 1.4 Solicitar Ajuda

**Objetivo:** Verificar se o bot explica suas funcionalidades.

**Testes:**
```
Usuário: me ajuda
Esperado: "Posso ajudar com datas de provas e aulas, conteudos de materias, informacoes sobre TCC, APS e Estagio e contato de professores."

Usuário: o que você sabe fazer
Esperado: "Posso ajudar com datas de provas e aulas, conteudos de materias, informacoes sobre TCC, APS e Estagio e contato de professores."

Usuário: quais as funções
Esperado: "Posso ajudar com datas de provas e aulas, conteudos de materias, informacoes sobre TCC, APS e Estagio e contato de professores."

Usuário: estou perdido
Esperado: "Posso ajudar com datas de provas e aulas, conteudos de materias, informacoes sobre TCC, APS e Estagio e contato de professores."

Usuário: como usar o bot
Esperado: "Posso ajudar com datas de provas e aulas, conteudos de materias, informacoes sobre TCC, APS e Estagio e contato de professores."

Usuário: lista de comandos
Esperado: "Posso ajudar com datas de provas e aulas, conteudos de materias, informacoes sobre TCC, APS e Estagio e contato de professores."
```

**Verificações:**
- ✅ Bot responde com lista de funcionalidades

---

### 1.5 Bot Challenge

**Objetivo:** Verificar se o bot identifica perguntas sobre sua natureza.

**Testes:**
```
Usuário: você é um robô
Esperado: "Sou um assistente virtual academico treinado para tirar suas duvidas."

Usuário: estou falando com uma pessoa
Esperado: "Sou um assistente virtual academico treinado para tirar suas duvidas."

Usuário: quem é você
Esperado: "Sou um assistente virtual academico treinado para tirar suas duvidas."
```

**Verificações:**
- ✅ Bot responde explicando sua natureza

---

## 2. TESTES DE CONSULTAS DE AVISOS

**Action:** `action_buscar_ultimos_avisos`

**Objetivo:** Verificar se o bot busca e exibe avisos corretamente.

**Testes:**
```
Usuário: tem algum aviso novo
Esperado: 
  - "Consultando mural de avisos..."
  - Lista dos últimos 3 avisos com título e conteúdo

Usuário: a aula foi cancelada
Esperado: 
  - "Consultando mural de avisos..."
  - Lista dos últimos 3 avisos

Usuário: recados do professor
Esperado: 
  - "Consultando mural de avisos..."
  - Lista dos últimos 3 avisos

Usuário: últimos avisos da coordenação
Esperado: 
  - "Consultando mural de avisos..."
  - Lista dos últimos 3 avisos

Usuário: quais são os avisos mais recentes
Esperado: 
  - "Consultando mural de avisos..."
  - Lista dos últimos 3 avisos

Usuário: me lista os avisos
Esperado: 
  - "Consultando mural de avisos..."
  - Lista dos últimos 3 avisos

Usuário: ver recados
Esperado: 
  - "Consultando mural de avisos..."
  - Lista dos últimos 3 avisos

Usuário: algum comunicado importante?
Esperado: 
  - "Consultando mural de avisos..."
  - Lista dos últimos 3 avisos
```

**Verificações:**
- ✅ Bot exibe mensagem "Consultando mural de avisos..."
- ✅ Bot retorna lista de avisos (máximo 3)
- ✅ Cada aviso tem título e conteúdo
- ✅ Se não houver avisos, exibe "Nao ha avisos recentes."
- ✅ Pergunta foi salva no banco com tópico "Aviso"
- ✅ Verificar no banco: `GET /mensagens_aluno/get_lista_msg/`

**Cenários de Erro:**
```
# Teste com API offline
Usuário: tem algum aviso novo
Esperado: "Erro ao conectar ao sistema de avisos."
```

---

## 3. TESTES DE CRONOGRAMAS E HORÁRIOS

**Action:** `action_buscar_cronograma`

**Objetivo:** Verificar se o bot busca horários de aulas corretamente.

**Testes com Disciplina Específica:**
```
Usuário: que horas é a aula de Sistemas Distribuídos
Esperado: 
  - "Buscando horários..."
  - Horário formatado: "Horario de Sistemas Distribuidos:\n- [dia] as [hora] (Sala [sala])"

Usuário: qual a sala da aula de Engenharia de Software
Esperado: 
  - Horário com sala informada

Usuário: que dia é a aula de Banco de Dados
Esperado: 
  - Horário com dia da semana

Usuário: horário da aula de Cloud Computing
Esperado: 
  - Horário completo

Usuário: quando é a aula de Qualidade de Software
Esperado: 
  - Horário completo

Usuário: qual o horário de Sistemas Distribuídos
Esperado: 
  - Horário completo
```

**Testes sem Disciplina:**
```
Usuário: que horas é a aula
Esperado: "De qual disciplina voce quer saber o horario?"
```

**Testes com Disciplina Não Encontrada:**
```
Usuário: que horas é a aula de Disciplina Inexistente
Esperado: "Nao encontrei a disciplina Disciplina Inexistente."
```

**Verificações:**
- ✅ Bot extrai entidade "disciplina" corretamente
- ✅ Bot busca ID da disciplina usando endpoint de cronograma
- ✅ Bot retorna horário formatado (dia, hora, sala)
- ✅ Se múltiplos horários, lista todos
- ✅ Pergunta foi salva com tópico "Disciplina"
- ✅ Verificar se `get_disciplina_id_by_name` funciona corretamente

**Cenários de Erro:**
```
# Disciplina não existe
Usuário: horário de Disciplina Teste 123
Esperado: "Nao encontrei a disciplina Disciplina Teste 123."

# API offline
Usuário: horário de Engenharia de Software
Esperado: "Erro ao buscar cronograma."
```

---

## 4. TESTES DE AVALIAÇÕES

**Action:** `action_buscar_data_avaliacao`

**Objetivo:** Verificar se o bot busca datas de avaliações corretamente.

**Testes com Disciplina e Tipo de Avaliação:**
```
Usuário: quando é a NP1 de Engenharia de Software
Esperado: 
  - "Buscando datas..."
  - Lista de datas: "Datas:\n- [tipo]: [data]"

Usuário: data da prova de Sistemas Distribuídos
Esperado: 
  - Lista de provas da disciplina

Usuário: quando é a np1 de ES
Esperado: 
  - Lista de datas

Usuário: data da prova 1 de Engenharia
Esperado: 
  - Lista de datas

Usuário: qual a data do exame de Banco de Dados
Esperado: 
  - Lista de exames

Usuário: quando é a NP2 de Cloud Computing
Esperado: 
  - Lista de datas

Usuário: data da substitutiva de Qualidade de Software
Esperado: 
  - Lista de datas
```

**Testes sem Disciplina:**
```
Usuário: quando é a prova
Esperado: "Qual a disciplina?"
```

**Testes com Disciplina Não Encontrada:**
```
Usuário: quando é a NP1 de Disciplina Inexistente
Esperado: "Disciplina 'Disciplina Inexistente' nao encontrada. Verifique se o nome esta correto."
```

**Verificações:**
- ✅ Bot extrai entidades "disciplina" e "tipo_avaliacao"
- ✅ Bot busca avaliações da disciplina
- ✅ Bot filtra por tipo de avaliação (NP1, NP2, exame, etc.)
- ✅ Bot retorna datas formatadas (sem hora, apenas data)
- ✅ Se não encontrar, exibe mensagem apropriada
- ✅ Pergunta foi salva com tópico "Disciplina"

**Cenários de Erro:**
```
# Disciplina não existe
Usuário: quando é a NP1 de Disciplina Teste
Esperado: "Disciplina 'Disciplina Teste' nao encontrada..."

# Nenhuma avaliação encontrada
Usuário: quando é a prova de Engenharia de Software
Esperado: "Nao achei datas de prova para essa materia."

# API offline
Usuário: quando é a NP1 de ES
Esperado: "Erro ao buscar avaliacoes."
```

---

## 5. TESTES DE ATIVIDADES ACADÊMICAS

**Action:** `action_buscar_info_atividade_academica`

**Objetivo:** Verificar se o bot busca informações sobre TCC, APS, Estágio e Horas Complementares.

### 5.1 Testes de TCC

**Testes:**
```
Usuário: o que é TCC
Esperado: 
  - "Buscando informacoes sobre TCC..."
  - Informações sobre TCC da base de conhecimento

Usuário: informações sobre trabalho de conclusão
Esperado: 
  - Informações sobre TCC

Usuário: regras do TCC
Esperado: 
  - Informações sobre TCC
```

**Verificações:**
- ✅ Bot identifica intent `consultar_regras_tcc`
- ✅ Bot busca na base de conhecimento
- ✅ Bot retorna informações formatadas
- ✅ Pergunta foi salva com tópico "TCC"

### 5.2 Testes de APS

**Testes:**
```
Usuário: o que é APS
Esperado: 
  - "Buscando informacoes sobre APS..."
  - Informações sobre APS

Usuário: regras da APS
Esperado: 
  - Informações sobre APS

Usuário: informações sobre atividade prática
Esperado: 
  - Informações sobre APS
```

**Verificações:**
- ✅ Bot identifica intent `consultar_regras_aps`
- ✅ Bot busca na base de conhecimento
- ✅ Pergunta foi salva com tópico "APS"

### 5.3 Testes de Estágio

**Testes:**
```
Usuário: informações sobre estágio
Esperado: 
  - "Buscando informacoes sobre Estagio..."
  - Informações sobre Estágio

Usuário: regras de estágio
Esperado: 
  - Informações sobre Estágio
```

**Verificações:**
- ✅ Bot identifica intent `consultar_estagio`
- ✅ Bot busca na base de conhecimento
- ✅ Pergunta foi salva com tópico "Estágio"

### 5.4 Testes de Horas Complementares

**Testes:**
```
Usuário: informações sobre horas complementares
Esperado: 
  - "Buscando informacoes sobre Horas Complementares..."
  - Informações sobre Horas Complementares

Usuário: regras de horas complementares
Esperado: 
  - Informações sobre Horas Complementares
```

**Verificações:**
- ✅ Bot identifica intent `consultar_horas_complementares`
- ✅ Bot busca na base de conhecimento
- ✅ Pergunta foi salva com tópico "Horas Complementares"

**Cenários de Erro:**
```
# Atividade não especificada
Usuário: informações sobre atividade
Esperado: "Sobre qual atividade voce quer saber? (TCC, APS, Estagio)"

# Informação não encontrada
Usuário: o que é TCC
Esperado: "Nao encontrei informacoes detalhadas sobre TCC."

# API offline
Usuário: regras do TCC
Esperado: "Erro ao buscar informacoes do curso."
```

---

## 6. TESTES DE INFORMAÇÕES DE DOCENTES

**Action:** `action_buscar_info_docente`

**Objetivo:** Verificar se o bot busca informações de contato de docentes.

**Testes:**
```
Usuário: qual o email do professor Alvaro
Esperado: 
  - "Contato Docente\nNome: [nome]\nEmail: [email]"

Usuário: contato do Zezinho
Esperado: 
  - Informações de contato

Usuário: onde encontro o Magrini
Esperado: 
  - Informações de contato

Usuário: me passa o email do Alvaro
Esperado: 
  - Email do docente

Usuário: qual o contato da Eliane
Esperado: 
  - Informações de contato
```

**Testes sem Nome:**
```
Usuário: qual o email do professor
Esperado: "Qual o nome do professor?"
```

**Testes com Docente Não Encontrado:**
```
Usuário: contato do Professor Inexistente
Esperado: "Nao encontrei o professor(a) Professor Inexistente no cadastro."
```

**Verificações:**
- ✅ Bot extrai entidade "nome_docente"
- ✅ Bot busca em professores e coordenadores
- ✅ Bot retorna nome e email
- ✅ Se não encontrar, exibe mensagem apropriada
- ✅ Pergunta foi salva com tópico "Docente"

**Cenários de Erro:**
```
# Docente não existe
Usuário: email do Professor Teste
Esperado: "Nao encontrei o professor(a) Professor Teste no cadastro."

# API offline
Usuário: contato do Alvaro
Esperado: "Erro ao buscar lista de professores."
```

---

## 7. TESTES DE ATENDIMENTO DE DOCENTES

**Action:** `action_buscar_atendimento_docente`  
**Form:** `form_atendimento_docente`

**Objetivo:** Verificar se o bot busca horários de atendimento usando formulário.

### 7.1 Testes com Nome no Primeiro Turno

**Testes:**
```
Usuário: qual o horário de atendimento do Zezinho
Esperado: 
  - "Atendimento [nome]:\n[horario]"
  - Slot limpo após resposta

Usuário: quando a Eliane está na faculdade
Esperado: 
  - Horário de atendimento

Usuário: a professora Myriam atende hoje
Esperado: 
  - Horário de atendimento

Usuário: qual o horário da Myriam?
Esperado: 
  - Horário de atendimento

Usuário: horário de atendimento do alvaro
Esperado: 
  - Horário de atendimento

Usuário: quando encontro o alvaro?
Esperado: 
  - Horário de atendimento

Usuário: qual o horário do professor alvaro?
Esperado: 
  - Horário de atendimento

Usuário: horário alvaro
Esperado: 
  - Horário de atendimento
```

### 7.2 Testes com Formulário (Nome Não Fornecido)

**Testes:**
```
Usuário: atendimento da coordenação
Esperado: 
  - "Claro. De qual professor voce quer saber o horario?"
  - Bot aguarda resposta do usuário

Usuário: [responde] Alvaro
Esperado: 
  - Horário de atendimento do Alvaro
  - Formulário desativado
```

**Verificações:**
- ✅ Bot ativa formulário se nome não fornecido
- ✅ Bot pergunta nome do professor
- ✅ Bot aguarda resposta do usuário
- ✅ Bot busca horário após receber nome
- ✅ Slot é limpo após busca
- ✅ Pergunta foi salva com tópico "Docente"

**Cenários de Erro:**
```
# Docente não encontrado
Usuário: horário do Professor Teste
Esperado: "Professor(a) Professor Teste nao encontrado(a)."

# API offline
Usuário: horário do Alvaro
Esperado: "Erro ao buscar lista de docentes."
```

---

## 8. TESTES DE PERGUNTAS COM IA

**Action:** `action_gerar_resposta_com_ia`

**Objetivo:** Verificar se o bot gera respostas usando IA e retorna URLs de referência.

**Testes:**
```
Usuário: o que é diagrama de classes
Esperado: 
  - "Consultando Base de Dados..."
  - Resposta gerada pela IA
  - Seção "📎 **Documentos de referência:**" com URLs (se disponíveis)

Usuário: me explica COCOMO
Esperado: 
  - Resposta da IA sobre COCOMO
  - URLs de documentos relacionados

Usuário: o que significa UML
Esperado: 
  - Resposta da IA sobre UML
  - URLs de documentos relacionados

Usuário: definição de scrum
Esperado: 
  - Resposta da IA sobre Scrum
  - URLs de documentos relacionados

Usuário: o que é PaaS
Esperado: 
  - Resposta da IA sobre PaaS
  - URLs de documentos relacionados

Usuário: o que é Cloud Computing
Esperado: 
  - Resposta da IA sobre Cloud Computing
  - URLs de documentos relacionados

Usuário: o que é cocomo 81
Esperado: 
  - Resposta da IA sobre COCOMO 81
  - URLs de documentos relacionados
```

**Verificações:**
- ✅ Bot identifica intent `perguntar_conteudo_ia`
- ✅ Bot extrai entidade "topico_estudo"
- ✅ Bot envia pergunta para `/ia/gerar-resposta`
- ✅ Bot retorna resposta da IA
- ✅ Bot busca URLs de documentos relacionados
- ✅ Bot adiciona seção "Documentos de referência" com até 3 URLs
- ✅ Se não houver URLs, não adiciona seção
- ✅ Pergunta foi salva com tópico "Conteúdo" (se encontrado na base)
- ✅ Verificar no banco se pergunta foi salva corretamente

**Cenários de Erro:**
```
# IA não retorna resposta
Usuário: o que é teste
Esperado: "A IA processou mas nao retornou texto." ou "Erro ao conectar com a IA."

# API offline
Usuário: o que é UML
Esperado: "Erro ao conectar com a IA."
```

---

## 9. TESTES DE SOLICITAÇÃO DE MATERIAIS

**Action:** `action_buscar_material`  
**Form:** `form_buscar_material`

**Objetivo:** Verificar se o bot busca e retorna URLs de materiais usando formulário.

### 9.1 Testes com Disciplina no Primeiro Turno

**Testes:**
```
Usuário: disponibiliza os slides de Sistemas Distribuídos
Esperado: 
  - "Buscando materiais para Sistemas Distribuidos..."
  - Lista de URLs de documentos (até 5)
  - Formato: "Encontrei X documento(s) para [disciplina]:\n\n1. [url]\n2. [url]..."

Usuário: quero baixar o pdf da aula de Engenharia
Esperado: 
  - Lista de URLs

Usuário: tem material complementar de banco de dados
Esperado: 
  - Lista de URLs

Usuário: pode me enviar o material de cloud computing?
Esperado: 
  - Lista de URLs

Usuário: me manda o material de Cloud Computing
Esperado: 
  - Lista de URLs

Usuário: me mande material de Qualidade de Software
Esperado: 
  - Lista de URLs

Usuário: quero o material de Engenharia de Software
Esperado: 
  - Lista de URLs

Usuário: preciso dos slides da aula de Sistemas Distribuidos
Esperado: 
  - Lista de URLs

Usuário: tem pdf de Banco de Dados?
Esperado: 
  - Lista de URLs

Usuário: quero baixar material de Inteligência Artificial
Esperado: 
  - Lista de URLs
```

### 9.2 Testes com Formulário (Disciplina Não Fornecida)

**Testes:**
```
Usuário: onde baixo os arquivos da aula
Esperado: 
  - "Claro. De qual disciplina voce quer o material?"
  - Bot aguarda resposta do usuário

Usuário: [responde] Engenharia de Software
Esperado: 
  - "Buscando materiais para Engenharia de Software..."
  - Lista de URLs
  - Formulário desativado
```

### 9.3 Testes com Informar Disciplina Diretamente

**Testes:**
```
Usuário: Cloud Computing
Esperado: 
  - "Claro. De qual disciplina voce quer o material?"
  - Formulário ativado

Usuário: [confirma] Cloud Computing
Esperado: 
  - Lista de URLs de materiais
```

**Verificações:**
- ✅ Bot ativa formulário se disciplina não fornecida
- ✅ Bot pergunta disciplina
- ✅ Bot aguarda resposta do usuário
- ✅ Bot busca materiais usando `/ia/testar-baseconhecimento`
- ✅ Bot retorna até 5 URLs de documentos
- ✅ Se mais de 5, indica quantidade adicional
- ✅ Se não encontrar documentos, usa fallback para busca geral
- ✅ Slot é limpo após busca
- ✅ Pergunta foi salva com tópico "Disciplina"

**Cenários de Erro:**
```
# Disciplina não encontrada
Usuário: material de Disciplina Teste
Esperado: "Disciplina 'Disciplina Teste' nao encontrada..."

# Nenhum material encontrado
Usuário: material de Engenharia de Software
Esperado: "Nao encontrei materiais para Engenharia de Software no sistema." ou mensagem de fallback

# API offline
Usuário: slides de SD
Esperado: "Erro ao conectar ao sistema de documentos."
```

---

## 10. TESTES DE DÚVIDAS FREQUENTES

**Action:** `action_buscar_duvidas_frequentes`

**Objetivo:** Verificar se o bot retorna categorias de dúvidas frequentes.

**Testes:**
```
Usuário: quais são as dúvidas mais frequentes
Esperado: 
  - "📚 **Dúvidas Frequentes por Categoria:**\n\n"
  - Seção "🏛️ **Dúvidas Institucionais:**" com top 5
  - Seção "📖 **Dúvidas de Conteúdo (Tópicos mais perguntados):**" com top 5

Usuário: o que os alunos mais perguntam
Esperado: 
  - Lista de categorias

Usuário: dúvidas frequentes
Esperado: 
  - Lista de categorias

Usuário: categorias mais perguntadas
Esperado: 
  - Lista de categorias

Usuário: quais são os tópicos mais consultados
Esperado: 
  - Lista de categorias

Usuário: o que é mais perguntado
Esperado: 
  - Lista de categorias

Usuário: quais são as perguntas mais comuns
Esperado: 
  - Lista de categorias

Usuário: dúvidas mais frequentes dos alunos
Esperado: 
  - Lista de categorias
```

**Formato Esperado da Resposta:**
```
📚 **Dúvidas Frequentes por Categoria:**

🏛️ **Dúvidas Institucionais:**
  • TCC: 15 pergunta(s)
  • APS: 12 pergunta(s)
  • Estágio: 8 pergunta(s)
  • Docente: 6 pergunta(s)
  • Disciplina: 5 pergunta(s)

📖 **Dúvidas de Conteúdo (Tópicos mais perguntados):**
  • Algoritmos: 8 pergunta(s)
  • Banco: 6 pergunta(s)
  • Cloud: 5 pergunta(s)
  • Software: 4 pergunta(s)
  • Engenharia: 3 pergunta(s)
```

**Verificações:**
- ✅ Bot identifica intent `consultar_duvidas_frequentes`
- ✅ Bot busca todas as mensagens dos alunos
- ✅ Bot agrupa por tópicos institucionais
- ✅ Bot agrupa dúvidas de conteúdo por palavras-chave
- ✅ Bot retorna top 5 de cada categoria
- ✅ Se não houver dados, exibe mensagem apropriada
- ✅ Formato da resposta está correto

**Cenários de Erro:**
```
# Nenhuma dúvida registrada
Usuário: dúvidas frequentes
Esperado: "Ainda não há dúvidas frequentes registradas."

# API offline
Usuário: quais são as dúvidas mais frequentes
Esperado: "Erro ao buscar duvidas frequentes."
```

**Teste de Integração:**
1. Fazer várias perguntas diferentes (TCC, APS, perguntas de conteúdo)
2. Verificar se foram salvas no banco
3. Perguntar "dúvidas frequentes"
4. Verificar se categorias aparecem corretamente

---

## 11. TESTES DE FORMULÁRIOS

### 11.1 Formulário de Atendimento Docente

**Form:** `form_atendimento_docente`

**Testes:**
```
# Cenário 1: Ativação do formulário
Usuário: atendimento da coordenação
Bot: "Claro. De qual professor voce quer saber o horario?"
[Formulário ativado]

# Cenário 2: Preenchimento do formulário
Usuário: Alvaro
Bot: [Busca horário e retorna]
[Formulário desativado]

# Cenário 3: Interrupção com saudação
Usuário: atendimento da coordenação
Bot: "Claro. De qual professor voce quer saber o horario?"
Usuário: oi
Bot: [Ignora saudação, mantém formulário ativo]
Usuário: Alvaro
Bot: [Busca horário]
```

**Verificações:**
- ✅ Formulário é ativado quando nome não fornecido
- ✅ Formulário aguarda resposta do usuário
- ✅ Formulário ignora intents: agradecer, saudar, despedir
- ✅ Formulário é desativado após preenchimento
- ✅ Slot é limpo após busca

### 11.2 Formulário de Busca de Material

**Form:** `form_buscar_material`

**Testes:**
```
# Cenário 1: Ativação do formulário
Usuário: onde baixo os arquivos da aula
Bot: "Claro. De qual disciplina voce quer o material?"
[Formulário ativado]

# Cenário 2: Preenchimento do formulário
Usuário: Engenharia de Software
Bot: [Busca materiais e retorna URLs]
[Formulário desativado]

# Cenário 3: Informar disciplina diretamente
Usuário: Cloud Computing
Bot: "Claro. De qual disciplina voce quer o material?"
[Formulário ativado]
Usuário: Cloud Computing
Bot: [Busca materiais]
```

**Verificações:**
- ✅ Formulário é ativado quando disciplina não fornecida
- ✅ Formulário aguarda resposta do usuário
- ✅ Formulário ignora intents: agradecer, saudar, despedir
- ✅ Formulário é desativado após preenchimento
- ✅ Slot é limpo após busca

---

## 12. TESTES DE SALVAMENTO DE PERGUNTAS

**Objetivo:** Verificar se todas as perguntas são salvas corretamente no banco.

### 12.1 Testes de Salvamento Automático

**Testes:**
```
# Fazer perguntas e verificar no banco
1. Usuário: oi
   Verificar: GET /mensagens_aluno/get_lista_msg/
   Esperado: Pergunta salva com tópico ["Geral"]

2. Usuário: quando é a NP1 de Engenharia de Software
   Verificar: Última mensagem no banco
   Esperado: 
     - primeira_pergunta: "quando é a NP1 de Engenharia de Software"
     - topico: ["Disciplina"]
     - feedback: ""

3. Usuário: o que é TCC
   Verificar: Última mensagem no banco
   Esperado: 
     - topico: ["TCC"]

4. Usuário: o que é diagrama de classes
   Verificar: Última mensagem no banco
   Esperado: 
     - topico: ["Conteúdo"] (se encontrado na base de conhecimento)

5. Usuário: horário do Alvaro
   Verificar: Última mensagem no banco
   Esperado: 
     - topico: ["Docente"]
```

### 12.2 Testes de Classificação de Tópicos

**Testes:**
```
# Dúvidas Institucionais
Usuário: informações sobre TCC
Esperado: topico: ["TCC"]

Usuário: regras da APS
Esperado: topico: ["APS"]

Usuário: informações sobre estágio
Esperado: topico: ["Estágio"]

Usuário: horas complementares
Esperado: topico: ["Horas Complementares"]

Usuário: contato do professor
Esperado: topico: ["Docente"]

Usuário: tem algum aviso
Esperado: topico: ["Aviso"]

Usuário: horário de Engenharia de Software
Esperado: topico: ["Disciplina"]

# Dúvidas de Conteúdo
Usuário: o que é UML
Esperado: topico: ["Conteúdo"] (se encontrado na base)

# Geral
Usuário: oi
Esperado: topico: ["Geral"]
```

**Verificações:**
- ✅ Todas as perguntas são salvas
- ✅ Tópicos são extraídos corretamente
- ✅ Dúvidas institucionais são classificadas corretamente
- ✅ Dúvidas de conteúdo são identificadas (se encontradas na base)
- ✅ Campo `data_hora` é preenchido automaticamente
- ✅ Campo `feedback` está vazio inicialmente

**Comando para Verificar:**
```bash
# Usar Postman ou curl
GET http://127.0.0.1:8000/mensagens_aluno/get_lista_msg/
```

---

## 13. TESTES DE RETORNO DE URLs

**Objetivo:** Verificar se URLs de documentos são retornadas corretamente.

### 13.1 URLs na Resposta da IA

**Testes:**
```
Usuário: o que é diagrama de classes
Esperado: 
  - Resposta da IA
  - Seção "📎 **Documentos de referência:**"
  - Lista de até 3 URLs

Usuário: me explica COCOMO
Esperado: 
  - Resposta da IA
  - URLs de documentos relacionados a COCOMO
```

**Verificações:**
- ✅ URLs são buscadas usando `/ia/testar-baseconhecimento`
- ✅ Até 3 URLs são retornadas
- ✅ Seção é adicionada apenas se houver URLs
- ✅ URLs são válidas e acessíveis

### 13.2 URLs na Busca de Materiais

**Testes:**
```
Usuário: material de Engenharia de Software
Esperado: 
  - "Encontrei X documento(s) para Engenharia de Software:\n\n"
  - Lista de até 5 URLs numeradas
  - Se mais de 5, indica quantidade adicional
```

**Verificações:**
- ✅ URLs são buscadas usando `/ia/testar-baseconhecimento`
- ✅ Até 5 URLs são retornadas
- ✅ URLs são numeradas (1., 2., 3., ...)
- ✅ Se mais de 5, mostra "... e mais X documento(s)."
- ✅ URLs são válidas e acessíveis

**Cenários de Erro:**
```
# Nenhum documento encontrado
Usuário: material de Disciplina Sem Documentos
Esperado: Mensagem de fallback ou "Nao encontrei materiais..."

# API não retorna URLs
Usuário: material de Engenharia de Software
Esperado: Mensagem de fallback
```

---

## 14. TESTES DE INTEGRAÇÃO COM API

**Objetivo:** Verificar se todas as integrações com a API funcionam corretamente.

### 14.1 Endpoints Testados

**Testes:**
```
# 1. GET /aviso/get_lista_aviso/
Action: action_buscar_ultimos_avisos
Status: ✅ Deve retornar lista de avisos

# 2. GET /disciplinas/get_diciplina_nome/{nome}/cronograma
Função: get_disciplina_id_by_name
Status: ✅ Deve retornar cronogramas com ID da disciplina

# 3. GET /cronograma/disciplina/{id}
Action: action_buscar_cronograma
Status: ✅ Deve retornar horários da disciplina

# 4. GET /avaliacao/disciplina/{id}
Action: action_buscar_data_avaliacao
Status: ✅ Deve retornar avaliações da disciplina

# 5. GET /baseconhecimento/get_buscar?q={termo}
Action: action_buscar_info_atividade_academica
Status: ✅ Deve retornar {"contextos": [...]}

# 6. GET /professores/lista_professores/
Actions: action_buscar_info_docente, action_buscar_atendimento_docente
Status: ✅ Deve retornar lista de professores

# 7. GET /coordenador/get_list_coordenador/
Action: action_buscar_info_docente
Status: ✅ Deve retornar lista de coordenadores

# 8. POST /ia/gerar-resposta
Action: action_gerar_resposta_com_ia
Status: ✅ Deve retornar resposta da IA

# 9. GET /ia/testar-baseconhecimento?q={termo}
Actions: action_buscar_material, action_gerar_resposta_com_ia
Status: ✅ Deve retornar documentos com URLs

# 10. POST /mensagens_aluno/
Função: salvar_pergunta_aluno
Status: ✅ Deve salvar pergunta no banco

# 11. GET /mensagens_aluno/get_lista_msg/
Action: action_buscar_duvidas_frequentes
Status: ✅ Deve retornar lista de mensagens
```

### 14.2 Testes de Timeout

**Testes:**
```
# Simular API lenta ou offline
1. Desligar API
2. Fazer pergunta
3. Verificar se timeout é respeitado (10s ou 30s)
4. Verificar se mensagem de erro é exibida
```

**Verificações:**
- ✅ Timeout de 10s para requisições normais
- ✅ Timeout de 30s para requisições de IA
- ✅ Mensagens de erro são exibidas quando API está offline
- ✅ Bot não trava indefinidamente

---

## 15. TESTES DE CASOS EXTREMOS E ERROS

### 15.1 Testes de Entrada Inválida

**Testes:**
```
# Perguntas vazias ou sem sentido
Usuário: 
Esperado: "Desculpe, nao entendi. Pode perguntar de outra forma?"

Usuário: asdfghjkl
Esperado: "Desculpe, nao entendi. Pode perguntar de outra forma?"

Usuário: 123456
Esperado: "Desculpe, nao entendi. Pode perguntar de outra forma?"

# Perguntas muito longas
Usuário: [pergunta com mais de 500 caracteres]
Esperado: Bot processa normalmente ou exibe erro apropriado
```

### 15.2 Testes de Disciplinas Não Existentes

**Testes:**
```
Usuário: horário de Disciplina Inexistente 123
Esperado: "Nao encontrei a disciplina Disciplina Inexistente 123."

Usuário: quando é a NP1 de Disciplina Teste
Esperado: "Disciplina 'Disciplina Teste' nao encontrada..."

Usuário: material de Disciplina Aleatória
Esperado: "Disciplina 'Disciplina Aleatória' nao encontrada..."
```

### 15.3 Testes de Docentes Não Existentes

**Testes:**
```
Usuário: contato do Professor Inexistente
Esperado: "Nao encontrei o professor(a) Professor Inexistente no cadastro."

Usuário: horário do Professor Teste 123
Esperado: "Professor(a) Professor Teste 123 nao encontrado(a)."
```

### 15.4 Testes de API Offline

**Testes:**
```
# Desligar API e testar cada funcionalidade
1. Consultar avisos
   Esperado: "Erro ao conectar ao sistema de avisos."

2. Buscar cronograma
   Esperado: "Erro ao buscar cronograma."

3. Buscar avaliação
   Esperado: "Erro ao buscar avaliacoes."

4. Buscar informação de atividade
   Esperado: "Erro ao buscar informacoes do curso."

5. Buscar informação de docente
   Esperado: "Erro ao buscar lista de professores."

6. Buscar atendimento
   Esperado: "Erro ao buscar lista de docentes."

7. Buscar material
   Esperado: "Erro ao conectar ao sistema de documentos."

8. Gerar resposta com IA
   Esperado: "Erro ao conectar com a IA."

9. Buscar dúvidas frequentes
   Esperado: "Erro ao buscar duvidas frequentes."
```

### 15.5 Testes de Múltiplas Perguntas Sequenciais

**Testes:**
```
# Fazer várias perguntas em sequência
Usuário: oi
Bot: [responde]

Usuário: quando é a NP1 de ES
Bot: [responde]

Usuário: obrigado
Bot: [responde]

Usuário: material de SD
Bot: [responde]

Usuário: tchau
Bot: [responde]
```

**Verificações:**
- ✅ Bot mantém contexto entre perguntas
- ✅ Slots são limpos corretamente
- ✅ Formulários não ficam ativos após conclusão
- ✅ Todas as perguntas são salvas

### 15.6 Testes de Interrupção de Formulários

**Testes:**
```
# Interromper formulário com outras perguntas
Usuário: material de aula
Bot: "Claro. De qual disciplina voce quer o material?"
Usuário: oi
Bot: [ignora ou mantém formulário]
Usuário: Engenharia de Software
Bot: [busca material]
```

---

## 16. CHECKLIST DE TESTES

### ✅ Checklist Básico

- [ ] Saudação funciona
- [ ] Despedida funciona
- [ ] Agradecimento funciona
- [ ] Solicitar ajuda funciona
- [ ] Bot challenge funciona

### ✅ Checklist de Funcionalidades

- [ ] Consultar avisos funciona
- [ ] Buscar cronograma funciona
- [ ] Buscar data de avaliação funciona
- [ ] Buscar informações de TCC funciona
- [ ] Buscar informações de APS funciona
- [ ] Buscar informações de Estágio funciona
- [ ] Buscar informações de Horas Complementares funciona
- [ ] Buscar informações de docente funciona
- [ ] Buscar atendimento de docente funciona
- [ ] Perguntar conteúdo com IA funciona
- [ ] Buscar material funciona
- [ ] Consultar dúvidas frequentes funciona

### ✅ Checklist de Formulários

- [ ] Formulário de atendimento ativa corretamente
- [ ] Formulário de atendimento preenche corretamente
- [ ] Formulário de material ativa corretamente
- [ ] Formulário de material preenche corretamente
- [ ] Formulários ignoram intents corretos
- [ ] Formulários desativam após preenchimento

### ✅ Checklist de Integração

- [ ] Todas as perguntas são salvas
- [ ] Tópicos são extraídos corretamente
- [ ] URLs são retornadas na resposta da IA
- [ ] URLs são retornadas na busca de materiais
- [ ] Dúvidas frequentes agrupa corretamente
- [ ] Timeouts são respeitados

### ✅ Checklist de Erros

- [ ] Disciplinas não existentes tratadas
- [ ] Docentes não existentes tratados
- [ ] API offline tratada
- [ ] Entrada inválida tratada
- [ ] Múltiplas perguntas sequenciais funcionam
- [ ] Interrupção de formulários funciona

---

## 📊 COMANDOS ÚTEIS PARA TESTES

### Testar no Rasa Shell
```bash
rasa shell
```

### Verificar Mensagens Salvas
```bash
# Usar Postman ou curl
GET http://127.0.0.1:8000/mensagens_aluno/get_lista_msg/
```

### Verificar Logs
```bash
# Ver logs do Rasa
rasa shell --debug

# Ver logs da API
# Verificar console onde a API está rodando
```

### Testar Endpoints da API Diretamente
```bash
# Avisos
curl http://127.0.0.1:8000/aviso/get_lista_aviso/

# Cronograma
curl http://127.0.0.1:8000/disciplinas/get_diciplina_nome/Engenharia%20de%20Software/cronograma

# Professores
curl http://127.0.0.1:8000/professores/lista_professores/

# IA
curl -X POST http://127.0.0.1:8000/ia/gerar-resposta \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "o que é UML"}'
```

---

## 🎯 PRIORIZAÇÃO DE TESTES

### 🔴 Crítico (Testar Primeiro)
1. Salvamento de perguntas
2. Busca de disciplina por nome
3. Retorno de URLs
4. Formato de resposta da base de conhecimento

### 🟡 Importante (Testar Depois)
5. Todas as actions principais
6. Formulários
7. Dúvidas frequentes
8. Integração com API

### 🟢 Desejável (Testar Por Último)
9. Casos extremos
10. Tratamento de erros
11. Múltiplas perguntas sequenciais

---

**Documento criado em:** 2025-01-27  
**Baseado em:** Análise completa do projeto e todas as funcionalidades implementadas

