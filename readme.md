# 📌 Documentação do SAST Scanner com Docker

Este documento descreve como **construir, utilizar e integrar** o SAST Scanner baseado em Docker para analisar projetos Python, PHP e JavaScript.

---

## 🚀 1. Construção da Imagem Docker

Antes de utilizar o scanner, é necessário criar a imagem Docker. Execute:

```sh
./build.sh
```

Isso criará a imagem **sast-scanner** com todas as ferramentas necessárias.

---

## 📦 2. Publicação no Docker Hub ou Registry Privado

Para permitir que a imagem seja utilizada de qualquer lugar, publique-a em um repositório acessível.

**Exemplo: Publicando no Docker Hub**
```sh
docker tag sast-scanner username/sast-scanner:latest
docker push username/sast-scanner:latest
```

**Exemplo: Publicando no GitLab Container Registry**
```sh
docker login registry.gitlab.com
docker tag sast-scanner registry.gitlab.com/namespace/sast-scanner:latest
docker push registry.gitlab.com/namespace/sast-scanner:latest
```

---

## 🛠 3. Como Executar a Varredura

Para escanear um projeto, basta executar na pasta onde estão seus projetos:

```sh
docker run --rm -v "$(pwd)/projeto:/app/projeto" sast-scanner scan projeto
```

Isso fará a análise de segurança no projeto localizado em `/caminho/do/projeto`.

ATENÇÃO: Os 3 parametros "projeto" devem ser iguais!

Alternativamente, você pode usar:

```sh
./scanner.sh projeto
```

Lembrando novamente que este script deve ficar FORA da pasta do projeto!
---

## 🔄 4. Integração com GitLab CI/CD

Crie um arquivo `.gitlab-ci.yml` no repositório e adicione:

```yaml
stages:
  - sast

sast:
  stage: sast
  image: sast-scanner:latest
  script:
    - docker run --rm -v $(pwd):/app/seu_projeto sast-scanner scan seu_projeto
  artifacts:
    paths:
      - cache.json
    expire_in: 1 week
```

Isso garantirá que o scanner seja executado automaticamente antes da publicação em produção.

---

## 🔧 5. Como Contribuir e Melhorar o Scanner

1. **Clone o repositório:**
   ```sh
   git clone https://gitlab.com/dmsysop/sast-scanner.git
   ```
2. **Faça as alterações desejadas** no código.
3. **Reconstrua a imagem:**
   ```sh
   ./build.sh
   ```
4. **Teste localmente:**
   ```sh
   docker run --rm -v /caminho/do/projeto:/app/projeto sast-scanner scan projeto
   ```
5. **Envie um Pull Request!**

---

## 📞 Suporte
Se encontrar problemas ou tiver sugestões, entre em contato pelo [GitLab Issues](https://gitlab.com/dmsysop/sast-scanner/issues).

🚀 **Happy Scanning!**