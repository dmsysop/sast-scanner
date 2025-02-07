# 📌 Documentação do SAST Scanner com Docker

Este documento descreve como **construir, utilizar e integrar** o SAST Scanner baseado em Docker para analisar projetos Python e PHP.

---

## 🚀 1. Construção da Imagem Docker

Antes de utilizar o scanner, é necessário criar a imagem Docker. Execute:

```sh
docker build -t sast-scanner .
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

Para escanear um projeto, basta executar:

```sh
docker run --rm -v $(pwd):/app/code sast-scanner
```

Isso fará a análise de segurança no projeto localizado em `/caminho/do/projeto`.

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
    - docker run --rm -v $(pwd):/app/code sast-scanner
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
   docker build -t sast-scanner .
   ```
4. **Teste localmente:**
   ```sh
   docker run --rm -v /caminho/do/projeto:/app/code sast-scanner
   ```
5. **Envie um Pull Request!**

---

## 📞 Suporte
Se encontrar problemas ou tiver sugestões, entre em contato pelo [GitLab Issues](https://gitlab.com/dmsysop/sast-scanner/issues).

🚀 **Happy Scanning!**

