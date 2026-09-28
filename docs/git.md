
  
  
  

# 📘 Guia de Contribuição: Branches, Commits e Fluxo de Trabalho

  

Este guia define as convenções oficiais do projeto para padronização de branches, mensagens de commit e o fluxo de trabalho da equipe. O objetivo é manter o histórico limpo, facilitar revisões e prevenir erros antes do envio para o repositório remoto.

  

---

  

## 1. Setup Inicial do Desenvolvedor

  

Para que os ganchos de validação automática (**Lefthook** e **Commitlint**) funcionem na sua máquina local — via terminal ou pelo **GitHub Desktop** —, execute os passos a seguir:

  

### 1.1 Pré-requisitos

*  **Git** configurado localmente.

*  **Node.js** (versão LTS instalada).

*  **Usuários de Windows (PowerShell):** Caso receba erros de restrição ao executar scripts do npm, abra o PowerShell e execute uma única vez:

```powershell
Set-ExecutionPolicy  -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ````
  
  

### 1.2 Ativação das Travas

  

Ao clonar o projeto pela primeira vez (ou atualizar sua branch com os novos arquivos), execute na raiz do projeto:

  

  
  
  

```Bash
npm  install
```

  

> O script `prepare` configurado executará o `lefthook install` automaticamente, registrando os hooks locais na pasta `.git/hooks/`.

>

>

  

## 2. Política de Branches

  

Adotamos um fluxo baseado em **Gitflow simplificado**. Commits diretos na `main` ou na `develop` não são permitidos.

  

  

### 2.1 Branches Base (Fixas)

  

-  **`main`**: Código de produção, estável e testado.

-  **`develop`**: Branch de integração onde todas as tarefas concluídas são reunidas.

  

### 2.2 Branches de Trabalho (Temporárias)

  

Toda nova branch deve seguir a convenção:

  

  



  

```Plaintext
<tipo>/<descricao-curta>
```

  

- Use apenas letras minúsculas, números, hífens (`-`) e pontos (`.`).

- Branches fora desse formato serão **rejeitadas** durante o `git push`.

  
| Prefixo | Descrição | Exemplo |
|---|---|---|
| `feat/` ou `feature/` | Nova funcionalidade ou recurso | `feat/login-usuario` |
| `fix/` | Correção de bugs em ambiente de desenvolvimento | `fix/calculo-total` |
| `hotfix/` | Correção emergencial diretamente voltada para produção | `hotfix/corrige-sessao` |
| `docs/` | Criação ou atualização exclusiva de documentação | `docs/atualiza-readme` |
| `refactor/` | Reestruturação de código sem alterar regra de negócio | `refactor/simplifica-funcoes` |
| `chore/` | Mudanças em configurações, build, dependências ou ferramentas | `chore/atualiza-pacotes` |
| `test/` | Implementação ou manutenção de testes | `test/testes-unitarios` |
| `release/` | Preparação e fechamento de versão para publicação | `release/1.0.0` |

## 3. Padrão de Commits (Conventional Commits Simplificado)

  

Adotamos a convenção de commits descritivos, sem exigência de escopo entre parênteses.


  

### 3.1 Estrutura Obrigatória

  

```Plaintext
<tipo>: <descrição no modo imperativo>
```

  

- Sempre use letras minúsculas no `<tipo>`.

- Coloque dois pontos (`:`) seguidos de **espaço**.

- Descreva a ação no presente indicativo/imperativo (ex: _"adiciona"_, _"corrige"_, _"remove"_).

  

### 3.2 Tipos Permitidos

  

-  **`feat:`** Adiciona nova funcionalidade (ex: `feat: cria tela de cadastro de usuarios`).

-  **`fix:`** Corrige um bug ou comportamento incorreto (ex: `fix: corrige validacao de campos vazios`).

-  **`docs:`** Alterações em documentação ou comentários (ex: `docs: adiciona manual de instalacao`).

-  **`style:`** Formatação, espaçamentos ou ponto e vírgula sem mudança de lógica (ex: `style: ajusta identacao do layout`).

-  **`refactor:`** Refatoração de código que não altera comportamento (ex: `refactor: divide componente em modulos menores`).

-  **`perf:`** Melhorias focadas em desempenho (ex: `perf: reduz tempo de resposta das consultas`).

-  **`test:`** Criação ou refatoração de testes (ex: `test: adiciona testes para validacao de cpf`).

-  **`build:`** Mudanças em scripts de build ou dependências externas (ex: `build: atualiza versao do pacote lefthook`).

-  **`ci:`** Alterações em arquivos de integração contínua (ex: `ci: configura pipeline de testes`).

-  **`chore:`** Tarefas gerais de manutenção e tarefas acessórias (ex: `chore: adiciona arquivo .gitignore`).

  

## 4. Fluxo de Trabalho Passo a Passo

  

### Passo 1: Partir da `develop` atualizada

  



  

```Bash
git checkout develop

git pull origin develop
```

  

### Passo 2: Criar a branch de trabalho

  



  

```Bash
git checkout -b feat/painel-principal
```

  

### Passo 3: Realizar alterações e commitar

  



  

```Bash
git add .

git commit -m "feat: cria estrutura basica do painel principal"
```

  

_(Se a mensagem não contiver o prefixo obrigatório, o commit será cancelado localmente)._

  

  

### Passo 4: Enviar alterações ao GitHub

  
  

```Bash
git push -u origin feat/painel-principal
```

  

_(Se o nome da branch estiver fora da convenção, o envio será bloqueado antes de sair da máquina)._

  

  

### Passo 5: Abrir Pull Request (PR)

  

1. Acesse o repositório no GitHub.

2. Abra um Pull Request com destino para a branch **`develop`**.

3. Solicite a revisão de código de um colega antes do merge.

  

## 5. Resolução Rápida de Erros Frequentes

  

-  **Commit rejeitado com `[type-empty]` ou `[subject-empty]`:**

- O commit não seguiu o formato `<tipo>: <descrição>`.

-  _Solução:_ Reescreva a mensagem iniciando com um tipo válido (ex: `feat: minha alteracao`).

-  **Push bloqueado com `❌ [ERRO] Nome de branch fora do padrão`:**

- A branch foi criada com nome genérico (ex: `teste`, `tela-nova`).

-  _Solução:_ Crie uma nova branch com nome padronizado (`git checkout -b feat/tela-nova`) e refaça o push.

-  **Erro de módulo não encontrado (`MODULE_NOT_FOUND`) no push:**

- Falta o arquivo `scripts/check-branch.js` localmente.

-  _Solução:_ Execute `git pull` na branch principal para puxar o script e confira se ele não está no `.gitignore`.