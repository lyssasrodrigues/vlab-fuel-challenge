# ⛽ VLAB - Fuel Monitoring (Full Stack Challenge)

...

## Como Rodar o Projeto 

**Pré-requisitos:** Docker e Docker Compose.

1.  **Construir e Iniciar os Contêineres (Backend, Frontend e DB):**
    ```bash
    docker-compose up --build -d
    ```

2.  **Verificar o Status:** Aguarde até que o serviço `db` esteja `healthy` e o `backend` esteja no ar.

3.  **Rodar o Script de Ingestão de Dados (Seed):**
    * Use o serviço `backend` para executar o script, garantindo que ele use a rede Docker interna para acessar o servidor:
        ```bash
        # Executa o script seed.py que fará chamadas para http://backend:8000
        docker-compose run --rm backend python seed.py --count 300
        ```
    
    * **Observação:** Se o seu `seed.py` estiver hardcoded para `localhost`, ajuste-o para `http://backend:8000` quando for rodado dentro do Docker Compose, ou execute o `seed.py` diretamente na sua máquina local após o `docker-compose up -d`.

4.  **Acessar a Aplicação:**
    * Frontend (Dashboard): `http://localhost:3000`
    * Backend (Docs): `http://localhost:8000/docs`

...
