<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sindicato FC - Laboratório F2P</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800&family=Roboto+Mono:wght@700&display=swap" rel="stylesheet">
    <style>
        :root {
            color-scheme: dark;
            --sf-bg: #13131F;
            --sf-surface: #1C1C2D;
            --sf-surface-raised: #222238;
            --sf-accent: #E94560;
            --sf-accent-hover: #D93652;
            --sf-success: #4ECCA3;
            --sf-error: #FF4D4D;
            --sf-text: #FFFFFF;
            --sf-muted: #A2A8D3;
            --sf-border: #2A2A40;
            --sf-radius-sm: 8px;
            --sf-radius-md: 12px;
            --sf-shadow-card: 0 12px 32px rgba(0, 0, 0, .22);
            --sf-font-body: "Inter", sans-serif;
            --sf-font-numeric: "Roboto Mono", monospace;
        }

        body { font-family: var(--sf-font-body); background: var(--sf-bg); color: var(--sf-text); margin: 0; padding: 40px 20px; display: flex; flex-direction: column; align-items: center; gap: 30px; }
        
        .header-main { text-align: center; margin-bottom: 20px; }
        .header-main h1 { font-size: 32px; font-weight: 800; margin: 0; text-transform: uppercase; letter-spacing: 1px; }
        .header-main span { color: var(--sf-accent); font-family: var(--sf-font-numeric); }

        .card { background: var(--sf-surface); padding: 32px 24px; border-radius: var(--sf-radius-md); box-shadow: var(--sf-shadow-card); width: 100%; max-width: 450px; border: 1px solid var(--sf-border); }
        .card-title { font-size: 18px; font-weight: 700; color: var(--sf-muted); margin-bottom: 20px; text-transform: uppercase; border-bottom: 1px solid var(--sf-border); padding-bottom: 10px; }

        .input-group { margin-bottom: 15px; }
        label { display: block; font-size: 11px; font-weight: 700; color: var(--sf-muted); margin-bottom: 6px; text-transform: uppercase; }
        input[type="number"] { width: 100%; background: var(--sf-bg); border: 1px solid var(--sf-border); color: var(--sf-text); font-family: var(--sf-font-numeric); font-size: 16px; padding: 12px; border-radius: var(--sf-radius-sm); box-sizing: border-box; outline: none; }
        input[type="number"]:focus { border-color: var(--sf-accent); }

        button { width: 100%; background: var(--sf-accent); color: var(--sf-text); font-weight: 700; font-size: 14px; padding: 14px; border: none; border-radius: var(--sf-radius-sm); cursor: pointer; text-transform: uppercase; margin-top: 10px; }
        button:hover { background: var(--sf-accent-hover); }

        .resultado-box { display: none; margin-top: 20px; padding: 15px; background: var(--sf-surface-raised); border-radius: var(--sf-radius-sm); text-align: center; border: 1px solid var(--sf-border); }
        .resultado-sucesso { border-color: rgba(78, 204, 163, 0.4); color: var(--sf-success); font-family: var(--sf-font-numeric); font-size: 20px; font-weight: bold;}
        .resultado-erro { border-color: rgba(255, 77, 77, 0.4); color: var(--sf-error); font-family: var(--sf-font-numeric); font-size: 16px; font-weight: bold;}
        
        .grid-container { display: flex; flex-wrap: wrap; justify-content: center; gap: 30px; width: 100%; max-width: 1000px; }
    </style>
