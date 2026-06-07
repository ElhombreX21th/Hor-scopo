# Snippets de integração de pagamentos

Este ficheiro contém exemplos práticos para integrar pagamentos no frontend usando os endpoints já presentes no backend.

Observação: para endpoints que exigem autenticação, envie o header `Authorization: Bearer <TOKEN>`.

---

## 1) PayPal (redirect flow usando o backend)

Fluxo: frontend pede ao backend para criar a ordem; o backend devolve links (incl. `approve`) — redireciona para aprovação; depois captura.

Exemplo simples (sem o SDK PayPal):

```javascript
async function startPayPal(plano, returnUrl, cancelUrl, accessToken) {
  const res = await fetch('/api/paypal/create-order', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`
    },
    body: JSON.stringify({ plano, return_url: returnUrl, cancel_url: cancelUrl })
  });

  const data = await res.json();
  // Procura link de approve
  const approve = data.links && data.links.find(l => l.rel === 'approve');
  if (approve) {
    window.location = approve.href; // leva o usuário ao PayPal para aprovar
  } else {
    console.error('Resposta PayPal:', data);
  }
}

// Depois que o usuário voltar (return_url), o teu frontend pode chamar:
async function capturePayPal(orderId, accessToken) {
  const res = await fetch('/api/paypal/capture/' + orderId, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${accessToken}` }
  });
  return await res.json();
}
```

Exemplo usando o PayPal JS SDK (buttons) com criação pelo backend:

```html
<script src="https://www.paypal.com/sdk/js?client-id=SEU_CLIENT_ID&currency=BRL"></script>
<div id="paypal-button-container"></div>
<script>
paypal.Buttons({
  createOrder: async function() {
    const res = await fetch('/api/paypal/create-order', {
      method: 'POST',
      headers: {'Content-Type':'application/json', 'Authorization': `Bearer ${accessToken}`},
      body: JSON.stringify({ plano: 'premium' })
    });
    const data = await res.json();
    return data.id; // o id da ordem criado pelo backend
  },
  onApprove: async function(data) {
    // data.orderID
    const capture = await fetch('/api/paypal/capture/' + data.orderID, { method: 'POST' });
    const result = await capture.json();
    console.log('Captura PayPal:', result);
  }
}).render('#paypal-button-container');
</script>
```

---

## 2) PIX via Mercado Pago (exibir QR Code retornado pelo backend)

Fluxo: frontend chama `/api/mercadopago/create-pix` com `plano` e token do usuário autenticado. O backend escolhe o preço oficial do plano e retorna `qr_code` e `qr_code_base64`.

Exemplo para obter e mostrar o QR code:

```javascript
async function startPix(plano, accessToken) {
  const res = await fetch('/api/mercadopago/create-pix', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`
    },
    body: JSON.stringify({ plano })
  });

  const data = await res.json();
  if (data.qr_code_base64) {
    // mostra imagem base64
    const img = document.createElement('img');
    img.src = 'data:image/png;base64,' + data.qr_code_base64;
    document.getElementById('pix-area').innerHTML = '';
    document.getElementById('pix-area').appendChild(img);
  } else if (data.qr_code) {
    // mostrar texto do QR ou usar uma biblioteca para criar imagem
    document.getElementById('pix-area').textContent = data.qr_code;
  } else {
    console.error('Resposta PIX:', data);
  }

  // Guardar o id da transação para futuras verificações
  // data.id
}
```

---

## Headers e notas de segurança
- Para endpoints que alteram estado, use `Authorization: Bearer <TOKEN>`.
- Sempre use HTTPS em produção.
- Valide respostas e trate erros (timeouts, 4xx/5xx).

Se quiser, posso:
- injetar esses snippets diretamente em `frontend/index.html`, adaptando o layout;
- gerar componentes React/Vue com esses fluxos;
- adicionar validações e tratamento de erros mais robusto.
