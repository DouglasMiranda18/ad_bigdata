# Site de convite de casamento — Manuella & Douglas

Projeto base em Flask com:

- Login restrito por **nome + senha personalizada** por convidado.
- Página do convite com data/local.
- Lista de presentes com controle de disponibilidade (1 compra por item).
- Opção de reserva com pagamento via **Pix** ou **Cartão (integração futura)**.
- Paleta visual em **verde oliva e rosa**.

## Dados atuais do convite

- Noivos: Manuella e Douglas
- Data: 02/05/2026
- Igreja: Nossa Senhora do Bom Parto
- Hora: a definir

## Como rodar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app init-db
flask --app app run
```

Acesse: http://127.0.0.1:5000

## Convidados de exemplo

- Ana Paula / 1234
- Carlos Silva / 5678
- Fernanda Lima / 9999

## Próximos passos sugeridos

1. Mover senhas para hash (ex.: `werkzeug.security`).
2. Criar painel admin para cadastrar convidados e presentes.
3. Integrar gateway de pagamento para cartão (ex.: Mercado Pago, Stripe, Pagar.me).
4. Enviar comprovante/confirmar pagamento automaticamente.