</head>
<body>

    <div class="header-main">
        <h1>Sindicato <span>FC</span></h1>
        <p style="color: var(--sf-muted); font-size: 14px; font-weight: 500;">Laboratório de Engenharia F2P</p>
    </div>

    <div class="grid-container">
        
        <!-- MÓDULO 1: CALCULADORA DE MALETAS -->
        <div class="card">
            <div class="card-title">1. Explosão de GRL (Maletas)</div>
            <div class="input-group">
                <label>GRL Atual (%)</label>
                <input type="number" id="current_ovr" placeholder="Ex: 40">
            </div>
            <div class="input-group">
                <label>GRL Desejado (%)</label>
                <input type="number" id="target_ovr" placeholder="Ex: 180">
            </div>
            <button onclick="calcularMaletas()">Calcular Consumo</button>
            <div id="res-maletas" class="resultado-box"></div>
        </div>

        <!-- MÓDULO 2: AVALIADOR FAST TRAINER -->
        <div class="card">
            <div class="card-title">2. Teste Avatar (Fast Trainer)</div>
            <div class="input-group">
                <label>Idade do Jogador</label>
                <input type="number" id="idade_ft" value="18" disabled>
            </div>
            <div class="input-group">
                <label>Atributos Ganhos (6 treinos M. Difícil)</label>
                <input type="number" id="ganho_ft" placeholder="Ex: 45">
            </div>
            <button onclick="avaliarMutante()">Avaliar Mutante</button>
            <div id="res-ft" class="resultado-box"></div>
        </div>

        <!-- MÓDULO 3: REGRA DOS 180% -->
        <div class="card">
            <div class="card-title">3. Falha da Média (180%)</div>
            <div class="input-group">
                <label>Atributo Branco Chave (%)</label>
                <input type="number" id="attr_branco" placeholder="Ex: 175">
            </div>
            <div class="input-group">
                <label>Atributo Cinza Sacrificado (%)</label>
                <input type="number" id="attr_cinza" placeholder="Ex: 1">
            </div>
            <button onclick="calcularMedia()">Simular Exercício</button>
            <div id="res-media" class="resultado-box"></div>
        </div>

    </div>

    <script>
        // Lógica: Calculadora de Maletas (API Python)
        async function calcularMaletas() {
            const current = parseFloat(document.getElementById('current_ovr').value);
            const target = parseFloat(document.getElementById('target_ovr').value);
            const resBox = document.getElementById('res-maletas');

            if (isNaN(current) || isNaN(target)) return;

            try {
                const response = await fetch('/api/calcular', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ current_ovr: current, target_ovr: target })
                });
                const data = await response.json();
                
                resBox.style.display = "block";
                resBox.className = "resultado-box " + (data.erro ? "resultado-erro" : "resultado-sucesso");
                resBox.innerText = data.erro ? data.erro : `+${data.maletas} Maletas Estimadas`;
            } catch (error) {
                resBox.style.display = "block";
                resBox.className = "resultado-box resultado-erro";
                resBox.innerText = "Erro no servidor (Vercel Booting...)";
            }
        }

        // Lógica: Fast Trainer (Front-end)
        function avaliarMutante() {
            const ganho = parseInt(document.getElementById('ganho_ft').value);
            const resBox = document.getElementById('res-ft');
            if (isNaN(ganho)) return;

            resBox.style.display = "block";
            if (ganho >= 45) {
                resBox.className = "resultado-box resultado-sucesso";
                resBox.innerText = "MUTANTE APROVADO! (Pode Congelar)";
            } else {
                resBox.className = "resultado-box resultado-erro";
                resBox.innerText = "MEDIANO. Venda Imediata!";
            }
        }

        // Lógica: Regra da Média 180% (Front-end)
        function calcularMedia() {
            const branco = parseFloat(document.getElementById('attr_branco').value);
            const cinza = parseFloat(document.getElementById('attr_cinza').value);
            const resBox = document.getElementById('res-media');
            if (isNaN(branco) || isNaN(cinza)) return;

            const media = (branco + cinza) / 2;
            resBox.style.display = "block";
            
            if (media < 180) {
                resBox.className = "resultado-box resultado-sucesso";
                resBox.innerText = `Média: ${media}%\n(Treino Liberado!)`;
            } else {
                resBox.className = "resultado-box resultado-erro";
                resBox.innerText = `Média: ${media}%\n(Bloqueio de 180% Atingido)`;
            }
        }
    </script>
</body>
</html>